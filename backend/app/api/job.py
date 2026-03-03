from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List
import json
import asyncio

from app.core.database import get_db, get_async_db, AsyncSessionLocal
from app.models.user import User
from app.models.resume import Resume
from app.models.job import Job
from app.models.interview import Interview, InterviewStatus
from app.schemas.job import (
    JobMatchRequest, JobMatchResponse,
    JobCreate, JobUpdate, JobResponse, JobBriefResponse
)
from app.schemas.interview import InterviewCreate, InterviewResponse
from app.schemas.common import ApiResponse, ListResponse
from app.api.auth import get_current_user

router = APIRouter()


# ===== 岗位管理 API =====

@router.post("", status_code=201, response_model=ApiResponse[JobResponse])
async def create_job(
    job_data: JobCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """创建岗位"""
    db_job = Job(
        user_id=current_user.id,
        title=job_data.title,
        company=job_data.company,
        job_description=job_data.job_description
    )
    db.add(db_job)
    await db.commit()
    await db.refresh(db_job)

    return ApiResponse(
        code=201,
        message="岗位创建成功",
        data=JobResponse.model_validate(db_job)
    )


@router.get("", response_model=ListResponse[JobResponse])
async def get_jobs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """获取用户的岗位列表"""
    result = await db.execute(
        select(Job)
        .where(Job.user_id == current_user.id)
        .order_by(desc(Job.created_at))
    )
    jobs = result.scalars().all()

    return ListResponse(
        code=200,
        message="获取成功",
        data=[JobResponse.model_validate(job) for job in jobs],
        total=len(jobs)
    )


@router.get("/{job_id}", response_model=ApiResponse[JobResponse])
async def get_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """获取岗位详情"""
    result = await db.execute(
        select(Job).where(
            Job.id == job_id,
            Job.user_id == current_user.id
        )
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="岗位不存在")

    return ApiResponse(
        code=200,
        message="获取成功",
        data=JobResponse.model_validate(job)
    )


@router.put("/{job_id}", response_model=ApiResponse[JobResponse])
async def update_job(
    job_id: int,
    job_data: JobUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """更新岗位信息"""
    result = await db.execute(
        select(Job).where(
            Job.id == job_id,
            Job.user_id == current_user.id
        )
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="岗位不存在")

    # 更新字段
    if job_data.title is not None:
        job.title = job_data.title
    if job_data.company is not None:
        job.company = job_data.company
    if job_data.job_description is not None:
        job.job_description = job_data.job_description

    await db.commit()
    await db.refresh(job)

    return ApiResponse(
        code=200,
        message="更新成功",
        data=JobResponse.model_validate(job)
    )


@router.delete("/{job_id}")
async def delete_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """删除岗位"""
    result = await db.execute(
        select(Job).where(
            Job.id == job_id,
            Job.user_id == current_user.id
        )
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="岗位不存在")

    await db.delete(job)
    await db.commit()

    return ApiResponse(
        code=200,
        message="删除成功"
    )


# ===== 岗位面试关联 API =====

@router.post("/{job_id}/interviews", status_code=201)
async def create_job_interview(
    job_id: int,
    interview_data: InterviewCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """针对该岗位创建面试"""
    # 验证岗位
    result = await db.execute(
        select(Job).where(
            Job.id == job_id,
            Job.user_id == current_user.id
        )
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="岗位不存在")

    # 验证简历
    result = await db.execute(
        select(Resume).where(
            Resume.id == interview_data.resume_id,
            Resume.user_id == current_user.id
        )
    )
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="简历不存在")

    # 构建简历数据
    try:
        resume_data = {
            "personal_info": json.loads(resume.personal_info) if resume.personal_info else {},
            "education": json.loads(resume.education) if resume.education else [],
            "experience": json.loads(resume.experience) if resume.experience else [],
            "skills": json.loads(resume.skills) if resume.skills else [],
            "projects": json.loads(resume.projects) if resume.projects else [],
            "highlights": json.loads(resume.highlights) if resume.highlights else []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"简历数据解析失败: {str(e)}")

    # 创建面试记录（使用岗位的 JD）
    db_interview = Interview(
        user_id=current_user.id,
        resume_id=interview_data.resume_id,
        job_id=job_id,
        job_description=job.job_description,
        status=InterviewStatus.initializing,
        questions=None,
        conversation=json.dumps([])
    )
    db.add(db_interview)
    await db.commit()
    await db.refresh(db_interview)

    # 启动后台异步任务生成面试问题
    from app.services.interview_service import InterviewService
    from app.services.task_notification_service import task_notification_service
    from app.models.task_notification import TaskType

    task_id = f"interview_{db_interview.id}"
    await task_notification_service.register_task(
        task_id=task_id,
        user_id=current_user.id,
        task_type=TaskType.INTERVIEW_GENERATION,
        task_title=f"面试问题生成 - {job.title}",
        extra_data={
            "interview_id": db_interview.id,
            "resume_id": interview_data.resume_id,
            "job_id": job_id,
            "job_title": job.title
        },
        db=db
    )

    async def background_task():
        async with AsyncSessionLocal() as bg_db:
            await InterviewService.generate_interview_questions_async(
                db=bg_db,
                interview_id=db_interview.id,
                resume_data=resume_data,
                job_description=job.job_description,
                num_questions=10,
                user_id=current_user.id,
                knowledge_doc_ids=interview_data.knowledge_doc_ids,
                task_id=task_id
            )

    asyncio.create_task(background_task())

    response_data = {
        "id": db_interview.id,
        "user_id": db_interview.user_id,
        "resume_id": db_interview.resume_id,
        "job_id": db_interview.job_id,
        "job_description": db_interview.job_description,
        "status": db_interview.status,
        "total_score": db_interview.total_score,
        "questions": [],
        "conversation": [],
        "created_at": db_interview.created_at
    }

    return ApiResponse(
        code=201,
        message="面试创建成功，正在生成面试问题",
        data=InterviewResponse(**response_data)
    )


@router.get("/{job_id}/interviews")
async def get_job_interviews(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """获取该岗位的历史面试记录"""
    # 验证岗位
    result = await db.execute(
        select(Job).where(
            Job.id == job_id,
            Job.user_id == current_user.id
        )
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="岗位不存在")

    # 获取面试记录
    result = await db.execute(
        select(Interview)
        .where(Interview.job_id == job_id)
        .order_by(desc(Interview.created_at))
    )
    interviews = result.scalars().all()

    interviews_data = []
    for interview in interviews:
        interviews_data.append({
            "id": interview.id,
            "resume_id": interview.resume_id,
            "status": interview.status.value if interview.status else None,
            "total_score": interview.total_score,
            "created_at": interview.created_at.isoformat() if interview.created_at else None
        })

    return ListResponse(
        code=200,
        message="获取成功",
        data=interviews_data,
        total=len(interviews_data)
    )


# ===== 岗位匹配 API（原有功能）=====

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
        raise HTTPException(status_code=404, detail="简历不存在")

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
    match_result = await JobMatchService.analyze_job_match(resume_data, request.job_description)

    return ApiResponse(
        code=200,
        message="匹配分析完成",
        data=JobMatchResponse(**match_result)
    )
