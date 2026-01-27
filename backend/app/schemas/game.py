from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class Difficulty(str, Enum):
    """游戏难度"""
    easy = "easy"
    medium = "medium"
    hard = "hard"


class GameStatus(str, Enum):
    """游戏状态"""
    in_progress = "in_progress"
    completed = "completed"
    abandoned = "abandoned"


class Period(str, Enum):
    """排行榜周期"""
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    all = "all"


# ============ 游戏会话相关 ============

class GameStartRequest(BaseModel):
    """开始游戏请求"""
    difficulty: Difficulty


class ErrorDetail(BaseModel):
    """错误详情"""
    id: int
    type: str
    location: str
    hint: str
    correct_text: str


class GameStartResponse(BaseModel):
    """开始游戏响应"""
    session_id: int
    resume: Dict[str, Any]
    error_count: int
    time_limit: int
    started_at: datetime


class AnswerSubmitRequest(BaseModel):
    """提交答案请求"""
    session_id: int
    location: str


class AnswerSubmitResponse(BaseModel):
    """提交答案响应"""
    is_correct: bool
    error_detail: Optional[ErrorDetail] = None
    score: int
    remaining_errors: int


class HintRequest(BaseModel):
    """使用提示请求"""
    session_id: int


class HintResponse(BaseModel):
    """使用提示响应"""
    hint: str
    remaining_hints: int
    score: int


class GameCompleteRequest(BaseModel):
    """完成游戏请求"""
    session_id: int


class AchievementInfo(BaseModel):
    """成就信息"""
    id: str
    name: str
    icon: str


class GameCompleteResponse(BaseModel):
    """完成游戏响应"""
    final_score: int
    found_errors: List[Dict[str, Any]]
    missed_errors: List[Dict[str, Any]]
    time_used: int
    achievements_unlocked: List[AchievementInfo]
    rank_change: Optional[str] = None


# ============ 统计相关 ============

class WeakPoint(BaseModel):
    """薄弱环节"""
    type: str
    detection_rate: float
    suggestion: str


class UserStatsResponse(BaseModel):
    """用户统计响应"""
    total_games: int
    total_found: int
    total_score: int
    win_rate: float
    best_time: int
    current_streak: int
    max_streak: int
    weak_points: List[WeakPoint]


# ============ 排行榜相关 ============

class RankingItem(BaseModel):
    """排行榜项"""
    rank: int
    user_id: int
    username: str
    score: int
    avatar: Optional[str] = None


class LeaderboardResponse(BaseModel):
    """排行榜响应"""
    period: str
    rankings: List[RankingItem]
    my_rank: Optional[int] = None
    my_score: Optional[int] = None


# ============ 成就相关 ============

class AchievementItem(BaseModel):
    """成就项"""
    id: str
    name: str
    description: str
    icon: str
    unlocked: bool
    unlocked_at: Optional[datetime] = None
    progress: Optional[int] = None
    total: Optional[int] = None


class AchievementsResponse(BaseModel):
    """成就列表响应"""
    total: int
    unlocked: int
    achievements: List[AchievementItem]


# ============ 错误类型学习相关 ============

class ErrorTypeItem(BaseModel):
    """错误类型项"""
    type_id: str
    name: str
    description: str
    example: str
    correct: str
    tips: str


class ErrorTypesResponse(BaseModel):
    """错误类型列表响应"""
    error_types: List[ErrorTypeItem]


# ============ 游戏会话详情 ============

class GameSessionDetail(BaseModel):
    """游戏会话详情"""
    id: int
    user_id: int
    difficulty: str
    buggy_resume: Dict[str, Any]
    errors: List[Dict[str, Any]]
    status: str
    score: int
    found_errors: int
    hints_used: int
    time_limit: int
    time_used: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True