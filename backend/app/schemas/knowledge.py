from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime


class KnowledgeUpload(BaseModel):
    file_name: str


class KnowledgeDocumentResponse(BaseModel):
    id: int
    user_id: int
    file_name: str
    file_type: str
    category: str
    chunk_strategy: str
    created_at: datetime

    class Config:
        from_attributes = True


class KnowledgeQuery(BaseModel):
    query: str
    top_k: int = 5
    use_query_expansion: Optional[bool] = None  # 使用查询扩展
    use_hybrid_search: Optional[bool] = None  # 使用混合检索
    use_reranking: Optional[bool] = None  # 使用重排序


class DocumentPreviewResponse(BaseModel):
    content: str


class CategoryUpdateRequest(BaseModel):
    category: str

    @field_validator('category')
    @classmethod
    def validate_category(cls, v):
        valid_categories = ["技术文档", "面试题", "公司资料", "其他", ""]
        if v not in valid_categories:
            raise ValueError(f"分类必须是以下之一: {', '.join(valid_categories)}")
        return v


class QueryHistoryRequest(BaseModel):
    query: str


class ChunkStrategyRequest(BaseModel):
    chunk_strategy: str = "semantic"  # 默认语义分段

    @field_validator('chunk_strategy')
    @classmethod
    def validate_chunk_strategy(cls, v):
        valid_strategies = ["semantic", "parent_child", "recursive"]
        if v not in valid_strategies:
            raise ValueError(f"分段策略必须是以下之一: {', '.join(valid_strategies)}")
        return v


class ChunkStrategyUpdateRequest(BaseModel):
    chunk_strategy: str

    @field_validator('chunk_strategy')
    @classmethod
    def validate_chunk_strategy(cls, v):
        valid_strategies = ["semantic", "parent_child", "recursive"]
        if v not in valid_strategies:
            raise ValueError(f"分段策略必须是以下之一: {', '.join(valid_strategies)}")
        return v


class RecallTestCaseCreate(BaseModel):
    query: str
    expected_chunk_ids: List[int]
    description: Optional[str] = None


class RecallTestCaseResponse(BaseModel):
    id: int
    user_id: int
    query: str
    expected_chunk_ids: List[int]
    description: Optional[str]
    created_at: datetime

    @field_validator('expected_chunk_ids', mode='before')
    @classmethod
    def json_to_list(cls, v):
        if isinstance(v, str):
            import json
            return json.loads(v)
        return v

    class Config:
        from_attributes = True


class RecallTestRunRequest(BaseModel):
    test_case_id: int
    top_k: int = 5
    use_query_expansion: Optional[bool] = None
    use_hybrid_search: Optional[bool] = None
    use_reranking: Optional[bool] = None


class RecallTestResultResponse(BaseModel):
    id: int
    user_id: int
    test_case_id: int
    retrieved_chunk_ids: List[int]
    retrieved_scores: List[float]
    recall: int
    precision: int
    f1_score: int
    mrr: int
    use_query_expansion: bool
    use_hybrid_search: bool
    use_reranking: bool
    top_k: int
    created_at: datetime

    @field_validator('retrieved_chunk_ids', 'retrieved_scores', mode='before')
    @classmethod
    def json_to_list(cls, v):
        if isinstance(v, str):
            import json
            return json.loads(v)
        return v

    @field_validator('use_query_expansion', 'use_hybrid_search', 'use_reranking', mode='before')
    @classmethod
    def int_to_bool(cls, v):
        if isinstance(v, int):
            return bool(v)
        return v

    class Config:
        from_attributes = True


class RecallTestSummaryResponse(BaseModel):
    total_tests: int
    avg_recall: float
    avg_precision: float
    avg_f1_score: float
    avg_mrr: float
    results: List[RecallTestResultResponse]