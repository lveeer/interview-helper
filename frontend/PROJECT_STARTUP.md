# 智能面试提升系统 - 项目启动文档

## 项目概述

智能面试提升系统是一个基于 AI 的面试辅助平台，帮助求职者进行简历优化、岗位匹配、模拟面试和知识管理。

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

## 环境要求

- Node.js >= 16.x
- npm >= 8.x
- Python >= 3.8

## 项目结构

```
interview-helper/
├── frontend/           # 前端项目
│   ├── src/
│   │   ├── api/        # API 接口
│   │   ├── components/ # 公共组件
│   │   ├── router/     # 路由配置
│   │   ├── stores/     # Pinia 状态管理
│   │   ├── utils/      # 工具函数
│   │   └── views/      # 页面组件
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
└── backend/            # 后端项目
```

## 快速启动

### 1. 克隆项目

```bash
git clone git@github.com:lveeer/interview-helper.git
cd interview-helper
```

### 2. 后端启动

```bash
cd backend

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 启动后端服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端服务将运行在 `http://localhost:8000`

### 3. 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端服务将运行在 `http://localhost:5173`

### 4. 访问应用

打开浏览器访问：`http://localhost:5173`

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
uvicorn app.main:app --reload

# 启动生产服务器
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 环境配置

### 前端环境变量

在 `frontend/` 目录下创建 `.env.development` 文件：

```env
VITE_API_BASE_URL=http://localhost:8000/api
```

### 后端环境变量

在 `backend/` 目录下创建 `.env` 文件（根据实际需求配置）：

```env
DATABASE_URL=sqlite:///./interview.db
SECRET_KEY=your-secret-key
```

## 功能模块

### 1. 用户认证
- 用户注册
- 用户登录
- 登录状态管理

### 2. 简历管理
- 上传简历（支持 PDF/DOCX）
- 查看简历列表
- 查看简历详情
- 删除简历

### 3. 简历优化
- AI 智能优化建议
- 导出优化后的简历（PDF）

### 4. 岗位匹配
- 选择简历与岗位进行匹配
- 匹配度分析
- 优化建议

### 5. 模拟面试
- 创建面试会话
- WebSocket 实时对话
- AI 面试官交互
- 查看面试报告

### 6. 知识库
- 上传学习文档
- 知识库查询
- 删除文档

### 7. 评估报告
- 面试评分
- 详细评价
- 推荐资源

### 8. 数据统计
- 用户数据统计
- 面试记录统计

## 开发注意事项

1. **确保后端服务先启动**：前端依赖后端 API，请先启动后端服务
2. **API 地址配置**：默认后端地址为 `http://localhost:8000/api`
3. **WebSocket 连接**：模拟面试功能使用 WebSocket，地址为 `ws://localhost:8000/api/interview/ws`
4. **文件上传限制**：简历上传支持 PDF 和 DOCX 格式

## 常见问题

### Q: 前端启动后无法连接后端？
A: 检查后端服务是否正常启动，端口是否为 8000，防火墙是否放行。

### Q: npm install 失败？
A: 尝试清除缓存：`npm cache clean --force`，然后重新安装。

### Q: 模拟面试功能无法使用？
A: 确保 WebSocket 连接正常，检查浏览器是否支持 WebSocket。

### Q: 简历上传失败？
A: 检查文件格式是否为 PDF 或 DOCX，文件大小是否超出限制。

## 联系方式

- 项目地址：https://github.com/lveeer/interview-helper
- 问题反馈：请提交 GitHub Issue

## 许可证

本项目采用 MIT 许可证。