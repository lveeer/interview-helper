# 智能面试提升系统 - 前端

## 技术栈
- Vue 3
- Element Plus
- Pinia
- Vue Router
- Axios

## 快速开始

### 1. 安装依赖
```bash
npm install
```

### 2. 启动开发服务器
```bash
npm run dev
```

### 3. 构建生产版本
```bash
npm run build
```

## 项目结构
```
frontend/
├── src/
│   ├── api/           # API 接口
│   ├── components/    # 公共组件
│   ├── router/        # 路由配置
│   ├── stores/        # Pinia 状态管理
│   ├── utils/         # 工具函数
│   ├── views/         # 页面组件
│   ├── App.vue        # 根组件
│   └── main.js        # 入口文件
├── index.html
├── package.json
└── vite.config.js
```

## 功能模块

### 1. 用户认证
- 用户注册
- 用户登录
- 路由守卫

### 2. 简历管理
- 上传简历（PDF/DOCX）
- 查看简历列表
- 查看简历详情
- 删除简历

### 3. 岗位匹配
- 选择简历
- 输入岗位描述
- 匹配度分析
- 优化建议

### 4. 模拟面试
- 创建面试会话
- WebSocket 实时对话
- AI 面试官
- 查看面试报告

### 5. 知识库
- 上传学习文档
- 知识库查询
- 删除文档

### 6. 评估报告
- 面试评分
- 详细评价
- 推荐资源

## 环境变量

创建 `.env.development` 文件：
```env
VITE_API_BASE_URL=http://localhost:8000/api
```

## 注意事项

1. 确保后端服务已启动
2. API 地址默认为 `http://localhost:8000/api`
3. WebSocket 地址默认为 `ws://localhost:8000/api/interview/ws`