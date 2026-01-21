from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class UserLLMConfig(Base):
    """用户 LLM 配置表"""
    __tablename__ = "user_llm_configs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    provider = Column(String(100), nullable=False, comment="LLM 提供商，如 dashscope/qwen-turbo")
    model_name = Column(String(100), nullable=False, comment="模型名称")
    api_key = Column(Text, nullable=True, comment="加密存储的 API Key")
    api_base = Column(String(500), nullable=True, comment="自定义 API 端点")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    user = relationship("User", backref="llm_configs")