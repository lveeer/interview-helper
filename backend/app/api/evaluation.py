from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.interview import Interview
from app.schemas.evaluation import InterviewReport
from app.api.auth import get_current_user
import json

router = APIRouter()


@router.get("/report/{interview_id}")
async def get_interview_report(
    interview_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取面试评估报告"""
    from app.schemas.common import ApiResponse

    interview = db.query(Interview).filter(
        Interview.id == interview_id,
        Interview.user_id == current_user.id
    ).first()
    if not interview:
        raise HTTPException(
            status_code=404,
            detail="面试不存在"
        )

    if interview.status != "completed":
        raise HTTPException(
            status_code=400,
            detail="面试尚未完成"
        )

    # 获取对话记录
    conversation = json.loads(interview.conversation) if interview.conversation else []

    # 调用评估报告生成服务
    from app.services.evaluation_service import EvaluationService
    report_data = await EvaluationService.generate_interview_report(
        {
            "id": interview.id,
            "job_description": interview.job_description
        },
        conversation
    )

    return ApiResponse(
        code=200,
        message="获取成功",
        data=InterviewReport(
            interview_id=interview_id,
            **report_data,
            created_at=interview.created_at
        )
    )