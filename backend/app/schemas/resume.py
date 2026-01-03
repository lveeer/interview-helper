from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class ResumeUpload(BaseModel):
    file_name: str


class ResumeParse(BaseModel):
    personal_info: Dict[str, Any]
    education: List[Dict[str, Any]]
    experience: List[Dict[str, Any]]
    skills: List[str]
    projects: List[Dict[str, Any]]
    highlights: List[str]


class ResumeResponse(BaseModel):
    id: int
    user_id: int
    file_name: str
    file_type: str
    personal_info: Optional[Dict[str, Any]] = None
    education: Optional[List[Dict[str, Any]]] = None
    experience: Optional[List[Dict[str, Any]]] = None
    skills: Optional[List[str]] = None
    projects: Optional[List[Dict[str, Any]]] = None
    highlights: Optional[List[str]] = None
    created_at: datetime

    class Config:
        from_attributes = True