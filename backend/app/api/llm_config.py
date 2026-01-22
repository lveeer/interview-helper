from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.core.database import get_async_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.llm_config import UserLLMConfig
from app.schemas.llm_config import (
    UserLLMConfigCreate,
    UserLLMConfigUpdate,
    UserLLMConfigResponse,
    LLMConnectionTestRequest,
    LLMConnectionTestResponse,
    LLMProviderInfo
)
from app.schemas.common import ApiResponse
from app.services.llm_service import (
    encrypt_api_key,
    decrypt_api_key,
    test_llm_connection
)

router = APIRouter(prefix="/api/llm-config", tags=["LLM配置管理"])


@router.get("/", response_model=ApiResponse[UserLLMConfigResponse])
async def get_llm_config(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """获取当前用户的 LLM 配置"""
    result = await db.execute(
        select(UserLLMConfig)
        .where(UserLLMConfig.user_id == current_user.id)
        .order_by(UserLLMConfig.created_at.desc())
    )
    config = result.scalar_one_or_none()

    if not config:
        return ApiResponse(
            code=200,
            message="获取成功",
            data={
                "id": 0,
                "user_id": current_user.id,
                "provider": "",
                "model_name": "",
                "api_key": None,
                "api_base": None,
                "is_active": False,
                "created_at": None,
                "updated_at": None
            }
        )

    # 解密 API Key
    config_dict = {
        "id": config.id,
        "user_id": config.user_id,
        "provider": config.provider,
        "model_name": config.model_name,
        "api_key": decrypt_api_key(config.api_key) if config.api_key else None,
        "api_base": config.api_base,
        "is_active": config.is_active,
        "created_at": config.created_at,
        "updated_at": config.updated_at
    }

    return ApiResponse(
        code=200,
        message="获取成功",
        data=config_dict
    )


@router.post("/", response_model=ApiResponse[UserLLMConfigResponse], status_code=status.HTTP_201_CREATED)
async def create_llm_config(
    config_data: UserLLMConfigCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """创建 LLM 配置"""
    # 检查是否已存在配置
    result = await db.execute(
        select(UserLLMConfig).where(UserLLMConfig.user_id == current_user.id)
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您已存在 LLM 配置，请使用更新接口"
        )

    # 加密 API Key
    encrypted_key = encrypt_api_key(config_data.api_key) if config_data.api_key else None

    # 创建配置
    new_config = UserLLMConfig(
        user_id=current_user.id,
        provider=config_data.provider,
        model_name=config_data.model_name,
        api_key=encrypted_key,
        api_base=config_data.api_base,
        is_active=config_data.is_active
    )

    db.add(new_config)
    await db.commit()
    await db.refresh(new_config)

    # 解密返回
    new_config.api_key = decrypt_api_key(new_config.api_key) if new_config.api_key else None

    return ApiResponse(
        code=201,
        message="创建成功",
        data=UserLLMConfigResponse.model_validate(new_config)
    )


@router.put("/", response_model=ApiResponse[UserLLMConfigResponse])
async def update_llm_config(
    config_data: UserLLMConfigUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """更新 LLM 配置"""
    result = await db.execute(
        select(UserLLMConfig).where(UserLLMConfig.user_id == current_user.id)
    )
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到 LLM 配置"
        )

    # 更新字段
    if config_data.provider is not None:
        config.provider = config_data.provider
    if config_data.model_name is not None:
        config.model_name = config_data.model_name
    if config_data.api_key is not None:
        config.api_key = encrypt_api_key(config_data.api_key)
    if config_data.api_base is not None:
        config.api_base = config_data.api_base
    if config_data.is_active is not None:
        config.is_active = config_data.is_active

    await db.commit()
    await db.refresh(config)

    # 解密返回
    config.api_key = decrypt_api_key(config.api_key) if config.api_key else None

    return ApiResponse(
        code=200,
        message="更新成功",
        data=UserLLMConfigResponse.model_validate(config)
    )


@router.delete("/", response_model=ApiResponse[None])
async def delete_llm_config(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """删除 LLM 配置（回退到全局配置）"""
    result = await db.execute(
        select(UserLLMConfig).where(UserLLMConfig.user_id == current_user.id)
    )
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到 LLM 配置"
        )

    await db.delete(config)
    await db.commit()

    return ApiResponse(
        code=200,
        message="删除成功",
        data=None
    )


@router.post("/test-connection", response_model=ApiResponse[LLMConnectionTestResponse])
async def test_connection(
    test_request: LLMConnectionTestRequest,
    current_user: User = Depends(get_current_user)
):
    """测试 LLM 连接"""
    result = await test_llm_connection(
        provider=test_request.provider,
        model_name=test_request.model_name,
        api_key=test_request.api_key,
        api_base=test_request.api_base
    )

    return ApiResponse(
        code=200,
        message="测试完成",
        data=LLMConnectionTestResponse(**result)
    )


@router.get("/providers", response_model=ApiResponse[List[LLMProviderInfo]])
async def get_supported_providers():
    """获取支持的 LLM 提供商列表"""
    providers = [
        LLMProviderInfo(
            provider="dashscope",
            name="通义千问",
            models=[
                "qwen3-max",
                "qwen3-max-longcontext",
                "qwen3-plus",
                "qwen3-turbo",
                "qwen3-vl-plus",
                "qwen3-vl-max",
                "qwen3-coder-plus",
                "qwen3-math-plus",
                "qwen2.5-turbo",
                "qwen2.5-plus",
                "qwen2.5-max",
                "qwen2.5-max-longcontext"
            ],
            description="阿里云通义千问大模型（Qwen3 系列，支持思考模式）"
        ),
        LLMProviderInfo(
            provider="ernie",
            name="文心一言",
            models=[
                "ernie-bot-4",
                "ernie-bot-4-turbo",
                "ernie-bot-3.5",
                "ernie-bot-turbo",
                "ernie-speed",
                "ernie-lite",
                "ernie-vision",
                "ernie-function"
            ],
            description="百度文心一言大模型"
        ),
        LLMProviderInfo(
            provider="openai",
            name="OpenAI",
            models=[
                "gpt-4o",
                "gpt-4o-mini",
                "gpt-4-turbo",
                "gpt-3.5-turbo",
                "o1-preview",
                "o1-mini",
                "o3-mini"
            ],
            description="OpenAI GPT 系列"
        ),
        LLMProviderInfo(
            provider="anthropic",
            name="Anthropic",
            models=[
                "claude-3.5-sonnet",
                "claude-3.5-haiku",
                "claude-3-opus",
                "claude-3-sonnet",
                "claude-3-haiku"
            ],
            description="Anthropic Claude 系列"
        ),
        LLMProviderInfo(
            provider="ollama",
            name="Ollama",
            models=[
                "qwen2.5",
                "qwen2.5-coder",
                "qwen3",
                "llama3.2",
                "llama3.1",
                "deepseek-v3",
                "deepseek-r1",
                "phi-3",
                "gemma2"
            ],
            description="本地部署的开源模型"
        ),
        LLMProviderInfo(
            provider="zhipuai",
            name="智谱 AI",
            models=[
                "glm-4.7",
                "glm-4-plus",
                "glm-4-air",
                "glm-4-flash",
                "glm-4v",
                "glm-z1-air",
                "glm-z1-airx",
                "glm-z1-flash"
            ],
            description="智谱 AI GLM 系列（GLM-4.7 支持思考模式）"
        ),
        LLMProviderInfo(
            provider="deepseek",
            name="DeepSeek",
            models=[
                "deepseek-v3.2",
                "deepseek-v3.1",
                "deepseek-v3.1-terminus",
                "deepseek-v3-0324",
                "deepseek-r1-0528",
                "deepseek-chat",
                "deepseek-coder"
            ],
            description="DeepSeek 深度求索模型（V3.2 支持 GPT-5 水平推理）"
        ),
        LLMProviderInfo(
            provider="moonshot",
            name="Moonshot AI",
            models=[
                "kimi-k2",
                "kimi-k2-turbo-preview",
                "kimi-k2-thinking",
                "kimi-latest",
                "kimi-thinking-preview",
                "moonshot-v1-8k",
                "moonshot-v1-32k",
                "moonshot-v1-128k"
            ],
            description="Moonshot AI Kimi 系列（K2 模型 1T 参数 MoE 架构）"
        )
    ]

    return ApiResponse(
        code=200,
        message="获取成功",
        data=providers
    )