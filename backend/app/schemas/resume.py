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
    skills_raw: List[str] = []
    projects: List[Dict[str, Any]]
    highlights: List[str]


class ResumeListItem(BaseModel):
    """简历列表项 - 轻量级响应模型"""
    id: int
    file_name: str
    file_type: str
    created_at: datetime

    class Config:
        from_attributes = True


class ResumeResponse(BaseModel):
    id: int
    user_id: int
    file_name: str
    file_type: str
    personal_info: Optional[Dict[str, Any]] = None
    education: Optional[List[Dict[str, Any]]] = None
    experience: Optional[List[Dict[str, Any]]] = None
    skills: Optional[List[str]] = None
    skills_raw: Optional[List[str]] = None
    projects: Optional[List[Dict[str, Any]]] = None
    highlights: Optional[List[str]] = None
    current_version: Optional[str] = None
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

    @field_validator('skills_raw', mode='before')
    @classmethod
    def parse_skills_raw(cls, v: Optional[Union[str, List]]) -> Optional[List]:
        """解析专业技能原始内容的 JSON 字符串"""
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


# 简历分析相关 Schema
class PersonalAnalysis(BaseModel):
    status: str
    message: str
    included: List[str] = []
    missing: List[str] = []


class EducationAnalysis(BaseModel):
    status: str
    message: str
    suggestions: Optional[str] = None


class ExperienceAnalysis(BaseModel):
    status: str
    message: str
    issues: Optional[str] = None
    suggestions: Optional[str] = None


class SkillsAnalysis(BaseModel):
    status: str
    message: str
    hard_skills: List[str] = []
    soft_skills: List[str] = []
    suggestions: Optional[str] = None


class ResumeAnalysisResult(BaseModel):
    overall_score: int
    content_score: int
    match_score: int
    clarity_score: int
    strengths: List[str]
    weaknesses: List[str]
    personal_analysis: PersonalAnalysis
    education_analysis: EducationAnalysis
    experience_analysis: ExperienceAnalysis
    skills_analysis: SkillsAnalysis


# 简历优化建议相关 Schema
class OptimizationSuggestion(BaseModel):
    id: int
    priority: str  # high, medium, low
    title: str
    description: str
    before: Optional[str] = None
    after: Optional[str] = None
    reason: Optional[str] = None


class OptimizationSuggestionCreate(BaseModel):
    id: int
    priority: str
    title: str
    description: str
    before: Optional[str] = None
    after: Optional[str] = None
    reason: Optional[str] = None


class OptimizationApplyRequest(BaseModel):
    suggestions: List[OptimizationSuggestionCreate]
    jd: Optional[str] = None  # 可选的职位描述（Job Description），用于针对性优化


class OptimizationApplyResponse(BaseModel):
    version: str
    optimized_at: datetime
    applied_count: int


# 简历优化历史相关 Schema
class OptimizationHistoryItem(BaseModel):
    id: int
    version: str
    version_before: Optional[str] = None
    version_after: Optional[str] = None
    title: str
    description: Optional[str] = None
    status: str
    created_at: datetime


# 简历版本比较相关 Schema
class DiffItem(BaseModel):
    type: str  # added, deleted, modified
    section: str
    content: Dict[str, Any]


class ResumeCompareResult(BaseModel):
    before: str
    after: str
    diff: List[DiffItem]


# 简历恢复相关 Schema
class ResumeRestoreRequest(BaseModel):
    version: str


class ResumeRestoreResponse(BaseModel):
    version: str
    restored_at: datetime