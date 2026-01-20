"""提示词加载工具"""
import os
import re
from typing import Dict


class PromptLoader:
    """提示词加载器"""

    _prompts_cache: Dict[str, str] = {}

    @staticmethod
    def get_prompt(prompt_name: str) -> str:
        """
        加载提示词模板

        Args:
            prompt_name: 提示词名称（不含扩展名）

        Returns:
            提示词内容
        """
        # 检查缓存
        if prompt_name in PromptLoader._prompts_cache:
            return PromptLoader._prompts_cache[prompt_name]

        # 获取项目根目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        prompt_path = os.path.join(project_root, 'prompts', f'{prompt_name}.txt')

        # 读取提示词文件
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                content = f.read()
            # 缓存结果
            PromptLoader._prompts_cache[prompt_name] = content
            return content
        except FileNotFoundError:
            raise FileNotFoundError(f"提示词文件未找到: {prompt_path}")

    @staticmethod
    def format_prompt(prompt_name: str, **kwargs) -> str:
        """
        格式化提示词

        Args:
            prompt_name: 提示词名称
            **kwargs: 格式化参数

        Returns:
            格式化后的提示词
        """
        template = PromptLoader.get_prompt(prompt_name)
        
        # 使用字符串替换，避免正则表达式对特殊字符（如反斜杠）的解析问题
        result = template
        for key, value in kwargs.items():
            placeholder = '{' + key + '}'
            result = result.replace(placeholder, str(value))
        
        return result

    @staticmethod
    def clear_cache():
        """清空缓存"""
        PromptLoader._prompts_cache.clear()
