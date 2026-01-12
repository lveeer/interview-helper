# 面向求职者的智能面试提升系统

基于 AI 的面试辅助平台，帮助求职者进行简历优化、岗位匹配、模拟面试和知识管理。

## 项目概述

随着高校毕业生规模增加，求职竞争激烈。传统面试准备方式缺乏针对性指导、反馈滞后且真人模拟成本高昂。本项目利用生成式大语言模型（LLM）及 RAG 技术，构建一套集简历解析、岗位匹配、AI模拟面试及知识强化于一体的智能系统，以提升求职者的面试竞争力。

## 技术栈

### 前端
- Vue 3.5.24
- Element Plus 2.13.0
- Pinia 3.0.4（状态管理）
- Vue Router 4.6.4（路由）
- Axios 1.13.2（HTTP 客户端）
- Vite 5.4.0（构建工具）

### 后端
- FastAPI
- Python 3.x
- PostgreSQL + pgvector（数据库）
- SQLAlchemy（ORM）
- Unstructured.io（文档解析）
- LangChain（LLM 应用框架）
- WebSocket（实时通信）

## 环境要求

- Node.js >= 16.x
- npm >= 8.x
- Python >= 3.8
- Docker（用于数据库）

## 快速启动

### 启动顺序说明

**重要：必须先启动后端，再启动前端！**

```
后端服务 (端口 8000) → 前端服务 (端口 5173) → 浏览器访问
```

### 步骤 1：克隆项目

```bash
git clone git@github.com:lveeer/interview-helper.git
cd interview-helper
```

### 步骤 2：启动后端服务

打开第一个终端窗口，执行以下命令：

```bash
# 进入后端目录
cd backend

# 创建 Python 虚拟环境（首次运行需要）
python -m venv venv

# 激活虚拟环境
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 安装后端依赖（首次运行需要）
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填写必要的配置信息

# 启动数据库
docker-compose up -d

# 初始化数据库
alembic upgrade head

# 启动后端开发服务器
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**后端启动成功标志：**
- 终端显示 `INFO: Uvicorn running on http://0.0.0.0:8000`
- 访问 `http://localhost:8000/docs` 可以看到 Swagger API 文档界面

### 步骤 3：启动前端服务

打开第二个终端窗口，执行以下命令：

```bash
# 进入前端目录
cd frontend

# 安装前端依赖（首次运行需要）
npm install

# 启动前端开发服务器
npm run dev
```

**前端启动成功标志：**
- 终端显示 `Local: http://localhost:5173/`
- 浏览器自动打开或手动访问 `http://localhost:5173` 可以看到登录页面

### 步骤 4：验证服务

1. **后端验证：** 访问 `http://localhost:8000/docs` 查看 API 文档
2. **前端验证：** 访问 `http://localhost:5173` 查看应用界面
3. **功能验证：** 注册/登录账号，测试基本功能

## 服务端口说明

| 服务 | 端口 | 地址 | 说明 |
|------|------|------|------|
| 后端 API | 8000 | http://localhost:8000 | RESTful API 和 WebSocket |
| 前端页面 | 5173 | http://localhost:5173 | Vue 应用界面 |

## 停止服务

在各自的终端窗口按 `Ctrl + C` 停止服务

## 项目结构

```
interview-helper/
├── backend/            # 后端项目
│   ├── app/
│   │   ├── api/       # API 路由（认证、简历、岗位、面试、知识库、评估）
│   │   ├── core/      # 核心配置（数据库、安全）
│   │   ├── models/    # 数据库模型（用户、简历、面试、知识库）
│   │   ├── schemas/   # Pydantic 数据模型
│   │   ├── services/  # 业务逻辑
│   │   └── utils/     # 工具函数
│   ├── alembic/       # 数据库迁移配置
│   ├── uploads/       # 文件上传目录
│   ├── prompts/       # LLM 提示词模板
│   ├── main.py        # 应用入口
│   ├── config.py      # 配置管理
│   ├── requirements.txt
│   └── docker-compose.yml
└── frontend/          # 前端项目
    ├── src/
    │   ├── api/       # API 接口
    │   ├── components/# 公共组件
    │   ├── router/    # 路由配置
    │   ├── stores/    # Pinia 状态管理
    │   ├── utils/     # 工具函数
    │   └── views/     # 页面组件
    ├── index.html
    ├── package.json
    └── vite.config.js
```

## 功能模块

### 1. 用户管理
- 用户注册
- 用户登录
- 登录状态管理

### 2. 简历管理
- 上传简历（支持 PDF/DOCX）
- 简历智能解析
- 简历亮点分析
- 查看简历列表
- 查看简历详情
- 删除简历

### 3. 简历优化
- AI 智能优化建议
- 导出优化后的简历（PDF）

### 4. 岗位匹配分析
- 选择简历与岗位进行匹配
- 多维度匹配计算（关键词匹配、技能等级、项目相关性）
- 匹配度分析
- 优化建议

### 5. AI 模拟面试（核心功能）
- 个性化问题生成（基于简历和岗位 JD）
- 多模态交互（文字/语音）
- 多轮追问机制
- WebSocket 实时对话
- AI 面试官交互
- 查看面试报告

### 6. 外挂题库与知识库（RAG）
- 私有文档导入
- 本地知识库构建（基于 pgvector）
- 基于库的问答/提问
- 知识库查询
- 删除文档

