"""面试官人设 API"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from app.core.database import get_async_db
from app.api.auth import get_current_user
from app.models.user import User
from app.services.persona_service import PersonaManager, initialize_personas
from app.models.persona import InterviewerPersona
from app.schemas.common import ApiResponse


router = APIRouter(prefix="/personas", tags=["personas"])


# Pydantic 模型
class PersonaConfig(BaseModel):
    """人设配置"""
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    max_followup: int = Field(default=3, ge=1, le=10)
    question_difficulty: str = Field(default="adaptive")
    response_length: str = Field(default="medium")
    strictness: float = Field(default=0.5, ge=0.0, le=1.0)
    patience: float = Field(default=0.5, ge=0.0, le=1.0)
    technical_depth: float = Field(default=0.5, ge=0.0, le=1.0)
    communication_focus: float = Field(default=0.5, ge=0.0, le=1.0)


class PersonaCreate(BaseModel):
    """创建人设请求"""
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(default="")
    tone: str = Field(default="professional")
    focus_areas: List[str] = Field(default_factory=list)
    questioning_style: str = Field(default="balanced")
    followup_frequency: str = Field(default="medium")
    encouragement_level: str = Field(default="medium")
    conversation_style: str = Field(default="professional")
    personality_traits: List[str] = Field(default_factory=list)
    question_templates: List[str] = Field(default_factory=list)
    transition_phrases: List[str] = Field(default_factory=list)
    feedback_phrases: List[str] = Field(default_factory=list)
    encouragement_phrases: List[str] = Field(default_factory=list)
    config: PersonaConfig = Field(default_factory=PersonaConfig)


class PersonaUpdate(BaseModel):
    """更新人设请求"""
    name: str = Field(None, min_length=1, max_length=100)
    description: str = Field(None)
    tone: str = Field(None)
    focus_areas: List[str] = Field(None)
    questioning_style: str = Field(None)
    followup_frequency: str = Field(None)
    encouragement_level: str = Field(None)
    conversation_style: str = Field(None)
    personality_traits: List[str] = Field(None)
    question_templates: List[str] = Field(None)
    transition_phrases: List[str] = Field(None)
    feedback_phrases: List[str] = Field(None)
    encouragement_phrases: List[str] = Field(None)
    config: PersonaConfig = Field(None)


class PersonaResponse(BaseModel):
    """人设响应"""
    id: int
    name: str
    type: str
    description: str
    tone: str
    focus_areas: List[str]
    questioning_style: str
    followup_frequency: str
    encouragement_level: str
    conversation_style: str
    personality_traits: List[str]
    question_templates: List[str]
    transition_phrases: List[str]
    feedback_phrases: List[str]
    encouragement_phrases: List[str]
    is_default: bool
    is_custom: bool
    config: dict
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


@router.get("", response_model=ApiResponse[List[PersonaResponse]])
async def list_personas(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """列出所有人设（包括系统预设和用户自定义）"""
    manager = PersonaManager(db)
    personas = await manager.list_personas(current_user.id)
    return ApiResponse(code=200, message="获取人设列表成功", data=personas)


@router.get("/default", response_model=ApiResponse[PersonaResponse])
async def get_default_persona(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """获取默认人设"""
    manager = PersonaManager(db)
    persona = await manager.get_default_persona()

    if not persona:
        # 如果没有默认人设，初始化预设人设
        await initialize_personas(db)
        persona = await manager.get_default_persona()

    if not persona:
        raise HTTPException(status_code=404, detail="默认人设不存在")

    return ApiResponse(code=200, message="获取默认人设成功", data=persona)


@router.get("/{persona_id}", response_model=ApiResponse[PersonaResponse])
async def get_persona(
    persona_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """获取人设详情"""
    manager = PersonaManager(db)
    persona = await manager.get_persona(persona_id)

    if not persona:
        raise HTTPException(status_code=404, detail="人设不存在")

    return ApiResponse(code=200, message="获取人设详情成功", data=persona)


@router.post("", response_model=ApiResponse[PersonaResponse])
async def create_persona(
    persona_data: PersonaCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """创建自定义人设"""
    manager = PersonaManager(db)
    persona = await manager.create_custom_persona(
        current_user.id,
        persona_data.dict()
    )
    return ApiResponse(code=201, message="创建人设成功", data=persona)


@router.put("/{persona_id}", response_model=ApiResponse[PersonaResponse])
async def update_persona(
    persona_id: int,
    persona_data: PersonaUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """更新自定义人设"""
    manager = PersonaManager(db)
    persona = await manager.update_persona(
        persona_id,
        current_user.id,
        persona_data.dict(exclude_unset=True)
    )

    if not persona:
        raise HTTPException(
            status_code=404,
            detail="人设不存在或无权修改"
        )

    return ApiResponse(code=200, message="更新人设成功", data=persona)


@router.delete("/{persona_id}", response_model=ApiResponse[None])
async def delete_persona(
    persona_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """删除自定义人设"""
    manager = PersonaManager(db)
    success = await manager.delete_persona(persona_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=404,
            detail="人设不存在或无权删除"
        )

    return ApiResponse(code=200, message="人设删除成功")


@router.post("/initialize", response_model=ApiResponse[None])
async def initialize_personas_endpoint(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """初始化预设人设"""
    await initialize_personas(db)
    return ApiResponse(code=200, message="预设人设初始化完成")