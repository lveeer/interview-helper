from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime


class RecentInterview(BaseModel):
    """最近面试记录"""
    id: int
    job_description: Optional[str] = None
    total_score: int
    status: str
    created_at: datetime


class DashboardStatistics(BaseModel):
    """用户统计数据"""
    resume_count: int
    interview_count: int
    knowledge_count: int
    avg_score: int
    recent_interviews: List[RecentInterview]