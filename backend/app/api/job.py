from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.resume import Resume
from app.schemas.job import JobMatchRequest, JobMatchResponse
from app.api.auth import get_current_user
import json

router = APIRouter()


@router.post("/match")
async def match_job(
    request: JobMatchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """计算简历与岗位的匹配度"""
    # 获取简历
    resume = db.query(Resume).filter(
        Resume.id == request.resume_id,
        Resume.user_id == current_user.id
    ).first()
    if not resume:
        raise HTTPException(
            status_code=404,
            detail="简历不存在"
        )

    # 构建简历数据
    resume_data = {
        "personal_info": json.loads(resume.personal_info) if resume.personal_info else {},
        "education": json.loads(resume.education) if resume.education else [],
        "experience": json.loads(resume.experience) if resume.experience else [],
        "skills": json.loads(resume.skills) if resume.skills else [],
        "projects": json.loads(resume.projects) if resume.projects else [],
        "highlights": json.loads(resume.highlights) if resume.highlights else []
    }

    # 调用岗位匹配服务
    from app.services.job_match_service import JobMatchService
    from app.schemas.common import ApiResponse
    match_result = await JobMatchService.analyze_job_match(resume_data, request.job_description)

    return ApiResponse(
        code=200,
        message="匹配分析完成",
        data=JobMatchResponse(**match_result)
    )