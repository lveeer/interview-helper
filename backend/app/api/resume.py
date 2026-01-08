from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.user import User
from app.models.resume import Resume
from app.schemas.resume import (
    ResumeResponse,
    OptimizationSuggestion,
    OptimizationApplyRequest,
    OptimizationApplyResponse,
    OptimizationHistoryItem,
    ResumeCompareResult,
    ResumeRestoreRequest,
    ResumeRestoreResponse
)
from app.api.auth import get_current_user
from app.services.resume_optimization_service import ResumeOptimizationService
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


# ========== 简历优化相关 API ==========
# 注意：这些带有子路径的路由必须在 /{resume_id} 之前定义，避免路由冲突

@router.post("/{resume_id}/analyze")
async def analyze_resume(
    resume_id: int,
    force_refresh: bool = Query(False, description="是否强制重新分析"),
    jd: Optional[str] = Query(None, description="目标职位描述（可选），用于针对性分析"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """分析简历，生成多维度评分和分析报告"""
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"API接收到参数: resume_id={resume_id}, force_refresh={force_refresh}, jd={bool(jd)}, jd_value={jd[:50] if jd else None}")

    from app.schemas.common import ApiResponse

    # 验证简历所有权
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="简历不存在"
        )

    # 获取 LLM 服务
    from app.services.llm_service import get_iflow_llm
    llm_service = await get_iflow_llm()

    # 分析简历
    try:
        analysis_result = await ResumeOptimizationService.analyze_resume(
            db=db,
            resume_id=resume_id,
            llm_service=llm_service,
            force_refresh=force_refresh,
            jd=jd
        )

        return ApiResponse(
            code=200,
            message="分析成功",
            data=analysis_result
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"分析失败: {str(e)}"
        )


@router.get("/{resume_id}/suggestions")
async def get_optimization_suggestions(
    resume_id: int,
    force_refresh: bool = Query(False, description="是否强制重新生成"),
    jd: Optional[str] = Query(None, description="目标职位描述（可选），用于针对性优化"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取简历优化建议"""
    from app.schemas.common import ApiResponse

    # 验证简历所有权
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="简历不存在"
        )

    # 获取 LLM 服务
    from app.services.llm_service import get_iflow_llm
    llm_service = await get_iflow_llm()

    # 生成优化建议
    try:
        suggestions = await ResumeOptimizationService.generate_suggestions(
            db=db,
            resume_id=resume_id,
            llm_service=llm_service,
            force_refresh=force_refresh,
            jd=jd
        )

        return ApiResponse(
            code=200,
            message="获取成功",
            data=suggestions
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取优化建议失败: {str(e)}"
        )


@router.post("/{resume_id}/optimize")
async def apply_optimizations(
    resume_id: int,
    request: OptimizationApplyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """应用优化建议到简历"""
    from app.schemas.common import ApiResponse

    # 验证简历所有权
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="简历不存在"
        )

    # 应用优化建议
    try:
        result = ResumeOptimizationService.apply_optimizations(
            db=db,
            resume_id=resume_id,
            suggestions=[s.model_dump() for s in request.suggestions]
        )

        return ApiResponse(
            code=200,
            message="优化应用成功",
            data=result
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"应用优化失败: {str(e)}"
        )


@router.get("/{resume_id}/optimization-history")
async def get_optimization_history(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取简历优化历史"""
    from app.schemas.common import ApiResponse

    # 验证简历所有权
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="简历不存在"
        )

    # 获取优化历史
    try:
        history = ResumeOptimizationService.get_optimization_history(
            db=db,
            resume_id=resume_id
        )

        return ApiResponse(
            code=200,
            message="获取成功",
            data=history
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取优化历史失败: {str(e)}"
        )


@router.get("/{resume_id}/export")
async def export_resume(
    resume_id: int,
    format: str = Query("pdf", description="导出格式：pdf 或 docx"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """导出优化后的简历"""
    # 验证简历所有权
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="简历不存在"
        )

    # 验证导出格式
    if format not in ["pdf", "docx"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不支持的导出格式，仅支持 pdf 和 docx"
        )

    # 检查文件是否存在
    if not os.path.exists(resume.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="简历文件不存在"
        )

    # 返回文件
    file_name = f"optimized_resume_{resume.current_version}.{format}"
    return FileResponse(
        path=resume.file_path,
        filename=file_name,
        media_type="application/pdf" if format == "pdf" else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )


@router.get("/{resume_id}/compare")
async def compare_resume_versions(
    resume_id: int,
    version1: str = Query(..., description="版本1"),
    version2: str = Query(..., description="版本2"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """比较两个版本的简历差异"""
    from app.schemas.common import ApiResponse

    # 验证简历所有权
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="简历不存在"
        )

    # 比较版本
    try:
        result = ResumeOptimizationService.compare_versions(
            db=db,
            resume_id=resume_id,
            version1=version1,
            version2=version2
        )

        return ApiResponse(
            code=200,
            message="对比成功",
            data=result
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"版本对比失败: {str(e)}"
        )


@router.post("/{resume_id}/restore")
async def restore_resume_version(
    resume_id: int,
    request: ResumeRestoreRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """恢复简历到指定历史版本"""
    from app.schemas.common import ApiResponse

    # 验证简历所有权
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="简历不存在"
        )

    # 恢复版本
    try:
        result = ResumeOptimizationService.restore_version(
            db=db,
            resume_id=resume_id,
            version=request.version
        )

        return ApiResponse(
            code=200,
            message="恢复成功",
            data=result
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"恢复失败: {str(e)}"
        )


# ========== 基础简历操作 API ==========
# 注意：这些通用的 /{resume_id} 路由必须在所有带有子路径的路由之后定义

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