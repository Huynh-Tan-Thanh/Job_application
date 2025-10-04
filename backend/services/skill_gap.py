from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Dict, Iterable, List, Sequence, TypeVar

GAP_RESOURCES = {
    "python": [
        "https://docs.python.org/3/tutorial/",
        "https://realpython.com/",
    ],
    "fastapi": [
        "https://fastapi.tiangolo.com/tutorial/",
        "https://testdriven.io/blog/fastapi-tutorial/",
    ],
    "sql": [
        "https://mode.com/sql-tutorial/",
        "https://www.khanacademy.org/computing/computer-programming/sql",
    ],
    "postgresql": [
        "https://www.postgresql.org/docs/current/tutorial.html",
        "https://www.practicalsql.com/",
    ],
    "javascript": [
        "https://javascript.info/",
        "https://developer.mozilla.org/docs/Web/JavaScript",
    ],
    "typescript": [
        "https://www.typescriptlang.org/docs/handbook/intro.html",
        "https://www.totaltypescript.com/",
    ],
    "react": [
        "https://react.dev/learn",
        "https://ui.dev/react/",
    ],
    "docker": [
        "https://docs.docker.com/get-started/",
        "https://www.katacoda.com/courses/docker",
    ],
    "kubernetes": [
        "https://kubernetes.io/docs/home/",
        "https://www.cncf.io/online-programs/kubernetes/",
    ],
    "aws": [
        "https://aws.amazon.com/getting-started/hands-on/",
        "https://www.aws.training/",
    ],
    "gcp": [
        "https://cloud.google.com/training",
        "https://cloud.google.com/free-training",
    ],
    "azure": [
        "https://learn.microsoft.com/training/azure/",
        "https://aka.ms/AzureTraining",
    ],
}

DEFAULT_RESOURCES = [
    "https://roadmap.sh/",
    "https://www.coursera.org/",
]

T = TypeVar("T")


def _normalise_label(label: str) -> str:
    return label.strip().lower()


def _unique(sequence: Sequence[T]) -> List[T]:
    seen: set[T] = set()
    ordered: List[T] = []
    for item in sequence:
        if item in seen:
            continue
        seen.add(item)
        ordered.append(item)
    return ordered


def summarise_skill_gaps(
    matches: Iterable[Dict[str, Any]],
    limit: int = 10,
) -> List[Dict[str, Any]]:
    """Aggregate missing skills across candidate matches."""

    rows = list(matches)
    if not rows:
        return []

    counter: Counter[str] = Counter()
    display: Dict[str, str] = {}
    job_ids: Dict[str, List[int]] = defaultdict(list)
    job_titles: Dict[str, List[str]] = defaultdict(list)

    for row in rows:
        missing_skills = row.get("missing_skills", [])
        j_id = row.get("job_id")
        j_title = row.get("title")
        seen_in_job: set[str] = set()
        for raw_skill in missing_skills:
            if not raw_skill:
                continue
            key = _normalise_label(raw_skill)
            if key in seen_in_job:
                continue
            seen_in_job.add(key)
            counter[key] += 1
            display.setdefault(key, raw_skill)
            if isinstance(j_id, int):
                job_ids[key].append(j_id)
            if isinstance(j_title, str):
                job_titles[key].append(j_title)

    total_jobs = max(len(rows), 1)

    summary: List[Dict[str, Any]] = []
    for skill_key, count in counter.most_common():
        label = display.get(skill_key, skill_key)
        resources = GAP_RESOURCES.get(skill_key, DEFAULT_RESOURCES)
        summary.append(
            {
                "skill": label,
                "demand_count": count,
                "demand_ratio": round(count / total_jobs, 4),
                "job_ids": _unique(job_ids.get(skill_key, [])),
                "job_titles": _unique(job_titles.get(skill_key, [])),
                "recommended_resources": resources,
            }
        )

    return summary[:limit]
