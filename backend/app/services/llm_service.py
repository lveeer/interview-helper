from typing import Optional, Dict, Any, List
import json
import logging
from config import settings

logger = logging.getLogger(__name__)


class iFlowLLMService:
    """基于 iFlow API 的 LLM 服务（使用 OpenAI SDK）"""

    def __init__(self):
        self.api_key = settings.IFLOW_API_KEY
        self.api_url = settings.IFLOW_API_URL
        self.model = settings.IFLOW_MODEL
        self._client = None

    def _get_client(self):
        """获取 OpenAI 异步客户端实例"""
        if self._client is None:
            try:
                from openai import AsyncOpenAI
                # 提取 base_url（去掉 /chat/completions 后缀）
                base_url = self.api_url.replace('/chat/completions', '')
                self._client = AsyncOpenAI(
                    base_url=base_url,
                    api_key=self.api_key,
                    timeout=180.0
                )
                logger.info(f"OpenAI 异步客户端初始化成功: {base_url}")
            except ImportError:
                raise Exception("openai 库未安装，请运行: pip install openai")
            except Exception as e:
                logger.error(f"OpenAI 异步客户端初始化失败: {e}")
                raise Exception(f"OpenAI 异步客户端初始化失败: {str(e)}")
        return self._client

    async def generate_text(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 65535,
        **kwargs
    ) -> str:
        """
        生成文本（兼容接口）

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
        max_tokens: int = 65535,
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
        if not self.api_key:
            raise Exception("iFlow API Key 未配置")

        try:
            client = self._get_client()

            # 构建请求参数
            request_params = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "top_p": kwargs.get("top_p", 0.7),
            }

            # 添加 response_format 参数（如果指定）
            if "response_format" in kwargs:
                request_params["response_format"] = kwargs["response_format"]

            # 添加 tools 参数（如果指定）
            if "tools" in kwargs:
                request_params["tools"] = kwargs["tools"]

            # 调用 OpenAI API（异步）
            response = await client.chat.completions.create(**request_params)

            # 提取生成的文本
            if response and response.choices:
                return response.choices[0].message.content
            else:
                raise Exception("API 返回空响应")

        except Exception as e:
            logger.error(f"LLM 调用失败: {e}", exc_info=True)
            raise Exception(f"LLM 调用失败: {str(e)}")

    async def stream_chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 65535,
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
        if not self.api_key:
            raise Exception("iFlow API Key 未配置")

        try:
            client = self._get_client()

            # 构建请求参数
            request_params = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "top_p": kwargs.get("top_p", 0.7),
                "stream": True
            }

            # 调用 OpenAI 流式 API（异步）
            stream = await client.chat.completions.create(**request_params)

            # 逐块返回内容
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"LLM 流式调用失败: {e}", exc_info=True)
            raise Exception(f"LLM 流式调用失败: {str(e)}")

    async def parse_document(
        self,
        file_path: str,
        prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 65535,
        **kwargs
    ) -> str:
        """
        解析文档文件（先提取文本，然后通过 LLM 解析）

        Args:
            file_path: 文档文件路径
            prompt: 解析提示词
            temperature: 温度参数（0-1）
            max_tokens: 最大生成 token 数
            **kwargs: 其他参数

        Returns:
            解析结果（JSON 格式字符串）
        """
        import os

        if not self.api_key:
            raise Exception("iFlow API Key 未配置")

        if not os.path.exists(file_path):
            raise Exception(f"文件不存在: {file_path}")

        try:
            # 1. 提取文本内容
            text_content = self._extract_text_from_file(file_path)
            logger.info(f"文本提取完成，长度: {len(text_content)} 字符")

            # 2. 使用 LLM 解析文本
            client = self._get_client()

            # 构建消息列表
            messages = [
                {
                    "role": "user",
                    "content": f"{prompt}\n\n简历内容：\n{text_content}"
                }
            ]

            # 构建请求参数
            request_params = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "response_format": {"type": "json_object"}
            }

            # 调用 OpenAI API（异步）
            response = await client.chat.completions.create(**request_params)

            # 提取解析结果
            if response and response.choices:
                result = response.choices[0].message.content
                logger.info(f"文档解析成功，响应长度: {len(result)} 字符")
                return result
            else:
                raise Exception("API 返回空响应")

        except Exception as e:
            logger.error(f"文档解析失败: {e}", exc_info=True)
            raise Exception(f"文档解析失败: {str(e)}")

    def _extract_text_from_file(self, file_path: str) -> str:
        """
        从文件中提取文本内容

        Args:
            file_path: 文件路径

        Returns:
            提取的文本内容
        """
        import os
        file_ext = os.path.splitext(file_path)[1].lower()

        # 1. 处理文本文件
        if file_ext == '.txt':
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except UnicodeDecodeError:
                try:
                    with open(file_path, 'r', encoding='gbk') as f:
                        return f.read()
                except Exception as e:
                    logger.error(f"文本文件读取失败: {e}")
                    raise

        # 2. 处理 PDF 文件
        if file_ext == '.pdf':
            try:
                import pdfplumber
                text_content = ""
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text_content += page_text + "\n"
                return text_content
            except ImportError:
                logger.warning("pdfplumber 未安装，尝试使用 pypdf")
                try:
                    import pypdf
                    reader = pypdf.PdfReader(file_path)
                    text_content = ""
                    for page in reader.pages:
                        text_content += page.extract_text() + "\n"
                    return text_content
                except Exception as e:
                    logger.error(f"PDF 提取失败: {e}")
                    raise
            except Exception as e:
                logger.error(f"PDF 提取失败: {e}")
                raise

        # 3. 处理 Word 文件
        if file_ext in ['.docx', '.doc']:
            try:
                import docx2txt
                return docx2txt.process(file_path)
            except ImportError:
                logger.warning("docx2txt 未安装")
                raise Exception("缺少 docx2txt 库，请安装: pip install docx2txt")
            except Exception as e:
                logger.error(f"Word 文档提取失败: {e}")
                raise

        raise Exception(f"不支持的文件类型: {file_ext}")


# 全局 LLM 服务实例
_llm_service_instance: Optional[iFlowLLMService] = None


async def get_llm() -> iFlowLLMService:
    """
    获取全局 LLM 服务实例（单例模式）

    Returns:
        iFlowLLMService 实例
    """
    global _llm_service_instance
    if _llm_service_instance is None:
        _llm_service_instance = iFlowLLMService()
    return _llm_service_instance


def reset_llm_service():
    """重置 LLM 服务实例（用于测试或切换配置）"""
    global _llm_service_instance
    _llm_service_instance = None


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
            async with httpx.AsyncClient(timeout=120.0) as client:
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

        except httpx.TimeoutException:
            raise Exception("Ollama API 调用超时，请稍后重试或检查 Ollama 服务是否正常运行")
        except httpx.HTTPStatusError as e:
            error_msg = f"Ollama API 调用失败 (HTTP {e.response.status_code})"
            try:
                error_detail = e.response.json()
                if "error" in error_detail:
                    error_msg += f": {error_detail['error']}"
            except:
                error_msg += f": {e.response.text}"
            raise Exception(error_msg)
        except httpx.RequestError as e:
            raise Exception(f"Ollama API 网络请求失败: {str(e)}")
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