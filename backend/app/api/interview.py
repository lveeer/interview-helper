from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import json
from app.core.database import get_db
from app.models.user import User
from app.models.resume import Resume
from app.models.interview import Interview, InterviewStatus
from app.schemas.interview import InterviewCreate, InterviewResponse, InterviewAnswer
from app.api.auth import get_current_user

router = APIRouter()


@router.post("/create", status_code=201)
async def create_interview(
    interview_data: InterviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建新的面试会话（异步生成问题）"""
    import asyncio
    from app.schemas.common import ApiResponse

    print(f"[创建面试] 开始处理，用户ID: {current_user.id}, 简历ID: {interview_data.resume_id}")

    # 验证简历
    resume = db.query(Resume).filter(
        Resume.id == interview_data.resume_id,
        Resume.user_id == current_user.id
    ).first()
    if not resume:
        print(f"[创建面试] 简历不存在，简历ID: {interview_data.resume_id}, 用户ID: {current_user.id}")
        raise HTTPException(
            status_code=404,
            detail="简历不存在"
        )
    print(f"[创建面试] 简历验证通过")

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
        print(f"[创建面试] 简历数据构建完成")
    except Exception as e:
        print(f"[创建面试] 简历数据解析失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"简历数据解析失败: {str(e)}"
        )

    # 创建面试记录（状态为初始化中）
    try:
        print(f"[创建面试] 开始创建数据库记录...")
        db_interview = Interview(
            user_id=current_user.id,
            resume_id=interview_data.resume_id,
            job_description=interview_data.job_description,
            status=InterviewStatus.initializing,
            questions=None,
            conversation=json.dumps([])
        )
        db.add(db_interview)
        db.commit()
        db.refresh(db_interview)
        print(f"[创建面试] 数据库记录创建成功，面试ID: {db_interview.id}")
    except Exception as e:
        print(f"[创建面试] 数据库操作失败: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"创建面试记录失败: {str(e)}"
        )

    # 启动后台异步任务生成面试问题
    from app.services.interview_service import InterviewService
    from app.services.task_notification_service import task_notification_service
    
    # 注册任务通知
    from app.models.task_notification import TaskType
    task_id = f"interview_{db_interview.id}"
    task_notification_service.register_task(
        task_id=task_id,
        user_id=current_user.id,
        task_type=TaskType.INTERVIEW_GENERATION,
        task_title=f"面试问题生成 - JD: {interview_data.job_description[:30]}...",
        metadata={
            "interview_id": db_interview.id,
            "resume_id": interview_data.resume_id,
            "job_title": interview_data.job_description[:50] if len(interview_data.job_description) > 50 else interview_data.job_description
        },
        db=db
    )
    
    asyncio.create_task(
        InterviewService.generate_interview_questions_async(
            db=db,
            interview_id=db_interview.id,
            resume_data=resume_data,
            job_description=interview_data.job_description,
            num_questions=10,
            user_id=current_user.id,
            knowledge_doc_ids=interview_data.knowledge_doc_ids,
            task_id=task_id
        )
    )
    print(f"[创建面试] 已启动后台任务生成面试问题，任务ID: {task_id}")

    # 构建响应数据，将 JSON 字符串解析为 Python 对象
    response_data = {
        "id": db_interview.id,
        "user_id": db_interview.user_id,
        "resume_id": db_interview.resume_id,
        "job_description": db_interview.job_description,
        "status": db_interview.status,
        "total_score": db_interview.total_score,
        "questions": json.loads(db_interview.questions) if db_interview.questions else [],
        "conversation": json.loads(db_interview.conversation) if db_interview.conversation else [],
        "created_at": db_interview.created_at
    }

    return ApiResponse(
        code=201,
        message="面试创建成功，正在生成面试问题，请稍后刷新查看",
        data=InterviewResponse(**response_data)
    )


@router.get("/{interview_id}")
async def get_interview(
    interview_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取面试详情"""
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

    # 构建响应数据，将 JSON 字符串解析为 Python 对象
    response_data = {
        "id": interview.id,
        "user_id": interview.user_id,
        "resume_id": interview.resume_id,
        "job_description": interview.job_description,
        "status": interview.status,
        "total_score": interview.total_score,
        "questions": json.loads(interview.questions) if interview.questions else [],
        "conversation": json.loads(interview.conversation) if interview.conversation else [],
        "created_at": interview.created_at
    }

    return ApiResponse(
        code=200,
        message="获取成功",
        data=InterviewResponse(**response_data)
    )


@router.get("/{interview_id}/status")
async def get_interview_status(
    interview_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取面试问题生成状态"""
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

    # 解析错误信息
    error_info = None
    if interview.generation_error:
        try:
            error_info = json.loads(interview.generation_error)
        except:
            error_info = {"error": interview.generation_error}

    # 判断生成状态
    if interview.status == InterviewStatus.initializing:
        generation_status = "generating"
        message = "正在生成面试问题，请稍后..."
    elif interview.questions:
        generation_status = "completed"
        message = "面试问题已生成"
    elif error_info:
        generation_status = "failed"
        message = "面试问题生成失败"
    else:
        generation_status = "unknown"
        message = "状态未知"

    return ApiResponse(
        code=200,
        message="获取成功",
        data={
            "interview_id": interview.id,
            "status": interview.status,
            "generation_status": generation_status,
            "message": message,
            "has_questions": interview.questions is not None,
            "error": error_info
        }
    )


@router.get("/")
async def get_interviews(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户的所有面试记录"""
    from app.schemas.common import ListResponse

    interviews = db.query(Interview).filter(
        Interview.user_id == current_user.id
    ).order_by(Interview.created_at.desc()).all()

    # 构建响应数据列表，只返回列表页面需要的字段（精简版）
    interviews_data = []
    for interview in interviews:
        interviews_data.append({
            "id": interview.id,
            "job_description": interview.job_description,
            "status": interview.status,
            "total_score": interview.total_score,
            "created_at": interview.created_at
        })

    return ListResponse(
        code=200,
        message="获取成功",
        data=interviews_data,
        total=len(interviews)
    )


@router.get("/{interview_id}/record")
async def get_interview_record(
    interview_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取面试的完整对话记录

    返回面试的所有问题和回答记录，包括：
    - questions: 面试问题列表
    - conversation: 完整的对话流（包含问题、回答、追问）

    **响应字段说明：**
    - id: 面试ID
    - user_id: 用户ID
    - resume_id: 简历ID
    - job_description: 职位描述（JD）
    - status: 面试状态（pending/in_progress/completed）
    - total_score: 总分
    - questions: 问题列表，每个问题包含：
      - id: 问题ID
      - question: 问题内容
      - category: 问题分类
      - difficulty: 难度
    - conversation: 对话记录数组，每条消息包含：
      - role: 角色（interviewer/candidate）
      - content: 消息内容
      - question_id: 关联的问题ID（可选）
      - category: 问题分类（可选）
      - difficulty: 难度（可选）
      - type: 问题类型（可选，"followup"表示追问）
      - reason: 追问原因（可选）
      - timestamp: 时间戳（可选）
    - created_at: 创建时间
    """
    from app.schemas.common import ApiResponse
    from app.schemas.interview import InterviewRecordResponse

    interview = db.query(Interview).filter(
        Interview.id == interview_id,
        Interview.user_id == current_user.id
    ).first()
    if not interview:
        raise HTTPException(
            status_code=404,
            detail="面试不存在"
        )

    # 解析数据
    questions = json.loads(interview.questions) if interview.questions else []
    conversation = json.loads(interview.conversation) if interview.conversation else []

    # 构建完整的对话记录（包含问题和回答）
    full_conversation = []
    for msg in conversation:
        full_conversation.append({
            "role": msg.get("role"),
            "content": msg.get("content"),
            "question_id": msg.get("question_id"),
            "category": msg.get("category"),
            "difficulty": msg.get("difficulty"),
            "type": msg.get("type"),  # "followup" 或 None
            "reason": msg.get("reason"),  # 追问的原因
            "timestamp": msg.get("timestamp")
        })

    # 构建响应数据
    response_data = {
        "id": interview.id,
        "user_id": interview.user_id,
        "resume_id": interview.resume_id,
        "job_description": interview.job_description,
        "status": interview.status,
        "total_score": interview.total_score,
        "questions": questions,
        "conversation": full_conversation,
        "created_at": interview.created_at
    }

    return ApiResponse(
        code=200,
        message="获取成功",
        data=response_data
    )


@router.websocket("/ws/{interview_id}")
async def interview_websocket(
    websocket: WebSocket,
    interview_id: int,
    db: Session = Depends(get_db)
):
    """面试 WebSocket 连接"""
    await websocket.accept()

    try:
        # 获取面试信息
        interview = db.query(Interview).filter(
            Interview.id == interview_id
        ).first()
        if not interview:
            await websocket.close(code=4004, reason="面试不存在")
            return

        # 获取简历数据
        resume = db.query(Resume).filter(
            Resume.id == interview.resume_id
        ).first()
        if not resume:
            await websocket.close(code=4004, reason="简历不存在")
            return

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
            await websocket.close(code=4000, reason=f"简历数据解析失败: {str(e)}")
            return

        # 更新面试状态为进行中
        interview.status = InterviewStatus.in_progress
        db.commit()

        # 发送第一个问题并记录
        from datetime import datetime
        questions = json.loads(interview.questions)
        conversation = json.loads(interview.conversation) if interview.conversation else []

        # 记录第一个问题
        conversation.append({
            "role": "interviewer",
            "content": questions[0]["question"],
            "question_id": questions[0]["id"],
            "category": questions[0]["category"],
            "difficulty": questions[0]["difficulty"],
            "timestamp": datetime.now().isoformat()
        })
        interview.conversation = json.dumps(conversation)
        db.commit()

        await websocket.send_json({
            "type": "question",
            "data": questions[0]
        })

        # 处理用户回答
        current_question_index = 0
        while True:
            data = await websocket.receive_json()

            if data.get("type") == "answer":
                # 保存求职者回答
                conversation = json.loads(interview.conversation)
                conversation.append({
                    "role": "candidate",
                    "content": data.get("answer"),
                    "question_id": questions[current_question_index]["id"],
                    "timestamp": datetime.now().isoformat()
                })
                interview.conversation = json.dumps(conversation)
                db.commit()

                # 调用追问生成服务
                from app.services.interview_service import InterviewService
                followup_result = await InterviewService.generate_followup_question(
                    questions[current_question_index]["question"],
                    data.get("answer"),
                    conversation,
                    resume_data
                )

                if followup_result.get("type") == "followup":
                    # 记录并发送追问
                    conversation = json.loads(interview.conversation)
                    conversation.append({
                        "role": "interviewer",
                        "content": followup_result["question"],
                        "type": "followup",
                        "reason": followup_result.get("reason", ""),
                        "question_id": questions[current_question_index]["id"],
                        "timestamp": datetime.now().isoformat()
                    })
                    interview.conversation = json.dumps(conversation)
                    db.commit()

                    await websocket.send_json({
                        "type": "followup",
                        "data": {
                            "question": followup_result["question"],
                            "reason": followup_result.get("reason", "")
                        }
                    })
                else:
                    # 发送下一个问题
                    current_question_index += 1
                    if current_question_index < len(questions):
                        # 记录下一个问题
                        conversation = json.loads(interview.conversation)
                        conversation.append({
                            "role": "interviewer",
                            "content": questions[current_question_index]["question"],
                            "question_id": questions[current_question_index]["id"],
                            "category": questions[current_question_index]["category"],
                            "difficulty": questions[current_question_index]["difficulty"],
                            "timestamp": datetime.now().isoformat()
                        })
                        interview.conversation = json.dumps(conversation)
                        db.commit()

                        await websocket.send_json({
                            "type": "question",
                            "data": questions[current_question_index]
                        })
                    else:
                        # 面试结束
                        interview.status = InterviewStatus.completed
                        db.commit()
                        await websocket.send_json({
                            "type": "end",
                            "message": "面试已结束"
                        })
                        break

            elif data.get("type") == "end":
                # 用户主动结束面试
                interview.status = InterviewStatus.completed
                db.commit()
                break

    except WebSocketDisconnect:
        # 连接断开
        if interview.status == InterviewStatus.in_progress:
            interview.status = InterviewStatus.completed
            db.commit()
    except Exception as e:
        await websocket.close(code=4000, reason=str(e))