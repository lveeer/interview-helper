from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.core.database import get_db
from app.models.user import User
from app.models.resume import Resume
from app.models.interview import Interview
from app.models.knowledge import KnowledgeDocument
from app.schemas.statistics import DashboardStatistics, RecentInterview
from app.api.auth import get_current_user

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户统计数据

    返回数据包括：
    - resume_count: 简历数量
    - interview_count: 面试次数
    - knowledge_count: 知识文档数量
    - avg_score: 平均分数（四舍五入取整）
    - recent_interviews: 最近面试记录（最多 5 条）
    """
    from app.schemas.common import ApiResponse

    # 统计简历数量
    resume_count = db.query(func.count(Resume.id)).filter(
        Resume.user_id == current_user.id
    ).scalar() or 0

    # 统计面试数量
    interview_count = db.query(func.count(Interview.id)).filter(
        Interview.user_id == current_user.id
    ).scalar() or 0

    # 统计知识文档数量
    knowledge_count = db.query(func.count(KnowledgeDocument.id)).filter(
        KnowledgeDocument.user_id == current_user.id
    ).scalar() or 0

    # 计算平均分数（四舍五入取整）
    avg_score_result = db.query(func.round(func.avg(Interview.total_score))).filter(
        Interview.user_id == current_user.id
    ).scalar()
    avg_score = int(avg_score_result) if avg_score_result is not None else 0

    # 获取最近 5 条面试记录
    recent_interviews = db.query(Interview).filter(
        Interview.user_id == current_user.id
    ).order_by(Interview.created_at.desc()).limit(5).all()

    # 构建最近面试记录列表
    recent_interviews_data = [
        RecentInterview(
            id=interview.id,
            job_description=interview.job_description,
            total_score=interview.total_score,
            status=interview.status.value,
            created_at=interview.created_at
        )
        for interview in recent_interviews
    ]

    # 构建统计数据
    statistics = DashboardStatistics(
        resume_count=resume_count,
        interview_count=interview_count,
        knowledge_count=knowledge_count,
        avg_score=avg_score,
        recent_interviews=recent_interviews_data
    )

    return ApiResponse(
        code=200,
        message="success",
        data=statistics
    )