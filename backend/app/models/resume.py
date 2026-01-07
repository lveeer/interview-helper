from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(20))  # pdf, docx

    # 解析后的结构化数据
    personal_info = Column(Text)  # JSON 格式存储
    education = Column(Text)  # JSON 格式存储
    experience = Column(Text)  # JSON 格式存储
    skills = Column(Text)  # JSON 格式存储
    projects = Column(Text)  # JSON 格式存储
    highlights = Column(Text)  # JSON 格式存储

    # 版本控制
    current_version = Column(String(20), default="v1.0")

    # 优化分析结果缓存
    analysis_result = Column(Text)  # JSON 格式存储分析结果

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", backref="resumes")
    optimizations = relationship("ResumeOptimization", back_populates="resume", cascade="all, delete-orphan")
    optimization_history = relationship("ResumeOptimizationHistory", back_populates="resume", cascade="all, delete-orphan")


class ResumeOptimization(Base):
    """简历优化建议表"""
    __tablename__ = "resume_optimizations"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)

    # 优化建议内容
    priority = Column(String(20), nullable=False)  # high, medium, low
    title = Column(String(200), nullable=False)
    description = Column(Text)
    before = Column(Text)  # 优化前的内容
    after = Column(Text)  # 优化后的内容
    reason = Column(Text)  # 优化原因

    # 状态
    is_applied = Column(Boolean, default=False)

    # 创建时间
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    resume = relationship("Resume", back_populates="optimizations")


class ResumeOptimizationHistory(Base):
    """简历优化历史记录表"""
    __tablename__ = "resume_optimization_history"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)

    # 版本信息
    version = Column(String(20), nullable=False)
    version_before = Column(String(20))  # 优化前的版本
    version_after = Column(String(20))  # 优化后的版本

    # 操作信息
    title = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(String(20), default="success")  # success, failed

    # 变更内容
    changes = Column(JSON)  # 存储变更详情

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    resume = relationship("Resume", back_populates="optimization_history")