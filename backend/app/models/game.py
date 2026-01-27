from sqlalchemy import Column, Integer, String, DateTime, JSON, Date
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class ResumeFinderSession(Base):
    """简历找茬游戏会话表"""
    __tablename__ = "resume_finder_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    difficulty = Column(String(20), nullable=False)  # easy/medium/hard
    buggy_resume = Column(JSON, nullable=False)  # 带错误的简历
    errors = Column(JSON, nullable=False)  # 错误列表
    status = Column(String(20), default='in_progress', index=True)  # in_progress/completed/abandoned
    score = Column(Integer, default=0)
    found_errors = Column(Integer, default=0)
    hints_used = Column(Integer, default=0)
    time_limit = Column(Integer, nullable=False)
    time_used = Column(Integer, default=0)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class UserPoints(Base):
    """用户积分表"""
    __tablename__ = "user_points"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, nullable=False)
    total_score = Column(Integer, default=0)
    daily_score = Column(Integer, default=0)
    weekly_score = Column(Integer, default=0)
    monthly_score = Column(Integer, default=0)
    total_games = Column(Integer, default=0)
    total_found = Column(Integer, default=0)
    best_score = Column(Integer, default=0)
    best_time = Column(Integer, default=0)
    current_streak = Column(Integer, default=0)
    max_streak = Column(Integer, default=0)
    last_played_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class UserAchievement(Base):
    """用户成就表"""
    __tablename__ = "user_achievements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    achievement_id = Column(String(50), nullable=False)
    earned_at = Column(DateTime(timezone=True), server_default=func.now())


class LeaderboardSnapshot(Base):
    """排行榜快照表"""
    __tablename__ = "leaderboard_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    period = Column(String(20), nullable=False)  # daily/weekly/monthly
    snapshot_date = Column(Date, nullable=False)
    rankings = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())