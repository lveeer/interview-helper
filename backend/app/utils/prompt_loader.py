"""提示词加载工具 - 支持配置中心（数据库优先）和文件系统后备"""
import os
import asyncio
from typing import Dict, Optional, Any
from dataclasses import dataclass
from functools import lru_cache

from app.core.database import AsyncSessionLocal


@dataclass
class PromptResolution:
    """Prompt 解析结果"""
    content: str
    version_id: Optional[int] = None
    version: Optional[str] = None
    is_ab_test: bool = False
    ab_test_variant: Optional[str] = None
    ab_test_id: Optional[int] = None
    source: str = "file"  # file, database


class PromptLoader:
    """
    提示词加载器
    
    支持两种模式：
    1. 数据库模式（优先）：从配置中心获取，支持版本控制和 A/B 测试
    2. 文件系统模式（后备）：从 prompts/ 目录读取
    
    使用方式：
    - 同步：PromptLoader.get_prompt("interview_questions")
    - 异步（支持 A/B 测试）：await PromptLoader.get_prompt_async("interview_questions", user_id=1)
    """

    # 文件系统缓存（仅用于后备模式）
    _file_cache: Dict[str, str] = {}
    
    # 配置中心开关（可通过环境变量控制）
    _use_config_center: bool = True
    
    # 项目根目录
    _project_root: Optional[str] = None

    @classmethod
    def _get_project_root(cls) -> str:
        """获取项目根目录"""
        if cls._project_root is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            cls._project_root = os.path.dirname(os.path.dirname(current_dir))
        return cls._project_root

    @classmethod
    def set_config_center_enabled(cls, enabled: bool):
        """启用/禁用配置中心模式"""
        cls._use_config_center = enabled

    @staticmethod
    def get_prompt(prompt_name: str) -> str:
        """
        加载提示词模板（同步方法，仅文件系统模式）
        
        对于需要 A/B 测试的场景，请使用 get_prompt_async 方法
        
        Args:
            prompt_name: 提示词名称（不含扩展名）
        
        Returns:
            提示词内容
        """
        # 尝试从配置中心获取（同步简化版本）
        if PromptLoader._use_config_center:
            try:
                # 创建事件循环并运行异步方法
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # 如果已经在异步上下文中，直接使用文件系统
                    pass
                else:
                    result = loop.run_until_complete(
                        PromptLoader._get_from_database(prompt_name)
                    )
                    if result:
                        return result.content
            except Exception:
                pass  # 忽略错误，使用文件系统后备

        # 文件系统后备
        return PromptLoader._get_from_file(prompt_name)

    @staticmethod
    async def get_prompt_async(
        prompt_name: str,
        user_id: Optional[int] = None,
        session_id: Optional[str] = None
    ) -> PromptResolution:
        """
        异步加载提示词模板（支持配置中心和 A/B 测试）
        
        Args:
            prompt_name: 提示词名称
            user_id: 用户ID（用于 A/B 测试一致性分流）
            session_id: 会话ID（用于 A/B 测试一致性分流）
        
        Returns:
            PromptResolution 对象，包含内容和元数据
        """
        # 优先从配置中心获取
        if PromptLoader._use_config_center:
            result = await PromptLoader._get_from_database(
                prompt_name, user_id=user_id, session_id=session_id
            )
            if result:
                return result

        # 文件系统后备
        content = PromptLoader._get_from_file(prompt_name)
        return PromptResolution(content=content, source="file")

    @staticmethod
    async def format_prompt_async(
        prompt_name: str,
        user_id: Optional[int] = None,
        session_id: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        异步格式化提示词（支持配置中心和 A/B 测试）
        
        Args:
            prompt_name: 提示词名称
            user_id: 用户ID
            session_id: 会话ID
            **kwargs: 格式化参数
        
        Returns:
            格式化后的提示词
        """
        resolution = await PromptLoader.get_prompt_async(prompt_name, user_id, session_id)
        content = resolution.content
        
        # 使用字符串替换
        for key, value in kwargs.items():
            placeholder = '{' + key + '}'
            content = content.replace(placeholder, str(value))
        
        return content

    @staticmethod
    def format_prompt(prompt_name: str, **kwargs) -> str:
        """
        格式化提示词（同步方法）
        
        Args:
            prompt_name: 提示词名称
            **kwargs: 格式化参数
        
        Returns:
            格式化后的提示词
        """
        template = PromptLoader.get_prompt(prompt_name)
        
        # 使用字符串替换，避免正则表达式对特殊字符的解析问题
        result = template
        for key, value in kwargs.items():
            placeholder = '{' + key + '}'
            result = result.replace(placeholder, str(value))
        
        return result

    @classmethod
    def _get_from_file(cls, prompt_name: str) -> str:
        """从文件系统获取 prompt"""
        # 检查缓存
        if prompt_name in cls._file_cache:
            return cls._file_cache[prompt_name]

        # 构建文件路径
        prompt_path = os.path.join(
            cls._get_project_root(),
            'prompts',
            f'{prompt_name}.txt'
        )

        # 读取文件
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                content = f.read()
            # 缓存结果
            cls._file_cache[prompt_name] = content
            return content
        except FileNotFoundError:
            raise FileNotFoundError(f"提示词文件未找到: {prompt_path}")

    @staticmethod
    async def _get_from_database(
        prompt_name: str,
        user_id: Optional[int] = None,
        session_id: Optional[str] = None
    ) -> Optional[PromptResolution]:
        """从配置中心数据库获取 prompt"""
        try:
            async with AsyncSessionLocal() as db:
                from app.services.prompt_config_service import PromptConfigService
                
                service = PromptConfigService(db)
                resolved = await service.get_effective_prompt(
                    prompt_name,
                    user_id=user_id,
                    session_id=session_id
                )
                
                if resolved:
                    return PromptResolution(
                        content=resolved.content,
                        version_id=resolved.version_id,
                        version=resolved.version,
                        is_ab_test=resolved.is_ab_test,
                        ab_test_variant=resolved.ab_test_variant.value if resolved.ab_test_variant else None,
                        ab_test_id=resolved.ab_test_id,
                        source="database"
                    )
                return None
        except Exception:
            return None

    @classmethod
    def clear_cache(cls):
        """清空文件缓存"""
        cls._file_cache.clear()

    @classmethod
    def get_cache_stats(cls) -> Dict[str, Any]:
        """获取缓存统计信息"""
        return {
            "file_cache_count": len(cls._file_cache),
            "config_center_enabled": cls._use_config_center
        }


# 便捷函数
async def get_prompt(prompt_name: str, user_id: Optional[int] = None, session_id: Optional[str] = None) -> str:
    """
    异步获取 prompt 内容（便捷函数）
    
    Args:
        prompt_name: 提示词名称
        user_id: 用户ID
        session_id: 会话ID
    
    Returns:
        提示词内容
    """
    resolution = await PromptLoader.get_prompt_async(prompt_name, user_id, session_id)
    return resolution.content


async def format_prompt(prompt_name: str, user_id: Optional[int] = None, session_id: Optional[str] = None, **kwargs) -> str:
    """
    异步格式化 prompt（便捷函数）
    
    Args:
        prompt_name: 提示词名称
        user_id: 用户ID
        session_id: 会话ID
        **kwargs: 格式化参数
    
    Returns:
        格式化后的提示词
    """
    return await PromptLoader.format_prompt_async(prompt_name, user_id, session_id, **kwargs)
