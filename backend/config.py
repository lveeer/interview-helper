from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List


class Settings(BaseSettings):
    # 数据库配置
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/interview_helper"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "interview_helper"

    # JWT 配置
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200

    # LiteLLM 配置
    LITELLM_MODEL: str = "qwen/qwen-turbo"
    LITELLM_API_KEY: str = ""
    LITELLM_API_BASE: str = ""

    # iFlow API 配置
    IFLOW_API_KEY: str = ""
    IFLOW_API_URL: str = "https://apis.iflow.cn/v1/chat/completions"
    IFLOW_MODEL: str = "tstars2.0"

    # 通义千问配置（litellm 会自动使用）
    DASHSCOPE_API_KEY: str = ""

    # 文心一言配置（litellm 会自动使用）
    ERNIE_API_KEY: str = ""
    ERNIE_SECRET_KEY: str = ""

    # OpenAI 配置
    OPENAI_API_KEY: str = ""

    # 文件上传配置
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    ALLOWED_EXTENSIONS: str = ".pdf,.docx,.doc"

    # CORS 配置
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # Ollama 配置
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_EMBEDDING_MODEL: str = "qwen3-embedding:4b"
    OLLAMA_LLM_MODEL: str = "qwen2.5"

    # 向量数据库配置
    VECTOR_DIMENSION: int = 2560
    EMBEDDING_MODEL: str = "ollama"
    EMBEDDING_PROVIDER: str = "ollama"  # 可选: ollama, openai, litellm

    # RAG 配置
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    TOP_K: int = 5

    # RAG 优化配置
    ENABLE_QUERY_EXPANSION: bool = True  # 启用查询扩展
    QUERY_EXPANSION_COUNT: int = 3  # 查询扩展数量
    ENABLE_HYBRID_SEARCH: bool = True  # 启用混合检索
    ENABLE_RERANKING: bool = True  # 启用重排序
    RERANK_TOP_K: int = 10  # 重排序候选数量

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()