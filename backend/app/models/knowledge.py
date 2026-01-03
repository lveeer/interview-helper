from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, ARRAY, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(20))
    content = Column(Text)
    meta_info = Column(Text)  # JSON 格式存储额外元数据

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="knowledge_documents")


class VectorChunk(Base):
    __tablename__ = "vector_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("knowledge_documents.id"), nullable=False)
    chunk_text = Column(Text, nullable=False)
    embedding = Column(ARRAY(Float))  # pgvector 存储
    chunk_index = Column(Integer)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    document = relationship("KnowledgeDocument", backref="chunks")