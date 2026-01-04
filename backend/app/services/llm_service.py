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

        # 配置 iFlow API（通过 LiteLLM 的 OpenAI 兼容接口）
        if settings.IFLOW_API_KEY:
            import os
            os.environ["OPENAI_API_KEY"] = settings.IFLOW_API_KEY
            os.environ["OPENAI_API_BASE"] = settings.IFLOW_API_URL

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


class iFlowLLMService:
    """基于 iFlow API 的 LLM 服务"""

    def __init__(self):
        self.api_key = settings.IFLOW_API_KEY
        self.api_url = settings.IFLOW_API_URL
        self.model = settings.IFLOW_MODEL

    async def generate_chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False,
        **kwargs
    ) -> str:
        """
        生成对话

        Args:
            messages: 消息列表
            temperature: 温度参数（0-1）
            max_tokens: 最大生成 token 数
            stream: 是否流式输出
            **kwargs: 其他参数

        Returns:
            生成的文本
        """
        import httpx

        if not self.api_key:
            raise Exception("iFlow API Key 未配置")

        # 构建请求 payload
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": kwargs.get("top_p", 0.7),
            "top_k": kwargs.get("top_k", 50),
            "frequency_penalty": kwargs.get("frequency_penalty", 0.5),
            "n": kwargs.get("n", 1),
            "response_format": kwargs.get("response_format", {"type": "text"}),
        }

        # 添加可选的 tools 参数
        if "tools" in kwargs:
            payload["tools"] = kwargs["tools"]

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.api_url,
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                result = response.json()

                # 提取生成的文本
                if result and "choices" in result and result["choices"]:
                    return result["choices"][0]["message"]["content"]
                else:
                    raise Exception("API 返回空响应")

        except httpx.HTTPStatusError as e:
            raise Exception(f"iFlow API 调用失败 (HTTP {e.response.status_code}): {e.response.text}")
        except Exception as e:
            raise Exception(f"iFlow API 调用失败: {str(e)}")

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
        import httpx

        if not self.api_key:
            raise Exception("iFlow API Key 未配置")

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": kwargs.get("top_p", 0.7),
            "top_k": kwargs.get("top_k", 50),
            "frequency_penalty": kwargs.get("frequency_penalty", 0.5),
            "n": kwargs.get("n", 1),
            "response_format": kwargs.get("response_format", {"type": "text"}),
        }

        if "tools" in kwargs:
            payload["tools"] = kwargs["tools"]

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream(
                    "POST",
                    self.api_url,
                    json=payload,
                    headers=headers
                ) as response:
                    response.raise_for_status()

                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:]
                            if data_str == "[DONE]":
                                break

                            try:
                                import json
                                data = json.loads(data_str)
                                if "choices" in data and data["choices"]:
                                    delta = data["choices"][0].get("delta", {})
                                    content = delta.get("content", "")
                                    if content:
                                        yield content
                            except json.JSONDecodeError:
                                continue

        except httpx.HTTPStatusError as e:
            raise Exception(f"iFlow 流式 API 调用失败 (HTTP {e.response.status_code}): {e.response.text}")
        except Exception as e:
            raise Exception(f"iFlow 流式 API 调用失败: {str(e)}")


# 全局 iFlow 服务实例
_iflow_service_instance: Optional[iFlowLLMService] = None


async def get_iflow_llm() -> iFlowLLMService:
    """
    获取全局 iFlow LLM 服务实例（单例模式）

    Returns:
        iFlowLLMService 实例
    """
    global _iflow_service_instance
    if _iflow_service_instance is None:
        _iflow_service_instance = iFlowLLMService()
    return _iflow_service_instance


def reset_iflow_service():
    """重置 iFlow 服务实例（用于测试或切换配置）"""
    global _iflow_service_instance
    _iflow_service_instance = None


class OllamaEmbeddingService:
    """基于 Ollama 的 Embedding 服务"""

    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_EMBEDDING_MODEL

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
        import httpx

        try:
            # 调用 Ollama API
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/embeddings",
                    json={
                        "model": self.model,
                        "prompt": text
                    }
                )
                response.raise_for_status()
                result = response.json()

                # 提取向量
                if result and "embedding" in result:
                    return result["embedding"]
                else:
                    raise Exception("Ollama API 返回空响应")

        except httpx.HTTPStatusError as e:
            raise Exception(f"Ollama API 调用失败 (HTTP {e.response.status_code}): {e.response.text}")
        except Exception as e:
            raise Exception(f"Ollama API 调用失败: {str(e)}")

    async def generate_embeddings_batch(
        self,
        texts: List[str],
        **kwargs
    ) -> List[List[float]]:
        """
        批量生成文本嵌入

        Args:
            texts: 输入文本列表
            **kwargs: 其他参数

        Returns:
            向量嵌入列表
        """
        embeddings = []
        for text in texts:
            embedding = await self.generate_embedding(text, **kwargs)
            embeddings.append(embedding)
        return embeddings


# 全局 Ollama Embedding 服务实例
_ollama_embedding_instance: Optional[OllamaEmbeddingService] = None


async def get_ollama_embedding() -> OllamaEmbeddingService:
    """
    获取全局 Ollama Embedding 服务实例（单例模式）

    Returns:
        OllamaEmbeddingService 实例
    """
    global _ollama_embedding_instance
    if _ollama_embedding_instance is None:
        _ollama_embedding_instance = OllamaEmbeddingService()
    return _ollama_embedding_instance


def reset_ollama_embedding():
    """重置 Ollama Embedding 服务实例（用于测试或切换配置）"""
    global _ollama_embedding_instance
    _ollama_embedding_instance = None


async def get_embedding_service():
    """
    根据配置获取对应的 Embedding 服务

    Returns:
        Embedding 服务实例
    """
    provider = settings.EMBEDDING_PROVIDER.lower()

    if provider == "ollama":
        return await get_ollama_embedding()
    elif provider == "openai":
        llm = await get_llm()
        return llm
    elif provider == "litellm":
        llm = await get_llm()
        return llm
    else:
        raise Exception(f"不支持的 Embedding 提供商: {provider}")


async def create_embedding(text: str) -> List[float]:
    """
    统一的 Embedding 生成接口

    Args:
        text: 输入文本

    Returns:
        向量嵌入
    """
    service = await get_embedding_service()
    return await service.generate_embedding(text)