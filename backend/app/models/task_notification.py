"""
任务通知历史记录模型
用于存储用户的任务通知历史，支持查看历史推送记录
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum
import json

from app.core.database import Base


class TaskType(str, enum.Enum):
    """任务类型"""
    INTERVIEW_GENERATION = "interview_generation"  # 面试问题生成
    RESUME_UPLOAD = "resume_upload"                # 简历上传
    RESUME_PARSE = "resume_parse"                  # 简历解析
    RESUME_OPTIMIZE = "resume_optimize"            # 简历优化
    KNOWLEDGE_UPLOAD = "knowledge_upload"          # 知识库文档上传
    EVALUATION_GENERATE = "evaluation_generate"    # 评估报告生成
    JOB_MATCH = "job_match"                        # 岗位匹配分析


class NotificationStatus(str, enum.Enum):
    """通知状态"""
    PENDING = "pending"       # 等待中
    SENT = "sent"            # 已发送
    READ = "read"            # 已读
    FAILED = "failed"        # 发送失败


class TaskNotification(Base):
    """任务通知历史记录"""
    __tablename__ = "task_notifications"

    id = Column(Integer, primary_key=True, index=True)
    
    # 用户关联
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    user = relationship("User", backref="notifications")
    
    # 任务信息
    task_id = Column(String(255), nullable=False, index=True)  # 任务唯一标识
    task_type = Column(SQLEnum(TaskType), nullable=False)
    task_title = Column(String(255), nullable=False)  # 任务标题（用于显示）
    
    # 通知内容
    status = Column(SQLEnum(NotificationStatus), default=NotificationStatus.PENDING)
    message = Column(Text, nullable=True)  # 通知消息
    notification_type = Column(String(50), nullable=True)  # 通知类型: success, error, info, warning
    
    # 任务结果
    result = Column(Text, nullable=True)  # 任务结果（JSON格式）
    error = Column(Text, nullable=True)   # 错误信息
    progress = Column(Integer, default=0)  # 进度百分比
    
    # 跳转信息
    redirect_url = Column(String(500), nullable=True)  # 跳转链接
    redirect_params = Column(Text, nullable=True)      # 跳转参数（JSON格式）
    
    # 元数据
    extra_data = Column(Text, nullable=True)  # 其他元数据（JSON格式）
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    read_at = Column(DateTime(timezone=True), nullable=True)  # 已读时间
    
    def __repr__(self):
        return f"<TaskNotification(id={self.id}, task_id={self.task_id}, task_type={self.task_type}, status={self.status})>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "task_id": self.task_id,
            "task_type": self.task_type,
            "task_title": self.task_title,
            "status": self.status,
            "message": self.message,
            "notification_type": self.notification_type,
            "result": json.loads(self.result) if self.result else None,
            "error": self.error,
            "progress": self.progress,
            "redirect_url": self.redirect_url,
            "redirect_params": json.loads(self.redirect_params) if self.redirect_params else None,
            "extra_data": json.loads(self.extra_data) if self.extra_data else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "read_at": self.read_at.isoformat() if self.read_at else None
        }