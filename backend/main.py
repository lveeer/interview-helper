from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from config import settings
import os

from app.api import auth, resume, job, interview, knowledge, evaluation, statistics


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时创建必要的目录
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(os.path.join(settings.UPLOAD_DIR, "resumes"), exist_ok=True)
    os.makedirs(os.path.join(settings.UPLOAD_DIR, "knowledge"), exist_ok=True)
    yield
    # 关闭时的清理工作
    pass


app = FastAPI(
    title="智能面试提升系统 API",
    description="面向求职者的智能面试提升系统后端服务",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 配置
origins = settings.CORS_ORIGINS.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(resume.router, prefix="/api/resume", tags=["简历管理"])
app.include_router(job.router, prefix="/api/job", tags=["岗位匹配"])
app.include_router(interview.router, prefix="/api/interview", tags=["模拟面试"])
app.include_router(knowledge.router, prefix="/api/knowledge", tags=["知识库"])
app.include_router(evaluation.router, prefix="/api/evaluation", tags=["评估反馈"])
app.include_router(statistics.router, prefix="/api/statistics", tags=["统计数据"])


@app.get("/")
async def root():
    return {"message": "智能面试提升系统 API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )