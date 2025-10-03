from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import SessionLocal
from models.job import Job
from schemas.job import JobCreate, JobUpdate, JobResponse
from typing import List

router = APIRouter()

# Dependency để lấy DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Lấy tất cả jobs
@router.get("/jobs", response_model=List[JobResponse])
def get_jobs(db: Session = Depends(get_db)):
    return db.query(Job).all()

# Lấy chi tiết job theo ID
@router.get("/jobs/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

# Thêm job mới
@router.post("/jobs", response_model=JobResponse)
def create_job(job: JobCreate, db: Session = Depends(get_db)):
    new_job = Job(**job.dict())
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return new_job

# Update job
@router.put("/jobs/{job_id}", response_model=JobResponse)
def update_job(job_id: int, job_update: JobUpdate, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    for key, value in job_update.dict().items():
        setattr(job, key, value)
    db.commit()
    db.refresh(job)
    return job

# Xóa job
@router.delete("/jobs/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    db.delete(job)
    db.commit()
    return {"message": f"Job {job_id} deleted successfully"}
