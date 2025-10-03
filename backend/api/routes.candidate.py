from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from models.database import SessionLocal
from models.candidate import Candidate
from schemas.candidate import CandidateResponse
from services.cv_parser import parse_pdf, parse_docx, extract_skills
import tempfile, shutil, os
from typing import List

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Lấy tất cả candidates
@router.get("/candidates", response_model=List[CandidateResponse])
def get_candidates(db: Session = Depends(get_db)):
    return db.query(Candidate).all()

# Upload CV
@router.post("/candidates/upload", response_model=CandidateResponse)
def upload_cv(name: str = Form(...), file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Lưu file tạm
    with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    # Parse CV
    if file.filename.endswith(".pdf"):
        cv_text = parse_pdf(tmp_path)
    elif file.filename.endswith(".docx"):
        cv_text = parse_docx(tmp_path)
    else:
        os.remove(tmp_path)
        raise HTTPException(status_code=400, detail="Unsupported file type")

    os.remove(tmp_path)  # cleanup

    # Extract kỹ năng (simple demo)
    skills = extract_skills(cv_text)

    # Lưu DB
    candidate = Candidate(name=name, cv_text=cv_text, skills=str(skills))
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return candidate
