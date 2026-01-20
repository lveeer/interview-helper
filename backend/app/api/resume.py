from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.user import User
from app.models.resume import Resume
from app.schemas.resume import (
    ResumeResponse,
    ResumeListItem,
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
import logging
from config import settings

# 配置日志
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """上传简历文件并使用 LLM 增强解析"""
    from app.schemas.common import ApiResponse
    import asyncio
    import threading

    logger.info(f"用户 {current_user.id} 开始上传简历: {file.filename}")

    # 验证文件类型
    file_ext = os.path.splitext(file.filename)[1].lower()
    allowed_extensions = settings.get_allowed_extensions_list()
    if file_ext not in allowed_extensions:
        logger.warning(f"不支持的文件类型: {file_ext}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型，仅支持: {', '.join(allowed_extensions)}"
        )

    # 保存文件
    upload_dir = os.path.join(settings.UPLOAD_DIR, "resumes")
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f"{current_user.id}_{file.filename}")

    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        logger.info(f"文件保存成功: {file_path}")
    except Exception as e:
        logger.error(f"文件保存失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件保存失败: {str(e)}"
        )

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

    logger.info(f"简历记录创建成功，ID: {db_resume.id}")

    # 生成任务ID
    from app.models.task_notification import TaskType
    task_id = f"resume_{db_resume.id}"

    # 在独立线程中运行异步任务（fire-and-forget）
    def run_async_task():
        asyncio.run(
            parse_resume_with_registration(
                resume_id=db_resume.id,
                file_path=file_path,
                file_name=file.filename,
                user_id=current_user.id,
                task_id=task_id,
                task_type=TaskType.RESUME_PARSE,
                task_title=f"简历解析 - {file.filename}"
            )
        )

    thread = threading.Thread(target=run_async_task, daemon=True)
    thread.start()

    # 立即返回响应
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
    """获取用户的所有简历（轻量级响应）"""
    from app.schemas.common import ListResponse

    # 只查询列表需要的字段，减少数据传输，按创建时间倒序排列
    resumes = db.query(
        Resume.id,
        Resume.file_name,
        Resume.file_type,
        Resume.created_at
    ).filter(Resume.user_id == current_user.id).order_by(Resume.created_at.desc()).all()

    return ListResponse(
        code=200,
        message="获取成功",
        data=[ResumeListItem.model_validate(r) for r in resumes],
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

@router.post("/{resume_id}/reparse")
async def reparse_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """重新解析简历（使用最新的提示词）- 异步处理"""
    from app.schemas.common import ApiResponse
    import asyncio
    import threading

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

    # 检查文件是否存在
    if not os.path.exists(resume.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="简历文件不存在"
        )

    # 生成任务ID
    from app.models.task_notification import TaskType
    task_id = f"resume_reparse_{resume_id}"

    # 在独立线程中运行异步任务（fire-and-forget）
    def run_async_task():
        asyncio.run(
            reparse_resume_with_registration(
                resume_id=resume_id,
                file_path=resume.file_path,
                file_name=resume.file_name,
                user_id=current_user.id,
                task_id=task_id,
                task_type=TaskType.RESUME_PARSE,
                task_title=f"简历重新解析 - {resume.file_name}"
            )
        )

    thread = threading.Thread(target=run_async_task, daemon=True)
    thread.start()

    # 立即返回响应
    return ApiResponse(
        code=200,
        message="重新解析任务已启动",
        data={
            "task_id": task_id,
            "resume_id": resume_id,
            "status": "running"
        }
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


async def parse_resume_with_registration(
    resume_id: int,
    file_path: str,
    file_name: str,
    user_id: int,
    task_id: str,
    task_type: str,
    task_title: str
):
    """包装函数：注册任务并执行解析（用于 BackgroundTasks）"""
    from app.services.task_notification_service import task_notification_service
    from app.core.database import SessionLocal
    
    db = SessionLocal()
    try:
        # 注册任务
        await task_notification_service.register_task(
            task_id=task_id,
            user_id=user_id,
            task_type=task_type,
            task_title=task_title,
            extra_data={
                "resume_id": resume_id,
                "file_name": file_name
            },
            db=db
        )
    finally:
        db.close()
    
    # 执行解析
    await parse_resume_async(
        resume_id=resume_id,
        file_path=file_path,
        file_name=file_name,
        user_id=user_id,
        task_id=task_id
    )


async def reparse_resume_with_registration(
    resume_id: int,
    file_path: str,
    file_name: str,
    user_id: int,
    task_id: str,
    task_type: str,
    task_title: str
):
    """包装函数：注册任务并执行重新解析（用于 BackgroundTasks）"""
    from app.services.task_notification_service import task_notification_service
    from app.core.database import SessionLocal
    
    db = SessionLocal()
    try:
        # 注册任务
        await task_notification_service.register_task(
            task_id=task_id,
            user_id=user_id,
            task_type=task_type,
            task_title=task_title,
            extra_data={
                "resume_id": resume_id,
                "file_name": file_name
            },
            db=db
        )
    finally:
        db.close()
    
    # 执行重新解析
    await reparse_resume_async(
        resume_id=resume_id,
        file_path=file_path,
        file_name=file_name,
        user_id=user_id,
        task_id=task_id
    )


async def parse_resume_async(
    resume_id: int,
    file_path: str,
    file_name: str,
    user_id: int,
    task_id: str
):
    """异步解析简历"""
    from app.services.resume_service import parse_resume_with_llm
    from app.services.llm_service import get_iflow_llm
    from app.services.task_notification_service import task_notification_service
    from app.core.database import SessionLocal
    
    # 创建新的数据库会话
    db = SessionLocal()
    
    try:
        # 通知任务开始
        await task_notification_service.notify_started(
            task_id,
            message="正在解析简历..."
        )
        
        # 获取 LLM 服务
        llm_service = await get_iflow_llm()
        
        # 通知进度
        await task_notification_service.notify_progress(
            task_id,
            progress=30,
            message="正在提取简历内容...",
            step="内容提取"
        )
        
        # 使用 LLM 增强解析
        logger.info(f"开始解析简历 {resume_id}")
        parsed_data = await parse_resume_with_llm(file_path, llm_service)
        
        # 通知进度
        await task_notification_service.notify_progress(
            task_id,
            progress=70,
            message="正在保存解析结果...",
            step="保存数据"
        )
        
        # 保存解析结果
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if resume:
            resume.personal_info = json.dumps(parsed_data.get("personal_info"), ensure_ascii=False)
            resume.education = json.dumps(parsed_data.get("education"), ensure_ascii=False)
            resume.experience = json.dumps(parsed_data.get("experience"), ensure_ascii=False)
            resume.skills = json.dumps(parsed_data.get("skills"), ensure_ascii=False)
            resume.projects = json.dumps(parsed_data.get("projects"), ensure_ascii=False)
            resume.highlights = json.dumps(parsed_data.get("highlights"), ensure_ascii=False)
            resume.skills_raw = json.dumps(parsed_data.get("skills_raw", []), ensure_ascii=False)
            db.commit()

            logger.info(f"简历 {resume_id} 解析完成 - "
                       f"技能: {len(parsed_data.get('skills', []))}, "
                       f"教育: {len(parsed_data.get('education', []))}, "
                       f"经历: {len(parsed_data.get('experience', []))}, "
                       f"项目: {len(parsed_data.get('projects', []))}")
        
        # 通知任务完成
        await task_notification_service.notify_completed(
            task_id,
            result={
                "resume_id": resume_id,
                "skills_count": len(parsed_data.get('skills', [])),
                "education_count": len(parsed_data.get('education', [])),
                "experience_count": len(parsed_data.get('experience', [])),
                "projects_count": len(parsed_data.get('projects', []))
            },
            message=f"简历解析完成！提取了 {len(parsed_data.get('skills', []))} 项技能",
            redirect_url="/resume",
            redirect_params=None,
            db=db
        )
        
    except Exception as e:
        logger.error(f"简历解析失败: {e}", exc_info=True)
        db.rollback()
        
        # 通知任务失败
        await task_notification_service.notify_failed(
            task_id,
            error=str(e),
            error_type=type(e).__name__,
            db=db
        )
    finally:
        db.close()


async def reparse_resume_async(
    resume_id: int,
    file_path: str,
    file_name: str,
    user_id: int,
    task_id: str
):
    """异步重新解析简历"""
    from app.services.resume_service import parse_resume_with_llm
    from app.services.llm_service import get_iflow_llm
    from app.services.task_notification_service import task_notification_service
    from app.core.database import SessionLocal
    
    # 创建新的数据库会话
    db = SessionLocal()
    
    try:
        # 通知任务开始
        await task_notification_service.notify_started(
            task_id,
            message="正在重新解析简历..."
        )
        
        # 获取 LLM 服务
        llm_service = await get_iflow_llm()
        
        # 通知进度
        await task_notification_service.notify_progress(
            task_id,
            progress=30,
            message="正在提取简历内容...",
            step="内容提取"
        )
        
        # 使用 LLM 重新解析
        logger.info(f"开始重新解析简历 {resume_id}")
        parsed_data = await parse_resume_with_llm(file_path, llm_service)
        
        # 通知进度
        await task_notification_service.notify_progress(
            task_id,
            progress=70,
            message="正在保存解析结果...",
            step="保存数据"
        )
        
        # 更新解析结果
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if resume:
            resume.personal_info = json.dumps(parsed_data.get("personal_info"), ensure_ascii=False)
            resume.education = json.dumps(parsed_data.get("education"), ensure_ascii=False)
            resume.experience = json.dumps(parsed_data.get("experience"), ensure_ascii=False)
            resume.skills = json.dumps(parsed_data.get("skills"), ensure_ascii=False)
            resume.skills_raw = json.dumps(parsed_data.get("skills_raw", []), ensure_ascii=False)
            resume.projects = json.dumps(parsed_data.get("projects"), ensure_ascii=False)
            resume.highlights = json.dumps(parsed_data.get("highlights"), ensure_ascii=False)
            db.commit()

            logger.info(f"简历 {resume_id} 重新解析完成 - "
                       f"技能: {len(parsed_data.get('skills', []))}, "
                       f"教育: {len(parsed_data.get('education', []))}, "
                       f"经历: {len(parsed_data.get('experience', []))}, "
                       f"项目: {len(parsed_data.get('projects', []))}")
        
        # 通知任务完成
        await task_notification_service.notify_completed(
            task_id,
            result={
                "resume_id": resume_id,
                "skills_count": len(parsed_data.get('skills', [])),
                "education_count": len(parsed_data.get('education', [])),
                "experience_count": len(parsed_data.get('experience', [])),
                "projects_count": len(parsed_data.get('projects', []))
            },
            message=f"简历重新解析完成！提取了 {len(parsed_data.get('skills', []))} 项技能",
            redirect_url="/resume",
            redirect_params=None,
            db=db
        )
        
    except Exception as e:
        logger.error(f"简历重新解析失败: {e}", exc_info=True)
        db.rollback()
        
        # 通知任务失败
        await task_notification_service.notify_failed(
            task_id,
            error=str(e),
            error_type=type(e).__name__,
            db=db
        )
    finally:
        db.close()