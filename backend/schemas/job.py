from typing import List
from pydantic import BaseModel

class JobBase(BaseModel):
    title: str
    company: str
    description: str
    location: str
    skills: List[str]

class JobCreate(JobBase):
    pass

class JobUpdate(JobBase):
    pass

class JobResponse(JobBase):
    id: int
    class Config:
        from_attributes = True
