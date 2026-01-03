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
    """创建新的面试会话"""
    from app.schemas.common import ApiResponse

    # 验证简历
    resume = db.query(Resume).filter(
        Resume.id == interview_data.resume_id,
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

    # 调用面试问题生成服务
    from app.services.interview_service import InterviewService
    questions = await InterviewService.generate_interview_questions(
        resume_data,
        interview_data.job_description
    )

    # 创建面试记录
    db_interview = Interview(
        user_id=current_user.id,
        resume_id=interview_data.resume_id,
        job_description=interview_data.job_description,
        status=InterviewStatus.PENDING,
        questions=json.dumps(questions),
        conversation=json.dumps([])
    )
    db.add(db_interview)
    db.commit()
    db.refresh(db_interview)

    return ApiResponse(
        code=201,
        message="面试创建成功",
        data=InterviewResponse.model_validate(db_interview)
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
    return ApiResponse(
        code=200,
        message="获取成功",
        data=InterviewResponse.model_validate(interview)
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
    ).all()
    return ListResponse(
        code=200,
        message="获取成功",
        data=[InterviewResponse.model_validate(i) for i in interviews],
        total=len(interviews)
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

        # 更新面试状态为进行中
        interview.status = InterviewStatus.IN_PROGRESS
        db.commit()

        # 发送第一个问题
        questions = json.loads(interview.questions)
        await websocket.send_json({
            "type": "question",
            "data": questions[0]
        })

        # 处理用户回答
        current_question_index = 0
        while True:
            data = await websocket.receive_json()

            if data.get("type") == "answer":
                # 保存对话记录
                conversation = json.loads(interview.conversation)
                conversation.append({
                    "role": "candidate",
                    "content": data.get("answer"),
                    "question_id": questions[current_question_index]["id"]
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
                    # 发送追问
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
                        await websocket.send_json({
                            "type": "question",
                            "data": questions[current_question_index]
                        })
                    else:
                        # 面试结束
                        interview.status = InterviewStatus.COMPLETED
                        db.commit()
                        await websocket.send_json({
                            "type": "end",
                            "message": "面试已结束"
                        })
                        break

            elif data.get("type") == "end":
                # 用户主动结束面试
                interview.status = InterviewStatus.COMPLETED
                db.commit()
                break

    except WebSocketDisconnect:
        # 连接断开
        if interview.status == InterviewStatus.IN_PROGRESS:
            interview.status = InterviewStatus.COMPLETED
            db.commit()
    except Exception as e:
        await websocket.close(code=4000, reason=str(e))