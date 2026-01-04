from pydantic import BaseModel, field_validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
import json


class ResumeUpload(BaseModel):
    file_name: str


class ResumeParse(BaseModel):
    personal_info: Dict[str, Any]
    education: List[Dict[str, Any]]
    experience: List[Dict[str, Any]]
    skills: List[str]
    projects: List[Dict[str, Any]]
    highlights: List[str]


class ResumeResponse(BaseModel):
    id: int
    user_id: int
    file_name: str
    file_type: str
    personal_info: Optional[Dict[str, Any]] = None
    education: Optional[List[Dict[str, Any]]] = None
    experience: Optional[List[Dict[str, Any]]] = None
    skills: Optional[List[str]] = None
    projects: Optional[List[Dict[str, Any]]] = None
    highlights: Optional[List[str]] = None
    created_at: datetime

    @field_validator('personal_info', mode='before')
    @classmethod
    def parse_personal_info(cls, v: Optional[Union[str, Dict]]) -> Optional[Dict]:
        """解析个人信息的 JSON 字符串"""
        if v is None:
            return None
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return {}
        return v

    @field_validator('education', mode='before')
    @classmethod
    def parse_education(cls, v: Optional[Union[str, List]]) -> Optional[List]:
        """解析教育背景的 JSON 字符串"""
        if v is None:
            return None
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return []
        return v

    @field_validator('experience', mode='before')
    @classmethod
    def parse_experience(cls, v: Optional[Union[str, List]]) -> Optional[List]:
        """解析工作经历的 JSON 字符串"""
        if v is None:
            return None
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return []
        return v

    @field_validator('skills', mode='before')
    @classmethod
    def parse_skills(cls, v: Optional[Union[str, List]]) -> Optional[List]:
        """解析技能的 JSON 字符串"""
        if v is None:
            return None
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return []
        return v

    @field_validator('projects', mode='before')
    @classmethod
    def parse_projects(cls, v: Optional[Union[str, List]]) -> Optional[List]:
        """解析项目经历的 JSON 字符串"""
        if v is None:
            return None
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return []
        return v

    @field_validator('highlights', mode='before')
    @classmethod
    def parse_highlights(cls, v: Optional[Union[str, List]]) -> Optional[List]:
        """解析亮点的 JSON 字符串"""
        if v is None:
            return None
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return []
        return v

    class Config:
        from_attributes = True