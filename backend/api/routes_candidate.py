from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from ..models.database import get_db
from ..models.candidate import Candidate
from ..schemas.Candidate import CandidateCreate, CandidateUpdate, CandidateResponse
from ..services.cv_parser import parse_cv
from typing import List

router = APIRouter(prefix="/candidates", tags=["candidates"])

@router.post("", response_model=CandidateResponse)
def create_candidate(payload: CandidateCreate, db: Session = Depends(get_db)):
    c = Candidate(name=payload.name, skills=payload.skills, cv_text=payload.cv_text)
    db.add(c); db.commit(); db.refresh(c)
    return c

@router.get("", response_model=List[CandidateResponse])
def list_candidates(db: Session = Depends(get_db)):
    return db.query(Candidate).order_by(Candidate.id.desc()).all()

@router.get("/{candidate_id}", response_model=CandidateResponse)
def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    c = db.get(Candidate, candidate_id)
    if not c:
        raise HTTPException(404, "Candidate not found")
    return c

@router.delete("/{candidate_id}")
def delete_candidate(candidate_id: int, db: Session = Depends(get_db)):
    c = db.get(Candidate, candidate_id)
    if not c:
        raise HTTPException(404, "Candidate not found")
    db.delete(c); db.commit()
    return {"ok": True}

@router.put("/{candidate_id}", response_model=CandidateResponse)
def update_candidate(candidate_id: int, payload: CandidateUpdate, db: Session = Depends(get_db)):
    c = db.get(Candidate, candidate_id)
    if not c:
        raise HTTPException(404, "Candidate not found")
    if payload.name is not None: c.name = payload.name
    if payload.skills is not None: c.skills = payload.skills
    if payload.cv_text is not None: c.cv_text = payload.cv_text
    db.commit(); db.refresh(c)
    return c

@router.post("/upload", response_model=CandidateResponse)
async def upload_cv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        name_guess, cv_text, skills = await parse_cv(file)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    c = Candidate(name=name_guess or "Unknown", cv_text=cv_text, skills=skills)
    db.add(c); db.commit(); db.refresh(c)
    return c
