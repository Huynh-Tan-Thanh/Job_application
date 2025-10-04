from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class MatchResult(BaseModel):
    job_id: int
    title: str
    company: str
    location: Optional[str]
    score: float
    skill_score: float
    keyword_hits: int
    coverage: float
    semantic_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    candidate_extra_skills: List[str]


class CandidateMatchResponse(BaseModel):
    candidate_id: int
    candidate_name: str
    candidate_skills: List[str]
    results: List[MatchResult]

    model_config = ConfigDict(from_attributes=True)


class SkillGapItem(BaseModel):
    skill: str
    demand_count: int
    demand_ratio: float
    job_ids: List[int]
    job_titles: List[str]
    recommended_resources: List[str]


class CandidateSkillGapResponse(BaseModel):
    candidate_id: int
    candidate_name: str
    candidate_skills: List[str]
    considered_jobs: int
    gaps: List[SkillGapItem]

    model_config = ConfigDict(from_attributes=True)
