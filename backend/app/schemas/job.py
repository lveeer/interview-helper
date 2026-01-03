from pydantic import BaseModel
from typing import List, Dict, Any


class JobMatchRequest(BaseModel):
    resume_id: int
    job_description: str


class JobMatchResponse(BaseModel):
    match_score: int
    keyword_match: int
    skill_match: int
    project_relevance: int
    suggestions: List[str]
    missing_skills: List[str]
    strengths: List[str]