#!/bin/bash
# 智能面试提升系统 - 后端启动脚本

echo "========================================"
echo "智能面试提升系统 - 后端启动脚本"
echo "========================================"

echo ""
echo "[1/5] 设置环境变量..."
export OLLAMA_BASE_URL=http://localhost:11434
export OLLAMA_EMBEDDING_MODEL=qwen3-embedding:0.6b
export OLLAMA_LLM_MODEL=qwen2.5
export VECTOR_DIMENSION=1024
export EMBEDDING_PROVIDER=ollama

echo "环境变量已设置:"
echo "  OLLAMA_EMBEDDING_MODEL=$OLLAMA_EMBEDDING_MODEL"
echo "  VECTOR_DIMENSION=$VECTOR_DIMENSION"

echo ""
echo "[2/5] 激活虚拟环境..."
source venv/bin/activate

echo ""
echo "[3/5] 启动 PostgreSQL 数据库..."
docker-compose up -d

echo ""
echo "[4/5] 等待数据库启动..."
sleep 3

echo ""
echo "[5/5] 启动后端服务..."
echo "API 文档: http://localhost:8000/docs"
echo "健康检查: http://localhost:8000/health"
echo "========================================"

uvicorn main:app --reload --host 0.0.0.0 --port 8000