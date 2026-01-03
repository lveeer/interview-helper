# 智能面试提升系统 - 后端

## 技术栈
- FastAPI - Web 框架
- PostgreSQL + pgvector - 数据库
- SQLAlchemy - ORM
- Unstructured.io - 文档解析
- LangChain - LLM 应用框架
- WebSocket - 实时通信

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置环境变量
复制 `.env.example` 为 `.env` 并填写配置：
```bash
cp .env.example .env
```

### 3. 启动数据库
```bash
docker-compose up -d
```

### 4. 初始化数据库
```bash
alembic upgrade head
```

### 5. 启动服务
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 项目结构
```
backend/
├── alembic/              # 数据库迁移
├── app/
│   ├── api/             # API 路由
│   ├── core/            # 核心配置
│   ├── models/          # 数据库模型
│   ├── schemas/         # Pydantic 模型
│   ├── services/        # 业务逻辑
│   └── utils/           # 工具函数
├── uploads/             # 上传文件存储
├── main.py              # 应用入口
└── requirements.txt     # 依赖列表
```

## API 文档
启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc