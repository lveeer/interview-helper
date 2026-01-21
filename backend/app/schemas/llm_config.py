from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class UserLLMConfigBase(BaseModel):
    """用户 LLM 配置基础模型"""
    provider: Optional[str] = Field("", description="LLM 提供商，如 dashscope/qwen-turbo")
    model_name: Optional[str] = Field("", description="模型名称")
    api_key: Optional[str] = Field(None, description="API Key")
    api_base: Optional[str] = Field(None, description="自定义 API 端点")
    is_active: bool = Field(True, description="是否启用")


class UserLLMConfigCreate(UserLLMConfigBase):
    """创建用户 LLM 配置"""
    pass


class UserLLMConfigUpdate(BaseModel):
    """更新用户 LLM 配置"""
    provider: Optional[str] = Field(None, description="LLM 提供商")
    model_name: Optional[str] = Field(None, description="模型名称")
    api_key: Optional[str] = Field(None, description="API Key")
    api_base: Optional[str] = Field(None, description="自定义 API 端点")
    is_active: Optional[bool] = Field(None, description="是否启用")


class UserLLMConfigResponse(UserLLMConfigBase):
    """用户 LLM 配置响应"""
    id: int
    user_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LLMConnectionTestRequest(BaseModel):
    """LLM 连接测试请求"""
    provider: str = Field(..., description="LLM 提供商，如 dashscope/qwen-turbo")
    model_name: str = Field(..., description="模型名称")
    api_key: Optional[str] = Field(None, description="API Key（可选，不填则使用全局配置）")
    api_base: Optional[str] = Field(None, description="自定义 API 端点（可选）")


class LLMConnectionTestResponse(BaseModel):
    """LLM 连接测试响应"""
    success: bool = Field(..., description="是否连接成功")
    message: str = Field(..., description="测试结果消息")
    latency_ms: Optional[float] = Field(None, description="延迟（毫秒）")
    error: Optional[str] = Field(None, description="错误信息")


class LLMProviderInfo(BaseModel):
    """LLM 提供商信息"""
    provider: str = Field(..., description="提供商标识")
    name: str = Field(..., description="提供商名称")
    models: list[str] = Field(..., description="支持的模型列表")
    description: str = Field(..., description="提供商描述")