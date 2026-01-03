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
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # LiteLLM 配置
    LITELLM_MODEL: str = "qwen/qwen-turbo"
    LITELLM_API_KEY: str = ""
    LITELLM_API_BASE: str = ""

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

    # 向量数据库配置
    VECTOR_DIMENSION: int = 1536
    EMBEDDING_MODEL: str = "text-embedding-ada-002"

    # RAG 配置
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K: int = 5

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()