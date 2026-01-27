#!/usr/bin/env python3
"""
测试游戏模块导入是否正确
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("测试导入游戏模型...")
    from app.models.game import (
        ResumeFinderSession,
        UserPoints,
        UserAchievement,
        LeaderboardSnapshot
    )
    print("✓ 游戏模型导入成功")

    print("\n测试导入游戏Schema...")
    from app.schemas.game import (
        Difficulty,
        GameStatus,
        Period,
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
        ErrorTypesResponse
    )
    print("✓ 游戏Schema导入成功")

    print("\n测试导入游戏服务...")
    from app.services.game_service import game_service
    print("✓ 游戏服务导入成功")

    print("\n测试导入游戏API...")
    from app.api.game import router
    print("✓ 游戏API导入成功")

    print("\n验证错误类型定义...")
    error_types = game_service.ERROR_TYPES
    print(f"✓ 错误类型数量: {len(error_types)}")
    for error_type in error_types:
        print(f"  - {error_type}: {error_types[error_type]['name']}")

    print("\n验证成就定义...")
    achievements = game_service.ACHIEVEMENTS
    print(f"✓ 成就数量: {len(achievements)}")
    for achievement_id in achievements:
        print(f"  - {achievement_id}: {achievements[achievement_id]['name']}")

    print("\n验证难度配置...")
    for difficulty in [Difficulty.easy, Difficulty.medium, Difficulty.hard]:
        config = game_service._get_difficulty_config(difficulty)
        print(f"✓ {difficulty.value}: 错误数 {config['error_count']}, 时间限制 {config['time_limit']}秒")

    print("\n" + "="*50)
    print("所有测试通过！游戏模块结构正确。")
    print("="*50)

except Exception as e:
    print(f"\n✗ 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)