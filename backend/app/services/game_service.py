import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from app.models.game import (
    ResumeFinderSession,
    UserPoints,
    UserAchievement,
    LeaderboardSnapshot
)
from app.models.user import User
from app.schemas.game import (
    Difficulty,
    GameStatus,
    Period,
    ErrorDetail,
    WeakPoint,
    AchievementInfo,
    RankingItem
)
from app.utils.prompt_loader import PromptLoader
logger = logging.getLogger(__name__)


class ResumeFinderService:
    """简历找茬游戏服务"""

    # 错误类型定义
    ERROR_TYPES = {
        "format_inconsistency": {
            "name": "格式不一致",
            "description": "日期、电话等格式不统一",
            "example": "2023.01 / 2023-01 混用",
            "correct": "统一使用 2023-01 格式",
            "tips": "检查所有日期格式是否一致"
        },
        "spacing_issue": {
            "name": "间距问题",
            "description": "段落间距不一致",
            "example": "项目描述间距混乱",
            "correct": "统一段落间距",
            "tips": "确保所有段落间距一致"
        },
        "vague_description": {
            "name": "描述空洞",
            "description": "缺乏量化数据",
            "example": "负责项目开发，提升了系统性能",
            "correct": "负责项目开发，优化数据库查询，将响应时间从2s降低到0.5s",
            "tips": "使用具体数字说明成果"
        },
        "missing_quantification": {
            "name": "缺少量化成果",
            "description": "没有具体数字",
            "example": "用户增长显著",
            "correct": "用户增长从1000提升到5000，增长率400%",
            "tips": "添加具体的数字指标"
        },
        "action_verb_weak": {
            "name": "动词力度弱",
            "description": "使用被动或弱动词",
            "example": "参与了项目",
            "correct": "主导了项目开发，协调5人团队完成交付",
            "tips": "使用强有力的主动动词"
        },
        "timeline_conflict": {
            "name": "时间线冲突",
            "description": "工作时间重叠",
            "example": "2020-2022在A公司，同时2021-2023在B公司",
            "correct": "2020-2021在A公司，2021-2023在B公司",
            "tips": "检查工作时间是否有重叠"
        },
        "negative_language": {
            "name": "负面语言",
            "description": "抱怨前公司或项目",
            "example": "前公司管理混乱，项目失败",
            "correct": "在充满挑战的环境中，通过优化流程提升了团队效率",
            "tips": "避免使用负面语言，用积极方式表达"
        }
    }

    # 成就定义
    ACHIEVEMENTS = {
        "first_find": {
            "name": "初露锋芒",
            "description": "第一次找到简历错误",
            "icon": "🔍",
            "condition": lambda stats: stats["total_found"] >= 1
        },
        "bug_hunter": {
            "name": "简历侦探",
            "description": "累计找到50个错误",
            "icon": "🕵️",
            "condition": lambda stats: stats["total_found"] >= 50
        },
        "perfectionist": {
            "name": "完美主义者",
            "description": "连续3局完美通关",
            "icon": "✨",
            "condition": lambda stats: stats.get("consecutive_perfect", 0) >= 3
        },
        "speed_demon": {
            "name": "闪电侠",
            "description": "困难模式快速通关",
            "icon": "⚡",
            "condition": lambda stats: stats.get("hard_best_time", 999) <= 30
        },
        "master": {
            "name": "简历大师",
            "description": "困难模式通关10次",
            "icon": "👑",
            "condition": lambda stats: stats.get("hard_wins", 0) >= 10
        },
        "streak_king": {
            "name": "连胜之王",
            "description": "连续获胜10次",
            "icon": "🏆",
            "condition": lambda stats: stats["current_streak"] >= 10
        },
        "night_owl": {
            "name": "夜猫子",
            "description": "凌晨玩游戏",
            "icon": "🦉",
            "condition": lambda stats: stats.get("night_games", 0) >= 1
        }
    }

    @staticmethod
    def _get_difficulty_config(difficulty: Difficulty) -> Dict[str, Any]:
        """获取难度配置"""
        configs = {
            Difficulty.easy: {
                "error_count": (3, 5),
                "time_limit": 180  # 3分钟
            },
            Difficulty.medium: {
                "error_count": (5, 8),
                "time_limit": 300  # 5分钟
            },
            Difficulty.hard: {
                "error_count": (8, 12),
                "time_limit": 480  # 8分钟
            }
        }
        return configs.get(difficulty, configs[Difficulty.medium])

    @staticmethod
    def _generate_sample_resume() -> Dict[str, Any]:
        """生成示例简历"""
        return {
            "personal_info": {
                "name": "张三",
                "email": "zhangsan@example.com",
                "phone": "13800138000",
                "location": "北京市"
            },
            "education": [
                {
                    "school": "清华大学",
                    "major": "计算机科学与技术",
                    "degree": "本科",
                    "start_date": "2018.09",
                    "end_date": "2022.06"
                }
            ],
            "experience": [
                {
                    "company": "某互联网公司",
                    "position": "后端开发工程师",
                    "start_date": "2022.07",
                    "end_date": "2024.12",
                    "description": "参与了项目开发，提升了系统性能，用户增长显著。"
                },
                {
                    "company": "另一家公司",
                    "position": "实习生",
                    "start_date": "2021.06",
                    "end_date": "2021.09",
                    "description": "负责项目测试，发现并修复了多个bug。"
                }
            ],
            "skills": [
                "Python",
                "Java",
                "MySQL",
                "Redis",
                "Docker"
            ],
            "projects": [
                {
                    "name": "电商系统",
                    "role": "后端开发",
                    "description": "负责后端接口开发，实现了用户管理、订单处理等功能。"
                }
            ]
        }

    @staticmethod
    def _generate_buggy_resume_fallback(difficulty: Difficulty) -> tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """降级方法：生成带错误的简历和错误列表（硬编码模板）"""
        resume = ResumeFinderService._generate_sample_resume()
        buggy_resume = json.loads(json.dumps(resume))  # 深拷贝
        errors = []

        # 根据难度生成不同数量的错误
        config = ResumeFinderService._get_difficulty_config(difficulty)
        min_errors, max_errors = config["error_count"]
        target_error_count = min_errors

        # 可用的错误类型
        available_error_types = list(ResumeFinderService.ERROR_TYPES.keys())

        # 生成错误
        error_id = 0
        for error_type in available_error_types:
            if error_id >= target_error_count:
                break

            error_info = ResumeFinderService.ERROR_TYPES[error_type]

            if error_type == "format_inconsistency":
                # 日期格式不一致
                buggy_resume["education"][0]["start_date"] = "2018-09"
                buggy_resume["education"][0]["end_date"] = "2022.06"
                buggy_resume["experience"][0]["start_date"] = "2022.07"
                buggy_resume["experience"][0]["end_date"] = "2024-12"
                errors.append({
                    "id": error_id,
                    "type": error_type,
                    "location": "education[0].start_date",
                    "hint": error_info["tips"],
                    "correct_text": "2018.09"
                })
                error_id += 1

            elif error_type == "vague_description":
                # 描述空洞
                buggy_resume["experience"][0]["description"] = "参与了项目开发，提升了系统性能，用户增长显著。"
                errors.append({
                    "id": error_id,
                    "type": error_type,
                    "location": "experience[0].description",
                    "hint": error_info["tips"],
                    "correct_text": "主导了后端系统开发，优化数据库查询，将响应时间从2s降低到0.5s，用户从10万增长到50万"
                })
                error_id += 1

            elif error_type == "missing_quantification":
                # 缺少量化成果
                buggy_resume["projects"][0]["description"] = "负责后端接口开发，实现了用户管理、订单处理等功能。"
                errors.append({
                    "id": error_id,
                    "type": error_type,
                    "location": "projects[0].description",
                    "hint": error_info["tips"],
                    "correct_text": "负责后端接口开发，实现了用户管理、订单处理等功能，支持日均10万订单，响应时间<200ms"
                })
                error_id += 1

            elif error_type == "action_verb_weak":
                # 动词力度弱
                buggy_resume["experience"][1]["description"] = "负责项目测试，发现并修复了多个bug。"
                errors.append({
                    "id": error_id,
                    "type": error_type,
                    "location": "experience[1].description",
                    "hint": error_info["tips"],
                    "correct_text": "主导项目测试，建立自动化测试体系，发现并修复50+个bug，测试覆盖率提升至90%"
                })
                error_id += 1

            elif error_type == "timeline_conflict":
                # 时间线冲突
                buggy_resume["experience"][0]["start_date"] = "2021.07"
                buggy_resume["experience"][0]["end_date"] = "2023.12"
                buggy_resume["experience"][1]["start_date"] = "2022.06"
                buggy_resume["experience"][1]["end_date"] = "2022.09"
                errors.append({
                    "id": error_id,
                    "type": error_type,
                    "location": "experience[1].start_date",
                    "hint": error_info["tips"],
                    "correct_text": "2021.06"
                })
                error_id += 1

            elif error_type == "negative_language":
                # 负面语言
                buggy_resume["experience"][0]["description"] = "前公司管理混乱，项目失败，但我努力完成了任务。"
                errors.append({
                    "id": error_id,
                    "type": error_type,
                    "location": "experience[0].description",
                    "hint": error_info["tips"],
                    "correct_text": "在资源有限的情况下，通过优化流程和团队协作，成功完成了项目交付"
                })
                error_id += 1

        return buggy_resume, errors

    @staticmethod
    async def _generate_buggy_resume(difficulty: Difficulty, db: AsyncSession) -> tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """使用 LLM 生成带错误的简历和错误列表"""
        # 根据难度生成不同数量的错误
        config = ResumeFinderService._get_difficulty_config(difficulty)
        min_errors, max_errors = config["error_count"]
        target_error_count = min_errors

        # 加载 prompt 模板
        prompt = PromptLoader.format_prompt(
            "buggy_resume_generation",
            difficulty=difficulty.value,
            error_count=target_error_count
        )

        try:
            # 获取用户的 LLM 服务
            from app.services.llm_service import get_user_llm_service
            llm_service = await get_user_llm_service(user_id=1, db=db)  # 使用默认用户 ID

            # 调用 LLM 生成简历
            response = await llm_service.generate_chat(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,  # 使用较高的温度以增加多样性
                max_tokens=4000,
                response_format={"type": "json_object"}
            )

            # 解析 LLM 返回的 JSON
            result = json.loads(response)

            buggy_resume = result.get("resume", {})
            errors = result.get("errors", [])

            # 验证返回的数据格式
            if not buggy_resume or not errors:
                raise ValueError("LLM 返回的数据格式不正确")

            # 确保 errors 列表中的每个错误都有必要的字段
            for i, error in enumerate(errors):
                if "id" not in error:
                    error["id"] = i
                if "type" not in error:
                    error["type"] = "unknown"
                if "location" not in error:
                    error["location"] = "unknown"
                if "hint" not in error:
                    error["hint"] = "请仔细检查这个位置"
                if "correct_text" not in error:
                    error["correct_text"] = ""

            return buggy_resume, errors

        except Exception as e:
            logger.error(f"LLM 生成简历失败: {e}", exc_info=True)
            # 如果 LLM 调用失败，降级使用硬编码模板
            logger.warning("降级使用硬编码模板生成简历")
            return ResumeFinderService._generate_buggy_resume_fallback(difficulty)

    @staticmethod
    async def start_game(
        user_id: int,
        difficulty: Difficulty,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """开始游戏"""
        # 使用 LLM 生成带错误的简历
        buggy_resume, errors = await ResumeFinderService._generate_buggy_resume(difficulty, db)

        # 获取难度配置
        config = ResumeFinderService._get_difficulty_config(difficulty)

        # 创建游戏会话
        session = ResumeFinderSession(
            user_id=user_id,
            difficulty=difficulty.value,
            buggy_resume=buggy_resume,
            errors=errors,
            status=GameStatus.in_progress.value,
            time_limit=config["time_limit"]
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)

        return {
            "session_id": session.id,
            "resume": buggy_resume,
            "error_count": len(errors),
            "time_limit": config["time_limit"],
            "started_at": session.started_at
        }

    @staticmethod
    async def submit_answer(
        session_id: int,
        location: str,
        user_id: int,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """提交答案"""
        # 获取游戏会话
        result = await db.execute(
            select(ResumeFinderSession).where(
                ResumeFinderSession.id == session_id,
                ResumeFinderSession.user_id == user_id
            )
        )
        session = result.scalar_one_or_none()

        if not session:
            raise ValueError("游戏会话不存在")

        if session.status != GameStatus.in_progress.value:
            raise ValueError("游戏已结束")

        errors = session.errors
        found_error_ids = session.buggy_resume.get("_found_errors", [])

        # 查找匹配的错误
        matched_error = None
        for error in errors:
            if error["id"] not in found_error_ids and error["location"] == location:
                matched_error = error
                break

        if matched_error:
            # 找到错误
            session.score += 10
            session.found_errors += 1
            found_error_ids.append(matched_error["id"])
            session.buggy_resume["_found_errors"] = found_error_ids

            await db.commit()
            await db.refresh(session)

            return {
                "is_correct": True,
                "error_detail": ErrorDetail(**matched_error),
                "score": session.score,
                "remaining_errors": len(errors) - session.found_errors
            }
        else:
            # 点错位置
            session.score = max(0, session.score - 5)
            await db.commit()
            await db.refresh(session)

            return {
                "is_correct": False,
                "error_detail": None,
                "score": session.score,
                "remaining_errors": len(errors) - session.found_errors
            }

    @staticmethod
    async def use_hint(
        session_id: int,
        user_id: int,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """使用提示"""
        # 获取游戏会话
        result = await db.execute(
            select(ResumeFinderSession).where(
                ResumeFinderSession.id == session_id,
                ResumeFinderSession.user_id == user_id
            )
        )
        session = result.scalar_one_or_none()

        if not session:
            raise ValueError("游戏会话不存在")

        if session.status != GameStatus.in_progress.value:
            raise ValueError("游戏已结束")

        if session.hints_used >= 3:
            raise ValueError("提示次数已用完")

        # 找到未发现的错误
        errors = session.errors
        found_error_ids = session.buggy_resume.get("_found_errors", [])
        remaining_errors = [e for e in errors if e["id"] not in found_error_ids]

        if not remaining_errors:
            raise ValueError("所有错误已找到")

        # 根据提示次数生成不同级别的提示
        hint_level = session.hints_used + 1
        error = remaining_errors[0]
        error_info = ResumeFinderService.ERROR_TYPES.get(error["type"], {})

        if hint_level == 1:
            hint = f"错误类型：{error_info.get('name', error['type'])}"
        elif hint_level == 2:
            hint = f"错误位置范围：{error['location']}"
        else:
            hint = f"错误位置：{error['location']}，建议修改为：{error['correct_text']}"

        # 更新提示次数和分数
        session.hints_used += 1
        session.score = max(0, session.score - 3)
        await db.commit()
        await db.refresh(session)

        return {
            "hint": hint,
            "remaining_hints": 3 - session.hints_used,
            "score": session.score
        }

    @staticmethod
    async def complete_game(
        session_id: int,
        user_id: int,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """完成游戏"""
        # 获取游戏会话
        result = await db.execute(
            select(ResumeFinderSession).where(
                ResumeFinderSession.id == session_id,
                ResumeFinderSession.user_id == user_id
            )
        )
        session = result.scalar_one_or_none()

        if not session:
            raise ValueError("游戏会话不存在")

        if session.status != GameStatus.in_progress.value:
            raise ValueError("游戏已结束")

        # 计算用时
        time_used = int((datetime.now() - session.started_at).total_seconds())
        session.time_used = time_used

        # 时间奖励
        if time_used <= 30:
            session.score += 20
        elif time_used <= 60:
            session.score += 10

        # 完美通关奖励
        errors = session.errors
        is_perfect = session.found_errors == len(errors) and session.hints_used == 0
        if is_perfect:
            session.score += 50

        # 更新游戏状态
        session.status = GameStatus.completed.value
        session.completed_at = datetime.now()

        await db.commit()
        await db.refresh(session)

        # 更新用户积分
        await ResumeFinderService._update_user_points(user_id, session, db)

        # 检查成就
        achievements = await ResumeFinderService._check_achievements(user_id, db)

        # 计算排名变化
        rank_change = await ResumeFinderService._calculate_rank_change(user_id, db)

        # 分类找到和未找到的错误
        found_error_ids = session.buggy_resume.get("_found_errors", [])
        found_errors = [e for e in errors if e["id"] in found_error_ids]
        missed_errors = [e for e in errors if e["id"] not in found_error_ids]

        return {
            "final_score": session.score,
            "found_errors": found_errors,
            "missed_errors": missed_errors,
            "time_used": time_used,
            "achievements_unlocked": achievements,
            "rank_change": rank_change
        }

    @staticmethod
    async def _update_user_points(
        user_id: int,
        session: ResumeFinderSession,
        db: AsyncSession
    ):
        """更新用户积分"""
        result = await db.execute(
            select(UserPoints).where(UserPoints.user_id == user_id)
        )
        user_points = result.scalar_one_or_none()

        if not user_points:
            user_points = UserPoints(user_id=user_id)
            db.add(user_points)

        # 更新积分
        user_points.total_score += session.score
        user_points.daily_score += session.score
        user_points.weekly_score += session.score
        user_points.monthly_score += session.score

        # 更新游戏统计
        user_points.total_games += 1
        user_points.total_found += session.found_errors

        # 更新最佳成绩
        if session.score > user_points.best_score:
            user_points.best_score = session.score

        if session.time_used < user_points.best_time or user_points.best_time == 0:
            user_points.best_time = session.time_used

        # 更新连胜
        errors = session.errors
        if session.found_errors == len(errors):
            user_points.current_streak += 1
            if user_points.current_streak > user_points.max_streak:
                user_points.max_streak = user_points.current_streak
        else:
            user_points.current_streak = 0

        user_points.last_played_at = datetime.now()

        await db.commit()

    @staticmethod
    async def _check_achievements(user_id: int, db: AsyncSession) -> List[AchievementInfo]:
        """检查成就"""
        # 获取用户统计
        result = await db.execute(
            select(UserPoints).where(UserPoints.user_id == user_id)
        )
        user_points = result.scalar_one_or_none()

        if not user_points:
            return []

        stats = {
            "total_found": user_points.total_found,
            "current_streak": user_points.current_streak,
            "hard_best_time": 999,
            "hard_wins": 0,
            "consecutive_perfect": 0,
            "night_games": 0
        }

        # 获取用户已获得的成就
        result = await db.execute(
            select(UserAchievement).where(UserAchievement.user_id == user_id)
        )
        existing_achievements = {a.achievement_id for a in result.scalars().all()}

        # 检查新成就
        new_achievements = []
        for achievement_id, achievement_info in ResumeFinderService.ACHIEVEMENTS.items():
            if achievement_id not in existing_achievements:
                if achievement_info["condition"](stats):
                    # 解锁成就
                    new_achievement = UserAchievement(
                        user_id=user_id,
                        achievement_id=achievement_id
                    )
                    db.add(new_achievement)
                    new_achievements.append(AchievementInfo(
                        id=achievement_id,
                        name=achievement_info["name"],
                        icon=achievement_info["icon"]
                    ))

        if new_achievements:
            await db.commit()

        return new_achievements

    @staticmethod
    async def _calculate_rank_change(user_id: int, db: AsyncSession) -> Optional[str]:
        """计算排名变化"""
        # 简化实现，实际应该比较前后排名
        return "+3"

    @staticmethod
    async def get_user_stats(user_id: int, db: AsyncSession) -> Dict[str, Any]:
        """获取用户统计"""
        result = await db.execute(
            select(UserPoints).where(UserPoints.user_id == user_id)
        )
        user_points = result.scalar_one_or_none()

        if not user_points:
            return {
                "total_games": 0,
                "total_found": 0,
                "total_score": 0,
                "win_rate": 0.0,
                "best_time": 0,
                "current_streak": 0,
                "max_streak": 0,
                "weak_points": []
            }

        # 计算胜率
        win_rate = 0.0
        if user_points.total_games > 0:
            completed_result = await db.execute(
                select(func.count(ResumeFinderSession.id)).where(
                    ResumeFinderSession.user_id == user_id,
                    ResumeFinderSession.status == GameStatus.completed.value
                )
            )
            completed_count = completed_result.scalar() or 0
            win_rate = completed_count / user_points.total_games

        # 分析薄弱环节（简化实现）
        weak_points = []

        return {
            "total_games": user_points.total_games,
            "total_found": user_points.total_found,
            "total_score": user_points.total_score,
            "win_rate": round(win_rate, 2),
            "best_time": user_points.best_time,
            "current_streak": user_points.current_streak,
            "max_streak": user_points.max_streak,
            "weak_points": weak_points
        }

    @staticmethod
    async def get_leaderboard(
        period: Period,
        limit: int,
        user_id: Optional[int],
        db: AsyncSession
    ) -> Dict[str, Any]:
        """获取排行榜"""
        # 根据周期选择排序字段
        score_field = UserPoints.total_score
        if period == Period.daily:
            score_field = UserPoints.daily_score
        elif period == Period.weekly:
            score_field = UserPoints.weekly_score
        elif period == Period.monthly:
            score_field = UserPoints.monthly_score

        # 查询排行榜
        result = await db.execute(
            select(UserPoints, User)
            .join(User, UserPoints.user_id == User.id)
            .order_by(score_field.desc())
            .limit(limit)
        )

        rankings = []
        for rank, (user_points, user) in enumerate(result.all(), 1):
            rankings.append(RankingItem(
                rank=rank,
                user_id=user.id,
                username=user.username,
                score=getattr(user_points, score_field.key)
            ))

        # 获取当前用户排名
        my_rank = None
        my_score = None
        if user_id:
            # 简化实现
            result = await db.execute(
                select(UserPoints).where(UserPoints.user_id == user_id)
            )
            user_points = result.scalar_one_or_none()
            if user_points:
                my_score = getattr(user_points, score_field.key)

        return {
            "period": period.value,
            "rankings": rankings,
            "my_rank": my_rank,
            "my_score": my_score
        }

    @staticmethod
    async def get_achievements(user_id: int, db: AsyncSession) -> Dict[str, Any]:
        """获取成就列表"""
        # 获取用户已获得的成就
        result = await db.execute(
            select(UserAchievement).where(UserAchievement.user_id == user_id)
        )
        existing_achievements = {a.achievement_id: a.earned_at for a in result.scalars().all()}

        # 获取用户统计
        result = await db.execute(
            select(UserPoints).where(UserPoints.user_id == user_id)
        )
        user_points = result.scalar_one_or_none()

        stats = {
            "total_found": user_points.total_found if user_points else 0,
            "current_streak": user_points.current_streak if user_points else 0,
            "hard_best_time": 999,
            "hard_wins": 0,
            "consecutive_perfect": 0,
            "night_games": 0
        }

        # 构建成就列表
        achievements = []
        for achievement_id, achievement_info in ResumeFinderService.ACHIEVEMENTS.items():
            is_unlocked = achievement_id in existing_achievements
            achievement_item = {
                "id": achievement_id,
                "name": achievement_info["name"],
                "description": achievement_info["description"],
                "icon": achievement_info["icon"],
                "unlocked": is_unlocked,
                "unlocked_at": existing_achievements.get(achievement_id) if is_unlocked else None
            }

            # 添加进度信息
            if not is_unlocked and achievement_id == "bug_hunter":
                achievement_item["progress"] = stats["total_found"]
                achievement_item["total"] = 50
            elif not is_unlocked and achievement_id == "streak_king":
                achievement_item["progress"] = stats["current_streak"]
                achievement_item["total"] = 10

            achievements.append(achievement_item)

        return {
            "total": len(ResumeFinderService.ACHIEVEMENTS),
            "unlocked": len(existing_achievements),
            "achievements": achievements
        }

    @staticmethod
    async def get_error_types() -> Dict[str, Any]:
        """获取错误类型列表"""
        error_types = []
        for type_id, info in ResumeFinderService.ERROR_TYPES.items():
            error_types.append({
                "type_id": type_id,
                "name": info["name"],
                "description": info["description"],
                "example": info["example"],
                "correct": info["correct"],
                "tips": info["tips"]
            })

        return {"error_types": error_types}


# 创建服务实例
game_service = ResumeFinderService()