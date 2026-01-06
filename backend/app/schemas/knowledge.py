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