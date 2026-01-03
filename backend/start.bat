@echo off
echo ========================================
echo 智能面试提升系统 - 后端启动脚本
echo ========================================

echo.
echo [1/5] 检查环境变量文件...
if not exist .env (
    echo 警告: .env 文件不存在，正在从 .env.example 复制...
    copy .env.example .env
    echo 请编辑 .env 文件，填写正确的配置信息
    pause
    exit /b 1
)

echo.
echo [2/5] 启动 PostgreSQL 数据库...
docker-compose up -d

echo.
echo [3/5] 等待数据库启动...
timeout /t 5 /nobreak > nul

echo.
echo [4/5] 安装依赖（如果需要）...
pip install -r requirements.txt

echo.
echo [5/5] 初始化数据库...
alembic upgrade head

echo.
echo ========================================
echo 后端服务启动中...
echo ========================================
echo API 文档: http://localhost:8000/docs
echo 健康检查: http://localhost:8000/health
echo ========================================

uvicorn main:app --reload --host 0.0.0.0 --port 8000