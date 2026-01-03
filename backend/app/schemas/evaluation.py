from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime


class EvaluationScore(BaseModel):
    question_id: int
    question: str
    score: int
    feedback: str
    strengths: List[str]
    improvements: List[str]


class InterviewReport(BaseModel):
    interview_id: int
    total_score: int
    overall_feedback: str
    question_evaluations: List[EvaluationScore]
    recommended_resources: List[Dict[str, Any]]
    created_at: datetime