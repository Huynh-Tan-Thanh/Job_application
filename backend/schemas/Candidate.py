from typing import List, Optional
from pydantic import BaseModel

class CandidateBase(BaseModel):
    name: str
    skills: List[str] = []
    cv_text: Optional[str] = None

class CandidateCreate(CandidateBase):
    pass

class CandidateUpdate(BaseModel):
    name: Optional[str] = None
    skills: Optional[List[str]] = None
    cv_text: Optional[str] = None

class CandidateResponse(CandidateBase):
    id: int

    class Config:
        from_attributes = True  # Pydantic v2
