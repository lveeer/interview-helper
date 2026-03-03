"""面试官人设模型"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class InterviewerPersona(Base):
    """面试官人设表"""
    __tablename__ = "interviewer_personas"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="人设名称")
    type = Column(String(50), nullable=False, comment="人设类型")
    description = Column(Text, comment="人设描述")
    tone = Column(String(50), comment="语气风格")
    focus_areas = Column(JSON, default=list, comment="关注重点")
    questioning_style = Column(String(50), comment="提问风格")
    followup_frequency = Column(String(20), comment="追问频率")
    encouragement_level = Column(String(20), comment="鼓励程度")
    conversation_style = Column(String(50), comment="对话风格")
    personality_traits = Column(JSON, default=list, comment="个性特征")
    question_templates = Column(JSON, default=list, comment="问题模板")
    transition_phrases = Column(JSON, default=list, comment="过渡语句")
    feedback_phrases = Column(JSON, default=list, comment="反馈语句")
    encouragement_phrases = Column(JSON, default=list, comment="鼓励语句")
    is_default = Column(Boolean, default=False, comment="是否默认")
    is_custom = Column(Boolean, default=False, comment="是否自定义")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="创建用户ID")
    config = Column(JSON, default=dict, comment="人设配置")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", backref="custom_personas")


class PersonaConversationContext(Base):
    """人设对话上下文表"""
    __tablename__ = "persona_conversation_contexts"

    id = Column(Integer, primary_key=True, index=True)
    persona_id = Column(Integer, ForeignKey("interviewer_personas.id"), comment="人设ID")
    interview_id = Column(Integer, ForeignKey("interviews.id"), unique=True, comment="面试ID")
    user_id = Column(Integer, ForeignKey("users.id"), comment="用户ID")
    conversation_history = Column(JSON, default=list, comment="对话历史")
    current_mood = Column(String(50), default="neutral", comment="当前情绪")
    user_satisfaction = Column(Integer, default=50, comment="用户满意度 (0-100)")
    adjustment_history = Column(JSON, default=list, comment="调整历史")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    persona = relationship("InterviewerPersona")
    interview = relationship("Interview")
    user = relationship("User")