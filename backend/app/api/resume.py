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
    """上传简历文件"""
    from app.schemas.common import ApiResponse

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

    # 调用简历解析服务
    try:
        from app.services.resume_service import ResumeParser
        parsed_data = ResumeParser.parse_resume(file_path)
        db_resume.personal_info = json.dumps(parsed_data.get("personal_info"))
        db_resume.education = json.dumps(parsed_data.get("education"))
        db_resume.experience = json.dumps(parsed_data.get("experience"))
        db_resume.skills = json.dumps(parsed_data.get("skills"))
        db_resume.projects = json.dumps(parsed_data.get("projects"))
        db_resume.highlights = json.dumps(parsed_data.get("highlights"))
        db.commit()
    except Exception as e:
        print(f"简历解析失败: {e}")
        # 解析失败不影响简历上传，继续返回

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