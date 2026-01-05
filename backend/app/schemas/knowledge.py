from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class KnowledgeUpload(BaseModel):
    file_name: str


class KnowledgeDocumentResponse(BaseModel):
    id: int
    user_id: int
    file_name: str
    file_type: str
    created_at: datetime

    class Config:
        from_attributes = True


class KnowledgeQuery(BaseModel):
    query: str
    top_k: int = 5
    use_query_expansion: Optional[bool] = None  # 使用查询扩展
    use_hybrid_search: Optional[bool] = None  # 使用混合检索
    use_reranking: Optional[bool] = None  # 使用重排序