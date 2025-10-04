from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict


class JobBase(BaseModel):
    title: str
    company: str
    description: str
    location: str
    skills: List[str] = Field(default_factory=list)


class JobCreate(JobBase):
    title: str = Field(..., min_length=1, description="Job title must not be empty.")


class JobUpdate(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    skills: Optional[List[str]] = None


class JobResponse(JobBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
