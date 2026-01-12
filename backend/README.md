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

### 主要接口说明

#### 1. 认证接口 (`/api/auth`)
- `POST /register` - 用户注册
- `POST /login` - 用户登录
- `GET /me` - 获取当前用户信息

#### 2. 简历管理 (`/api/resume`)
- `POST /upload` - 上传简历
- `GET /` - 获取所有简历
- `GET /{resume_id}` - 获取简历详情
- `DELETE /{resume_id}` - 删除简历

#### 3. 模拟面试 (`/api/interview`)
- `POST /create` - 创建面试会话
  ```json
  {
    "resume_id": 1,
    "job_description": "高级后端工程师，要求熟悉Python、FastAPI、PostgreSQL",
    "knowledge_doc_ids": [1, 2, 3]  // 可选，指定知识库文档ID列表
  }
  ```
  - `resume_id`: 简历ID（必填）
  - `job_description`: 岗位描述（必填）
  - `knowledge_doc_ids`: 知识库文档ID列表（可选），用于从特定知识库文档中检索相关内容，生成更具针对性的面试问题

- `GET /{interview_id}` - 获取面试详情
- `GET /{interview_id}/status` - 获取面试问题生成状态
- `GET /` - 获取所有面试记录
- `GET /{interview_id}/record` - 获取完整对话记录
- `WebSocket /ws/{interview_id}` - 面试实时通信

#### 4. 知识库 (`/api/knowledge`)
- `POST /upload` - 上传知识库文档
- `GET /` - 获取所有知识库文档
- `DELETE /{doc_id}` - 删除知识库文档
- `POST /query` - 查询知识库
  ```json
  {
    "query": "Python FastAPI 性能优化",
    "top_k": 5,
    "use_query_expansion": true,
    "use_hybrid_search": true,
    "use_reranking": true
  }
  ```
- `GET /{doc_id}/preview` - 获取文档预览
- `PUT /{doc_id}/category` - 更新文档分类
- `GET /query/history` - 获取查询历史
- `POST /query/history` - 保存查询历史
- `DELETE /query/history` - 清空查询历史

#### 5. 评估反馈 (`/api/evaluation`)
- `GET /report/{interview_id}` - 获取面试评估报告

#### 6. 岗位匹配 (`/api/job`)
- `POST /match` - 岗位匹配分析

#### 7. 统计数据 (`/api/statistics`)
- `GET /` - 获取用户统计数据