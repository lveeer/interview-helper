from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime


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


# ===== 岗位管理 Schema =====

class JobCreate(BaseModel):
    """创建岗位请求"""
    title: str
    company: Optional[str] = None
    job_description: str


class JobUpdate(BaseModel):
    """更新岗位请求"""
    title: Optional[str] = None
    company: Optional[str] = None
    job_description: Optional[str] = None


class JobResponse(BaseModel):
    """岗位响应"""
    id: int
    user_id: int
    title: str
    company: Optional[str] = None
    job_description: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class JobBriefResponse(BaseModel):
    """岗位简要响应（列表用）"""
    id: int
    title: str
    company: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True