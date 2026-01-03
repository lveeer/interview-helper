from typing import Generic, TypeVar, Optional, Any, List
from pydantic import BaseModel

T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    """标准 API 响应格式"""
    code: int
    message: str
    data: Optional[T] = None


class ListResponse(BaseModel, Generic[T]):
    """列表响应格式"""
    code: int
    message: str
    data: List[T]
    total: int
    page: Optional[int] = None
    page_size: Optional[int] = None


class SuccessResponse(BaseModel):
    """操作成功响应"""
    code: int = 200
    message: str = "操作成功"


class ErrorResponse(BaseModel):
    """错误响应"""
    code: int
    message: str
    detail: Optional[str] = None