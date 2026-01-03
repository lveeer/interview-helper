from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
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

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", backref="resumes")