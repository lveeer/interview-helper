from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.interview import InterviewStatus


class InterviewCreate(BaseModel):
    resume_id: int
    job_description: str


class InterviewQuestion(BaseModel):
    question: str
    category: str
    difficulty: str


class InterviewMessage(BaseModel):
    role: str  # "interviewer" or "candidate"
    content: str
    timestamp: datetime


class InterviewResponse(BaseModel):
    id: int
    user_id: int
    resume_id: int
    job_description: str
    status: InterviewStatus
    total_score: int
    questions: Optional[List[Dict[str, Any]]] = None
    conversation: Optional[List[Dict[str, Any]]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class InterviewAnswer(BaseModel):
    answer: str
    answer_type: str = "text"  # "text" or "voice"


class InterviewRecordMessage(BaseModel):
    role: str  # "interviewer" or "candidate"
    content: str
    question_id: Optional[str] = None
    category: Optional[str] = None
    difficulty: Optional[str] = None
    type: Optional[str] = None  # "followup" 或 None
    reason: Optional[str] = None  # 追问原因
    timestamp: Optional[str] = None


class InterviewRecordResponse(BaseModel):
    id: int
    user_id: int
    resume_id: int
    job_description: str
    status: InterviewStatus
    total_score: int
    questions: List[Dict[str, Any]]
    conversation: List[InterviewRecordMessage]
    created_at: datetime