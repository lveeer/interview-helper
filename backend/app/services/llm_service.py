from typing import Optional, Dict, Any, List
from litellm import acompletion, aembedding
import json
from config import settings


class LiteLLMService:
    """基于 LiteLLM 的统一 LLM 服务"""

    def __init__(self):
        self.model = settings.LITELLM_MODEL
        self.api_key = settings.LITELLM_API_KEY
        self.api_base = settings.LITELLM_API_BASE

        # 设置环境变量供 litellm 使用
        if settings.DASHSCOPE_API_KEY:
            import os
            os.environ["DASHSCOPE_API_KEY"] = settings.DASHSCOPE_API_KEY

        if settings.ERNIE_API_KEY:
            import os
            os.environ["ERNIE_API_KEY"] = settings.ERNIE_API_KEY
            os.environ["ERNIE_SECRET_KEY"] = settings.ERNIE_SECRET_KEY

        if settings.OPENAI_API_KEY:
            import os
            os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY

    async def generate_text(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """
        生成文本

        Args:
            prompt: 提示词
            temperature: 温度参数（0-1）
            max_tokens: 最大生成 token 数
            **kwargs: 其他参数

        Returns:
            生成的文本
        """
        messages = [{"role": "user", "content": prompt}]

        response = await self.generate_chat(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )

        return response

    async def generate_chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """
        生成对话

        Args:
            messages: 消息列表
            temperature: 温度参数（0-1）
            max_tokens: 最大生成 token 数
            **kwargs: 其他参数

        Returns:
            生成的文本
        """
        try:
            # 构建请求参数
            params = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }

            # 添加可选参数
            if self.api_key:
                params["api_key"] = self.api_key
            if self.api_base:
                params["api_base"] = self.api_base

            # 添加其他参数
            params.update(kwargs)

            # 调用 litellm
            response = await acompletion(**params)

            # 提取生成的文本
            if response and response.choices:
                return response.choices[0].message.content
            else:
                raise Exception("API 返回空响应")

        except Exception as e:
            raise Exception(f"LLM 调用失败: {str(e)}")

    async def generate_embedding(
        self,
        text: str,
        **kwargs
    ) -> List[float]:
        """
        生成文本嵌入

        Args:
            text: 输入文本
            **kwargs: 其他参数

        Returns:
            向量嵌入
        """
        try:
            # 使用默认的 embedding 模型
            embedding_model = kwargs.get("model", "text-embedding-ada-002")

            params = {
                "model": embedding_model,
                "input": text,
            }

            if self.api_key:
                params["api_key"] = self.api_key
            if self.api_base:
                params["api_base"] = self.api_base

            # 调用 litellm embedding
            response = await aembedding(**params)

            # 提取向量
            if response and response.data:
                return response.data[0].embedding
            else:
                raise Exception("Embedding API 返回空响应")

        except Exception as e:
            raise Exception(f"Embedding 调用失败: {str(e)}")

    async def stream_chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ):
        """
        流式生成对话

        Args:
            messages: 消息列表
            temperature: 温度参数（0-1）
            max_tokens: 最大生成 token 数
            **kwargs: 其他参数

        Yields:
            生成的文本块
        """
        try:
            params = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": True,
            }

            if self.api_key:
                params["api_key"] = self.api_key
            if self.api_base:
                params["api_base"] = self.api_base

            params.update(kwargs)

            # 调用 litellm 流式接口
            response = await acompletion(**params)

            # 流式返回
            async for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            raise Exception(f"流式 LLM 调用失败: {str(e)}")


# 全局 LLM 服务实例
_llm_service_instance: Optional[LiteLLMService] = None


async def get_llm() -> LiteLLMService:
    """
    获取全局 LLM 服务实例（单例模式）

    Returns:
        LiteLLMService 实例
    """
    global _llm_service_instance
    if _llm_service_instance is None:
        _llm_service_instance = LiteLLMService()
    return _llm_service_instance


def reset_llm_service():
    """重置 LLM 服务实例（用于测试或切换配置）"""
    global _llm_service_instance
    _llm_service_instance = None