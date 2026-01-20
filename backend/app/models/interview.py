from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class InterviewStatus(str, enum.Enum):
    initializing = "initializing"
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"


class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    job_description = Column(Text)  # JD

    status = Column(Enum(InterviewStatus), default=InterviewStatus.pending)
    total_score = Column(Integer, default=0)

    # 面试问题（JSON 格式）
    questions = Column(Text)
    # 面试对话记录（JSON 格式）
    conversation = Column(Text)

    # 评估报告（JSON 格式）
    evaluation_report = Column(Text, nullable=True)
    # 评估报告生成时间
    evaluation_generated_at = Column(DateTime(timezone=True), nullable=True)

    # 问题生成错误信息（JSON 格式）
    generation_error = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", backref="interviews")
    resume = relationship("Resume", back_populates="interviews", passive_deletes='all')