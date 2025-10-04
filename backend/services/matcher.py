from __future__ import annotations

from ast import literal_eval
from collections.abc import Iterable
from typing import Any, Dict, List, Tuple

from sqlalchemy.orm import Session

from ..models.candidate import Candidate
from ..models.job import Job
from .embedding import get_embedding_service


def _ensure_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return []
        if text.startswith("[") and text.endswith("]"):
            try:
                parsed = literal_eval(text)
            except (ValueError, SyntaxError):
                parsed = [part.strip(" \"'") for part in text[1:-1].split(",")]
        else:
            parsed = [text]
    elif isinstance(value, Iterable):
        parsed = list(value)
    else:
        parsed = [value]

    items: List[str] = []
    for item in parsed:
        if item is None:
            continue
        label = str(item).strip()
        if label:
            items.append(label)
    return items


def _normalise_skills(raw: Any) -> Tuple[set[str], Dict[str, str]]:
    skills = _ensure_list(raw)
    normalised: set[str] = set()
    display: Dict[str, str] = {}
    for skill in skills:
        lowered = skill.lower()
        normalised.add(lowered)
        display.setdefault(lowered, skill)
    return normalised, display


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    intersection = len(a & b)
    union = len(a | b)
    if union == 0:
        return 0.0
    return intersection / union


def _compose_candidate_text(candidate: Candidate) -> str:
    parts: List[str] = []
    if candidate.cv_text:
        parts.append(candidate.cv_text)
    parts.extend(_ensure_list(candidate.skills))
    parts.append(candidate.name)
    return " ".join(part for part in parts if part)


def _compose_job_text(job: Job) -> str:
    parts: List[str] = [job.title, job.company, job.description, job.location]
    parts.extend(_ensure_list(job.skills))
    return " ".join(part for part in parts if part)


def score_candidate_to_job(candidate: Candidate, job: Job) -> Dict[str, Any]:
    cand_norm, cand_display = _normalise_skills(candidate.skills)
    job_norm, job_display = _normalise_skills(job.skills)

    skill_score = _jaccard(cand_norm, job_norm)

    keyword_hits = 0
    if candidate.cv_text:
        text = candidate.cv_text.lower()
        keyword_hits = sum(1 for skill in job_norm if skill in text)

    bonus = min(0.25, keyword_hits * 0.03)

    semantic_score = 0.0
    candidate_text = _compose_candidate_text(candidate)
    job_text = _compose_job_text(job)
    if candidate_text and job_text:
        try:
            embedder = get_embedding_service()
            semantic_score = embedder.similarity(candidate_text, job_text)
        except Exception:  # pragma: no cover - best effort fallback
            semantic_score = 0.0

    base_score = min(1.0, skill_score + bonus)
    score = round(min(1.0, base_score + 0.2 * semantic_score), 4)

    matched = sorted(job_display[s] for s in job_norm & cand_norm)
    missing = sorted(job_display[s] for s in job_norm - cand_norm)
    extras = sorted(cand_display[s] for s in cand_norm - job_norm)

    coverage = round(len(matched) / len(job_norm), 4) if job_norm else 0.0

    return {
        "job_id": job.id,
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "score": score,
        "skill_score": round(skill_score, 4),
        "keyword_hits": keyword_hits,
        "coverage": coverage,
        "semantic_score": round(semantic_score, 4),
        "matched_skills": matched,
        "missing_skills": missing,
        "candidate_extra_skills": extras,
    }


def candidate_skill_snapshot(candidate: Candidate) -> list[str]:
    _, display = _normalise_skills(candidate.skills)
    return sorted(display.values(), key=str.lower)


def match_for_candidate(db: Session, candidate_id: int, top_k: int = 20, min_score: float = 0.0) -> Tuple[Candidate | None, List[Dict[str, Any]]]:
    candidate = db.get(Candidate, candidate_id)
    if not candidate:
        return None, []

    jobs = db.query(Job).all()
    results = [score_candidate_to_job(candidate, job) for job in jobs]
    results = [row for row in results if row["score"] >= min_score]
    results.sort(key=lambda row: row["score"], reverse=True)
    return candidate, results[:top_k]