### 7. 评估与反馈
- 实时评分
- 面试总结报告（Markdown 格式）
- 知识关联推荐
- 报告可视化

### 8. 数据统计
- 用户数据统计
- 面试记录统计

## API 文档

启动后端服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 主要接口说明

#### 认证接口 (`/api/auth`)
- `POST /register` - 用户注册
- `POST /login` - 用户登录
- `GET /me` - 获取当前用户信息

#### 简历管理 (`/api/resume`)
- `POST /upload` - 上传简历
- `GET /` - 获取所有简历
- `GET /{resume_id}` - 获取简历详情
- `DELETE /{resume_id}` - 删除简历

#### 模拟面试 (`/api/interview`)
- `POST /create` - 创建面试会话
- `GET /{interview_id}` - 获取面试详情
- `GET /{interview_id}/status` - 获取面试问题生成状态
- `GET /` - 获取所有面试记录
- `GET /{interview_id}/record` - 获取完整对话记录
- `WebSocket /ws/{interview_id}` - 面试实时通信

#### 知识库 (`/api/knowledge`)
- `POST /upload` - 上传知识库文档
- `GET /` - 获取所有知识库文档
- `DELETE /{doc_id}` - 删除知识库文档
- `POST /query` - 查询知识库

#### 评估反馈 (`/api/evaluation`)
- `GET /report/{interview_id}` - 获取面试评估报告

#### 岗位匹配 (`/api/job`)
- `POST /match` - 岗位匹配分析

#### 统计数据 (`/api/statistics`)
- `GET /` - 获取用户统计数据

## 常用命令

### 前端命令

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview
```

### 后端命令

```bash
# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
uvicorn main:app --reload

# 启动生产服务器
uvicorn main:app --host 0.0.0.0 --port 8000

# 数据库迁移
alembic upgrade head

# 启动数据库
docker-compose up -d
```

## 环境配置

### 前端环境变量

在 `frontend/` 目录下创建 `.env.development` 文件：

```env
VITE_API_BASE_URL=http://localhost:8000/api
```

### 后端环境变量

在 `backend/` 目录下创建 `.env` 文件（根据 `.env.example` 配置）：

```env
DATABASE_URL=postgresql://user:password@localhost:5432/interview_db
SECRET_KEY=your-secret-key
LLM_API_KEY=your-llm-api-key
```

## 常见问题

### Q: 前端启动后无法连接后端？
**A: 请按以下步骤排查：**

1. 检查后端是否已启动
   ```bash
   # 查看端口 8000 是否被占用
   lsof -i :8000  # Linux/Mac
   netstat -ano | findstr :8000  # Windows
   ```

2. 检查后端服务状态
   - 访问 `http://localhost:8000/docs` 是否能看到 API 文档
   - 检查后端终端是否有错误信息

3. 检查防火墙设置
   ```bash
   # Linux/Mac 临时关闭防火墙测试
   sudo ufw disable
   ```

4. 检查前端 API 地址配置
   - 确认 `frontend/.env.development` 文件中的 `VITE_API_BASE_URL` 是否正确

### Q: npm install 失败？
**A: 尝试以下解决方案：**

1. 清除 npm 缓存
   ```bash
   npm cache clean --force
   ```

2. 删除 node_modules 重新安装
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

3. 使用国内镜像源
   ```bash
   npm config set registry https://registry.npmmirror.com
   npm install
   ```

4. 检查 Node.js 版本（需要 >= 16.x）
   ```bash
   node -v
   ```

### Q: 后端启动失败，提示端口被占用？
**A: 查找并终止占用端口的进程：**

```bash
# Linux/Mac
lsof -ti:8000 | xargs kill -9

# Windows
netstat -ano | findstr :8000
taskkill /PID <进程ID> /F
```

### Q: 模拟面试功能无法使用？
**A: 确保 WebSocket 连接正常：**

1. 检查浏览器控制台是否有 WebSocket 连接错误
2. 确认后端 WebSocket 地址正确：`ws://localhost:8000/api/interview/ws`
3. 检查浏览器是否支持 WebSocket（现代浏览器都支持）

### Q: 简历上传失败？
**A: 检查以下内容：**

1. 文件格式：仅支持 PDF 和 DOCX 格式
2. 文件大小：检查是否有大小限制
3. 浏览器控制台：查看具体错误信息

### Q: 虚拟环境激活失败？
**A: 按系统选择正确的激活命令：**

- **Linux/Mac:**
  ```bash
  source venv/bin/activate
  ```

- **Windows (CMD):**
  ```batch
  venv\Scripts\activate.bat
  ```

- **Windows (PowerShell):**
  ```powershell
  venv\Scripts\Activate.ps1
  # 如果提示执行策略错误，先运行：
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

## 开发注意事项

1. **确保后端服务先启动**：前端依赖后端 API，请先启动后端服务
2. **API 地址配置**：默认后端地址为 `http://localhost:8000/api`
3. **WebSocket 连接**：模拟面试功能使用 WebSocket，地址为 `ws://localhost:8000/api/interview/ws`
4. **文件上传限制**：简历上传支持 PDF 和 DOCX 格式
5. **数据隔离**：不同用户的数据（如个人知识库）必须严格隔离

## 联系方式

- 项目地址：https://github.com/lveeer/interview-helper
- 问题反馈：请提交 GitHub Issue

## 许可证

本项目采用 MIT 许可证。