from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.user import User
from app.models.resume import Resume
from app.schemas.resume import ResumeResponse
from app.api.auth import get_current_user
import os
import json
from config import settings

router = APIRouter()


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """上传简历文件并使用 LLM 增强解析"""
    from app.schemas.common import ApiResponse
    import logging

    logger = logging.getLogger(__name__)

    # 验证文件类型
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型，仅支持: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )

    # 保存文件
    upload_dir = os.path.join(settings.UPLOAD_DIR, "resumes")
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f"{current_user.id}_{file.filename}")

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    logger.info(f"用户 {current_user.id} 上传简历: {file.filename}")

    # 创建简历记录
    db_resume = Resume(
        user_id=current_user.id,
        file_name=file.filename,
        file_path=file_path,
        file_type=file_ext[1:]  # 去掉点号
    )
    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)

    # 调用简历解析服务（使用 LLM 增强）
    try:
        from app.services.resume_service import parse_resume_with_llm
        from app.services.llm_service import get_iflow_llm
        
        # 获取 LLM 服务
        llm_service = await get_iflow_llm()
        
        # 使用 LLM 增强解析
        parsed_data = await parse_resume_with_llm(file_path, llm_service)
        
        # 保存解析结果
        db_resume.personal_info = json.dumps(parsed_data.get("personal_info"), ensure_ascii=False)
        db_resume.education = json.dumps(parsed_data.get("education"), ensure_ascii=False)
        db_resume.experience = json.dumps(parsed_data.get("experience"), ensure_ascii=False)
        db_resume.skills = json.dumps(parsed_data.get("skills"), ensure_ascii=False)
        db_resume.projects = json.dumps(parsed_data.get("projects"), ensure_ascii=False)
        db_resume.highlights = json.dumps(parsed_data.get("highlights"), ensure_ascii=False)
        db.commit()
        
        logger.info(f"简历 {db_resume.id} 解析完成，提取到 {len(parsed_data.get('skills', []))} 个技能")
        
    except Exception as e:
        logger.error(f"简历解析失败: {e}", exc_info=True)
        # 解析失败不影响简历上传，继续返回
        # 可以选择在这里使用基础解析作为后备
        try:
            from app.services.resume_service import ResumeParser
            parsed_data = ResumeParser.parse_resume(file_path)
            db_resume.personal_info = json.dumps(parsed_data.get("personal_info"), ensure_ascii=False)
            db_resume.education = json.dumps(parsed_data.get("education"), ensure_ascii=False)
            db_resume.experience = json.dumps(parsed_data.get("experience"), ensure_ascii=False)
            db_resume.skills = json.dumps(parsed_data.get("skills"), ensure_ascii=False)
            db_resume.projects = json.dumps(parsed_data.get("projects"), ensure_ascii=False)
            db_resume.highlights = json.dumps(parsed_data.get("highlights"), ensure_ascii=False)
            db.commit()
            logger.info("使用基础解析完成简历解析")
        except Exception as fallback_error:
            logger.error(f"基础解析也失败: {fallback_error}", exc_info=True)

    return ApiResponse(
        code=201,
        message="简历上传成功",
        data=ResumeResponse.model_validate(db_resume)
    )


@router.get("/")
async def get_resumes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户的所有简历"""
    from app.schemas.common import ListResponse

    resumes = db.query(Resume).filter(Resume.user_id == current_user.id).all()
    return ListResponse(
        code=200,
        message="获取成功",
        data=[ResumeResponse.model_validate(r) for r in resumes],
        total=len(resumes)
    )


@router.get("/{resume_id}")
async def get_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取指定简历"""
    from app.schemas.common import ApiResponse

    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="简历不存在"
        )
    return ApiResponse(
        code=200,
        message="获取成功",
        data=ResumeResponse.model_validate(resume)
    )


@router.delete("/{resume_id}")
async def delete_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除简历"""
    from app.schemas.common import SuccessResponse

    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="简历不存在"
    )
    # 删除文件
    if os.path.exists(resume.file_path):
        os.remove(resume.file_path)
    # 删除数据库记录
    db.delete(resume)
    db.commit()
    return SuccessResponse()