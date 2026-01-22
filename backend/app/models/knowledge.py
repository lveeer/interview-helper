from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
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
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    chunk_count = Column(Integer, default=0)
    error_message = Column(Text)
    category = Column(String(50), default="")  # 文档分类：技术文档、面试题、公司资料、其他、空字符串
    chunk_strategy = Column(String(50), default="semantic")  # 分段策略：semantic(语义分段), parent_child(父子分段), recursive(递归分段)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="knowledge_documents")


class VectorChunk(Base):
    __tablename__ = "vector_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("knowledge_documents.id"), nullable=False)
    chunk_text = Column(Text, nullable=False)
    embedding = Column(Vector(1024))  # pgvector 存储
    chunk_index = Column(Integer)
    parent_chunk_id = Column(Integer, ForeignKey("vector_chunks.id"), nullable=True)  # 父块 ID，用于父子分段

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    document = relationship("KnowledgeDocument", backref="chunks")
    parent_chunk = relationship("VectorChunk", remote_side=[id], backref="child_chunks")


class QueryHistory(Base):
    __tablename__ = "query_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    query_text = Column(String(500), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="query_history")


class RecallTestCase(Base):
    __tablename__ = "recall_test_cases"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    query = Column(Text, nullable=False)
    expected_chunk_ids = Column(Text, nullable=False)  # JSON 格式存储期望的分段 ID 列表
    description = Column(Text)  # 测试用例描述
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="recall_test_cases")


class RecallTestResult(Base):
    __tablename__ = "recall_test_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    test_case_id = Column(Integer, ForeignKey("recall_test_cases.id"), nullable=False)
    retrieved_chunk_ids = Column(Text, nullable=False)  # JSON 格式存储实际召回的分段 ID 列表
    retrieved_scores = Column(Text, nullable=False)  # JSON 格式存储召回分数列表
    recall = Column(Integer)  # 召回率（百分比）
    precision = Column(Integer)  # 精确率（百分比）
    f1_score = Column(Integer)  # F1 分数（百分比）
    mrr = Column(Integer)  # 平均倒数排名（百分比）
    use_query_expansion = Column(Integer)  # 是否使用查询扩展（0/1）
    use_hybrid_search = Column(Integer)  # 是否使用混合检索（0/1）
    use_reranking = Column(Integer)  # 是否使用重排序（0/1）
    top_k = Column(Integer)  # 召回数量
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="recall_test_results")
    test_case = relationship("RecallTestCase", backref="test_results")