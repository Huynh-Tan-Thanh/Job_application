from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..models.database import get_db
from ..schemas.match import CandidateMatchResponse, CandidateSkillGapResponse
from ..services.matcher import candidate_skill_snapshot, match_for_candidate
from ..services.skill_gap import summarise_skill_gaps

router = APIRouter(prefix="/match", tags=["match"])


@router.get("/candidate/{candidate_id}", response_model=CandidateMatchResponse)
def match_candidate(
    candidate_id: int,
    top_k: int = Query(20, ge=1, le=100),
    min_score: float = Query(0.0, ge=0.0, le=1.0),
    db: Session = Depends(get_db),
):
    candidate, rows = match_for_candidate(db, candidate_id, top_k=top_k, min_score=min_score)
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")

    return CandidateMatchResponse(
        candidate_id=candidate.id,
        candidate_name=candidate.name,
        candidate_skills=candidate_skill_snapshot(candidate),
        results=rows,
    )


@router.get("/candidate/{candidate_id}/skill-gap", response_model=CandidateSkillGapResponse)
def candidate_skill_gap(
    candidate_id: int,
    top_k: int = Query(20, ge=1, le=100),
    min_score: float = Query(0.0, ge=0.0, le=1.0),
    gap_limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    candidate, rows = match_for_candidate(db, candidate_id, top_k=top_k, min_score=min_score)
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")

    gaps = summarise_skill_gaps(rows, limit=gap_limit)

    return CandidateSkillGapResponse(
        candidate_id=candidate.id,
        candidate_name=candidate.name,
        candidate_skills=candidate_skill_snapshot(candidate),
        considered_jobs=len(rows),
        gaps=gaps,
    )
