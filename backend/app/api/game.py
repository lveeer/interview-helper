from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_async_db
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.game import (
    GameStartRequest,
    GameStartResponse,
    AnswerSubmitRequest,
    AnswerSubmitResponse,
    HintRequest,
    HintResponse,
    GameCompleteRequest,
    GameCompleteResponse,
    UserStatsResponse,
    LeaderboardResponse,
    AchievementsResponse,
    ErrorTypesResponse,
    Period
)
from app.api.auth import get_current_user
from app.services.game_service import game_service

router = APIRouter(prefix="/game/resume-finder", tags=["游戏"])


@router.post("/start", response_model=ApiResponse[GameStartResponse])
async def start_game(
    request: GameStartRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    开始简历找茬游戏

    **请求参数：**
    - difficulty: 难度级别（easy/medium/hard）

    **响应内容：**
    - session_id: 游戏会话ID
    - resume: 带错误的简历数据
    - error_count: 错误总数
    - time_limit: 时间限制（秒）
    - started_at: 开始时间

    **业务规则：**
    - 简单模式：3-5个错误，时间限制3分钟
    - 中等模式：5-8个错误，时间限制5分钟
    - 困难模式：8-12个错误，时间限制8分钟
    """
    try:
        result = await game_service.start_game(
            user_id=current_user.id,
            difficulty=request.difficulty,
            db=db
        )
        return ApiResponse(
            code=200,
            message="游戏创建成功",
            data=GameStartResponse(**result)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/submit", response_model=ApiResponse[AnswerSubmitResponse])
async def submit_answer(
    request: AnswerSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    提交答案

    **请求参数：**
    - session_id: 游戏会话ID
    - location: 点击位置（如：experience[1].description）

    **响应内容：**
    - is_correct: 是否正确
    - error_detail: 错误详情（如果正确）
    - score: 当前得分
    - remaining_errors: 剩余错误数

    **业务规则：**
    - 找到错误：+10分
    - 点错位置：-5分
    - 同一错误重复点击：不扣分，提示已找到
    """
    try:
        result = await game_service.submit_answer(
            session_id=request.session_id,
            location=request.location,
            user_id=current_user.id,
            db=db
        )
        return ApiResponse(
            code=200,
            message="success",
            data=AnswerSubmitResponse(**result)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/hint", response_model=ApiResponse[HintResponse])
async def use_hint(
    request: HintRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    使用提示

    **请求参数：**
    - session_id: 游戏会话ID

    **响应内容：**
    - hint: 提示内容
    - remaining_hints: 剩余提示次数
    - score: 当前得分

    **业务规则：**
    - 每局游戏最多使用3次提示
    - 使用提示：-3分
    - 提示内容逐步详细：
      - 第1次：错误类型
      - 第2次：错误位置范围
      - 第3次：直接高亮错误位置
    """
    try:
        result = await game_service.use_hint(
            session_id=request.session_id,
            user_id=current_user.id,
            db=db
        )
        return ApiResponse(
            code=200,
            message="success",
            data=HintResponse(**result)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/complete", response_model=ApiResponse[GameCompleteResponse])
async def complete_game(
    request: GameCompleteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    完成游戏

    **请求参数：**
    - session_id: 游戏会话ID

    **响应内容：**
    - final_score: 最终得分
    - found_errors: 找到的错误列表
    - missed_errors: 未找到的错误列表
    - time_used: 用时（秒）
    - achievements_unlocked: 解锁的成就
    - rank_change: 排名变化

    **业务规则：**
    - 时间奖励：30秒内+20分，60秒内+10分
    - 完美通关（全找到且无提示）：额外+50分
    - 自动保存游戏记录
    """
    try:
        result = await game_service.complete_game(
            session_id=request.session_id,
            user_id=current_user.id,
            db=db
        )
        return ApiResponse(
            code=200,
            message="游戏完成",
            data=GameCompleteResponse(**result)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=ApiResponse[UserStatsResponse])
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    获取用户游戏统计

    **响应内容：**
    - total_games: 总游戏次数
    - total_found: 总找到错误数
    - total_score: 总积分
    - win_rate: 胜率（找到所有错误的次数/总次数）
    - best_time: 最佳用时
    - current_streak: 当前连胜次数
    - max_streak: 最大连胜次数
    - weak_points: 薄弱环节分析
    """
    try:
        result = await game_service.get_user_stats(
            user_id=current_user.id,
            db=db
        )
        return ApiResponse(
            code=200,
            message="获取成功",
            data=UserStatsResponse(**result)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/leaderboard", response_model=ApiResponse[LeaderboardResponse])
async def get_leaderboard(
    period: Period = Period.all,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    获取排行榜

    **查询参数：**
    - period: 时间周期（daily/weekly/monthly/all）
    - limit: 返回数量

    **响应内容：**
    - period: 时间周期
    - rankings: 排行榜列表
    - my_rank: 当前用户排名
    - my_score: 当前用户积分

    **业务规则：**
    - 每日排行榜：每天0点重置
    - 每周排行榜：每周一0点重置
    - 每月排行榜：每月1号0点重置
    - 全局排行榜：永不重置
    """
    try:
        result = await game_service.get_leaderboard(
            period=period,
            limit=limit,
            user_id=current_user.id,
            db=db
        )
        return ApiResponse(
            code=200,
            message="获取成功",
            data=LeaderboardResponse(**result)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/achievements", response_model=ApiResponse[AchievementsResponse])
async def get_achievements(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    获取成就列表

    **响应内容：**
    - total: 成就总数
    - unlocked: 已解锁数量
    - achievements: 成就列表
      - id: 成就ID
      - name: 成就名称
      - description: 成就描述
      - icon: 成就图标
      - unlocked: 是否解锁
      - unlocked_at: 解锁时间
      - progress: 当前进度（未解锁时）
      - total: 目标进度（未解锁时）

    **成就列表：**
    - 初露锋芒：第一次找到简历错误
    - 简历侦探：累计找到50个错误
    - 完美主义者：连续3局完美通关
    - 闪电侠：困难模式快速通关
    - 简历大师：困难模式通关10次
    - 连胜之王：连续获胜10次
    - 夜猫子：凌晨玩游戏
    """
    try:
        result = await game_service.get_achievements(
            user_id=current_user.id,
            db=db
        )
        return ApiResponse(
            code=200,
            message="获取成功",
            data=AchievementsResponse(**result)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/error-types", response_model=ApiResponse[ErrorTypesResponse])
async def get_error_types():
    """
    获取错误类型列表

    **响应内容：**
    - error_types: 错误类型列表
      - type_id: 类型ID
      - name: 名称
      - description: 描述
      - example: 错误示例
      - correct: 正确写法
      - tips: 优化建议

    **错误类型分类：**
    - 格式类错误：格式不一致、间距问题、字体混用
    - 内容类错误：描述空洞、缺少量化成果、动词力度弱
    - 逻辑类错误：时间线冲突、技能与经历不匹配、学历与工作年限矛盾
    - 专业性错误：负面语言、过度夸大、歧视性词汇
    """
    try:
        result = await game_service.get_error_types()
        return ApiResponse(
            code=200,
            message="获取成功",
            data=ErrorTypesResponse(**result)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))