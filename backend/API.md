# 智能面试提升系统 API 文档

## 基本信息

- **Base URL:** `http://localhost:8000`
- **API Version:** 1.0.0
- **认证方式:** Bearer Token (JWT)

## 通用响应格式

### 成功响应
```json
{
  "code": 200,
  "message": "操作成功",
  "data": { ... }
}
```

### 列表响应
```json
{
  "code": 200,
  "message": "获取成功",
  "data": [ ... ],
  "total": 100
}
```

### 错误响应
```json
{
  "detail": "错误描述信息"
}
```

---

## 1. 认证模块 (`/api/auth`)

### 1.1 用户注册

**接口:** `POST /api/auth/register`

**请求体:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "full_name": "string"
}
```

**响应:**
```json
{
  "code": 201,
  "message": "注册成功",
  "data": {
    "id": 1,
    "username": "string",
    "email": "string",
    "full_name": "string"
  }
}
```

### 1.2 用户登录

**接口:** `POST /api/auth/login`

**请求体 (form-data):**
```
username: string
password: string
```

**响应:**
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  }
}
```

### 1.3 获取当前用户信息

**接口:** `GET /api/auth/me`

**Headers:**
```
Authorization: Bearer <access_token>
```

**响应:**
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "id": 1,
    "username": "string",
    "email": "string",
    "full_name": "string"
  }
}
```

---

## 2. 简历管理模块 (`/api/resume`)

### 2.1 上传简历

**接口:** `POST /api/resume/upload`

**Headers:**
```
Authorization: Bearer <access_token>
```

**请求体 (multipart/form-data):**
```
file: <简历文件>
```

**支持的文件格式:** PDF, DOCX, TXT

**响应:**
```json
{
  "code": 201,
  "message": "简历上传成功",
  "data": {
    "id": 1,
    "user_id": 1,
    "file_name": "resume.pdf",
    "file_type": "pdf",
    "personal_info": { ... },
    "education": [ ... ],
    "experience": [ ... ],
    "skills": [ ... ],
    "skills_raw": [ ... ],
    "projects": [ ... ],
    "highlights": [ ... ],
    "current_version": "v1.0",
    "created_at": "2025-01-20T10:00:00Z"
  }
}
```

### 2.2 获取简历列表

**接口:** `GET /api/resume/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**响应:**
```json
{
  "code": 200,
  "message": "获取成功",
  "data": [
    {
      "id": 1,
      "file_name": "resume.pdf",
      "file_type": "pdf",
      "created_at": "2025-01-20T10:00:00Z"
    }
  ],
  "total": 1
}
```

### 2.3 获取简历详情

**接口:** `GET /api/resume/{resume_id}`

**Headers:**
```
Authorization: Bearer <access_token>
```

**路径参数:**
- `resume_id`: 简历 ID

**响应:**
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "id": 1,
    "user_id": 1,
    "file_name": "resume.pdf",
    "file_type": "pdf",
    "personal_info": { ... },
    "education": [ ... ],
    "experience": [ ... ],
    "skills": [ ... ],
    "skills_raw": [ ... ],
    "projects": [ ... ],
    "highlights": [ ... ],
    "current_version": "v1.0",
    "created_at": "2025-01-20T10:00:00Z"
  }
}
```

### 2.4 重新解析简历

**接口:** `POST /api/resume/{resume_id}/reparse`

**Headers:**
```
Authorization: Bearer <access_token>
```

**路径参数:**
- `resume_id`: 简历 ID

**功能:** 使用最新的 LLM 提示词重新解析简历

**响应:**
```json
{
  "code": 200,
  "message": "重新解析成功",
  "data": {
    "id": 1,
    "user_id": 1,
    "file_name": "resume.pdf",
    "file_type": "pdf",
    "personal_info": { ... },
    "education": [ ... ],
    "experience": [ ... ],
    "skills": [ ... ],
    "skills_raw": [ ... ],
    "projects": [ ... ],
    "highlights": [ ... ],
    "current_version": "v1.0",
    "created_at": "2025-01-20T10:00:00Z"
  }
}
```

### 2.5 分析简历

**接口:** `POST /api/resume/{resume_id}/analyze`

**Headers:**
```
Authorization: Bearer <access_token>
```

**路径参数:**
- `resume_id`: 简历 ID

**查询参数:**
- `force_refresh` (可选): 是否强制重新分析，默认 `false`
- `jd` (可选): 目标职位描述，用于针对性分析

**响应:**
```json
{
  "code": 200,
  "message": "分析成功",
  "data": {
    "overall_score": 85,
    "content_score": 80,
    "match_score": 85,
    "clarity_score": 90,
    "strengths": [ ... ],
    "weaknesses": [ ... ],
    "personal_analysis": { ... },
    "education_analysis": { ... },
    "experience_analysis": { ... },
    "skills_analysis": { ... }
  }
}
```

### 2.6 获取优化建议

**接口:** `GET /api/resume/{resume_id}/suggestions`

**Headers:**
```
Authorization: Bearer <access_token>
```

**路径参数:**
- `resume_id`: 简历 ID

**查询参数:**
- `force_refresh` (可选): 是否强制重新生成，默认 `false`
- `jd` (可选): 目标职位描述，用于针对性优化

**响应:**
```json
{
  "code": 200,
  "message": "获取成功",
  "data": [
    {
      "id": 1,
      "priority": "high",
      "title": "优化建议标题",
      "description": "详细描述",
      "before": "优化前内容",
      "after": "优化后内容",
      "reason": "优化原因"
    }
  ]
}
```

### 2.7 应用优化建议

**接口:** `POST /api/resume/{resume_id}/optimize`

**Headers:**
```
Authorization: Bearer <access_token>
```

**路径参数:**
- `resume_id`: 简历 ID

**请求体:**
```json
{
  "suggestions": [
    {
      "id": 1,
      "priority": "high",
      "title": "优化建议标题",
      "description": "详细描述",
      "before": "优化前内容",
      "after": "优化后内容",
      "reason": "优化原因"
    }
  ],
  "jd": "可选的职位描述"
}
```

**响应:**
```json
{
  "code": 200,
  "message": "优化应用成功",
  "data": {
    "version": "v1.1",
    "optimized_at": "2025-01-20T10:00:00Z",
    "applied_count": 3
  }
}
```

### 2.8 获取优化历史

**接口:** `GET /api/resume/{resume_id}/optimization-history`

**Headers:**
```
Authorization: Bearer <access_token>
```

**路径参数:**
- `resume_id`: 简历 ID

**响应:**
```json
{
  "code": 200,
  "message": "获取成功",
  "data": [
    {
      "id": 1,
      "version": "v1.1",
      "version_before": "v1.0",
      "version_after": "v1.1",
      "title": "优化标题",
      "description": "优化描述",
      "status": "success",
      "created_at": "2025-01-20T10:00:00Z"
    }
  ]
}
```

### 2.9 导出简历

**接口:** `GET /api/resume/{resume_id}/export`

**Headers:**
```
Authorization: Bearer <access_token>
```

**路径参数:**
- `resume_id`: 简历 ID

**查询参数:**
- `format`: 导出格式，支持 `pdf` 或 `docx`，默认 `pdf`

**响应:** 文件流

### 2.10 比较简历版本

**接口:** `GET /api/resume/{resume_id}/compare`

**Headers:**
```
Authorization: Bearer <access_token>
```

**路径参数:**
- `resume_id`: 简历 ID

**查询参数:**
- `version1`: 版本1
- `version2`: 版本2

**响应:**
```json
{
  "code": 200,
  "message": "对比成功",
  "data": {
    "before": "v1.0",
    "after": "v1.1",
    "diff": [
      {
        "type": "modified",
        "section": "experience",
        "content": { ... }
      }
    ]
  }
}
```

### 2.11 恢复简历版本

**接口:** `POST /api/resume/{resume_id}/restore`

**Headers:**
```
Authorization: Bearer <access_token>
```

**路径参数:**
- `resume_id`: 简历 ID

**请求体:**
```json
{
  "version": "v1.0"
}
```

**响应:**
```json
{
  "code": 200,
  "message": "恢复成功",
  "data": {
    "version": "v1.0",
    "restored_at": "2025-01-20T10:00:00Z"
  }
}
```

### 2.12 删除简历

**接口:** `DELETE /api/resume/{resume_id}`

**Headers:**
```
Authorization: Bearer <access_token>
```

**路径参数:**
- `resume_id`: 简历 ID

**响应:**
```json
{
  "code": 200,
  "message": "删除成功"
}
```

---

## 3. 岗位管理模块 (`/api/jobs`)

### 3.1 创建岗位

**接口:** `POST /api/jobs`

**Headers:**
```
Authorization: Bearer <access_token>
```

**请求体:**
```json
{
  "title": "前端开发工程师",
  "company": "某某公司",
  "job_description": "岗位职责：..."
}
```

**响应:**
```json
{
  "code": 201,
  "message": "岗位创建成功",
  "data": {
    "id": 1,
    "user_id": 1,
    "title": "前端开发工程师",
    "company": "某某公司",
    "job_description": "岗位职责：...",
    "created_at": "2026-03-03T10:00:00Z",
    "updated_at": null
  }
}
```

### 3.2 获取岗位列表

**接口:** `GET /api/jobs`

**Headers:**
```
Authorization: Bearer <access_token>
```

**响应:**
```json
{
  "code": 200,
  "message": "获取成功",
  "data": [
    {
      "id": 1,
      "title": "前端开发工程师",
      "company": "某某公司",
      "created_at": "2026-03-03T10:00:00Z"
    }
  ],
  "total": 1
}
```

### 3.3 获取岗位详情

**接口:** `GET /api/jobs/{job_id}`

**Headers:**
```
Authorization: Bearer <access_token>
```

**路径参数:**
- `job_id`: 岗位 ID

**响应:**
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "id": 1,
    "user_id": 1,
    "title": "前端开发工程师",
    "company": "某某公司",
    "job_description": "岗位职责：...",
    "created_at": "2026-03-03T10:00:00Z",
    "updated_at": null
  }
}
```

### 3.4 更新岗位

**接口:** `PUT /api/jobs/{job_id}`

**Headers:**
```
Authorization: Bearer <access_token>
```

**路径参数:**
- `job_id`: 岗位 ID

**请求体:**
```json
{
  "title": "高级前端开发工程师",
  "company": "新公司",
  "job_description": "更新后的JD..."
}
```

**响应:**
```json
{
  "code": 200,
  "message": "更新成功",
  "data": {
    "id": 1,
    "user_id": 1,
    "title": "高级前端开发工程师",
    "company": "新公司",
    "job_description": "更新后的JD...",
    "created_at": "2026-03-03T10:00:00Z",
    "updated_at": "2026-03-03T11:00:00Z"
  }
}
```

### 3.5 删除岗位

**接口:** `DELETE /api/jobs/{job_id}`

**Headers:**
```
Authorization: Bearer <access_token>
```

**路径参数:**
- `job_id`: 岗位 ID

**响应:**
```json
{
  "code": 200,
  "message": "删除成功"
}
```

### 3.6 针对岗位创建面试

**接口:** `POST /api/jobs/{job_id}/interviews`

**Headers:**
```
Authorization: Bearer <access_token>
```

**路径参数:**
- `job_id`: 岗位 ID

**请求体:**
```json
{
  "resume_id": 1,
  "knowledge_doc_ids": [1, 2]
}
```

**说明:** job_description 从岗位自动获取

**响应:**
```json
{
  "code": 201,
  "message": "面试创建成功，正在生成面试问题",
  "data": {
    "id": 1,
    "user_id": 1,
    "resume_id": 1,
    "job_id": 1,
    "job_description": "岗位职责：...",
    "status": "initializing",
    "total_score": 0,
    "questions": [],
    "conversation": [],
    "created_at": "2026-03-03T10:00:00Z"
  }
}
```

### 3.7 获取岗位面试历史

**接口:** `GET /api/jobs/{job_id}/interviews`

**Headers:**
```
Authorization: Bearer <access_token>
```

**路径参数:**
- `job_id`: 岗位 ID

**响应:**
```json
{
  "code": 200,
  "message": "获取成功",
  "data": [
    {
      "id": 1,
      "resume_id": 1,
      "status": "completed",
      "total_score": 85,
      "created_at": "2026-03-03T10:00:00Z"
    }
  ],
  "total": 1
}
```

### 3.8 岗位匹配分析

**接口:** `POST /api/jobs/match`

**Headers:**
```
Authorization: Bearer <access_token>
```

**请求体:**
```json
{
  "resume_id": 1,
  "job_description": "职位描述内容"
}
```

**响应:**
```json
{
  "code": 200,
  "message": "匹配分析完成",
  "data": {
    "match_score": 85,
    "keyword_match": 80,
    "skill_match": 90,
    "project_relevance": 85,
    "suggestions": ["建议1", "建议2"],
    "missing_skills": ["技能1", "技能2"],
    "strengths": ["优势1", "优势2"]
  }
}
```

---

## 4. 模拟面试模块 (`/api/interview`)

### 4.1 创建面试会话

**接口:** `POST /api/interview/create`

**Headers:**
```
Authorization: Bearer <access_token>
```

**请求体:**
```json
{
  "resume_id": 1,
  "job_description": "职位描述",
  "job_id": 1,
  "knowledge_doc_ids": [1, 2, 3]
}
```

**字段说明:**
- `resume_id`: 简历 ID（必填）
- `job_description`: 职位描述（可选，优先使用 job_id）
- `job_id`: 关联岗位 ID（可选，若提供则自动使用岗位的 JD）
- `knowledge_doc_ids`: 关联的知识库文档 ID 列表（可选）

**响应:**
```json
{
  "code": 201,
  "message": "面试创建成功，正在生成面试问题，请稍后刷新查看",
  "data": {
    "id": 1,
    "user_id": 1,
    "resume_id": 1,
    "job_id": 1,
    "job_description": "职位描述",
    "status": "initializing",
    "total_score": 0,
    "questions": [],
    "conversation": [],
    "created_at": "2026-03-03T10:00:00Z"
  }
}
```

### 4.2 获取面试详情

**接口:** `GET /api/interview/{interview_id}`

**Headers:**
```
Authorization: Bearer <access_token>
```

**路径参数:**
- `interview_id`: 面试 ID

**响应:**
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "id": 1,
    "user_id": 1,
    "resume_id": 1,
    "job_id": 1,
    "job_description": "职位描述",
    "status": "pending",
    "total_score": 0,
    "questions": [
      {
        "id": 1,
        "question": "问题内容",
        "category": "技术",
        "difficulty": "中等"
      }
    ],
    "conversation": [],
    "created_at": "2026-03-03T10:00:00Z"
  }
}
```

### 4.3 获取面试状态

**接口:** `GET /api/interview/{interview_id}/status`

**Headers:**
```
Authorization: Bearer <access_token>
```

**路径参数:**
- `interview_id`: 面试 ID

**响应:**
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "interview_id": 1,
    "status": "pending",
    "generation_status": "completed",
    "message": "面试问题已生成",
    "has_questions": true,
    "error": null
  }
}
```

### 4.4 获取面试列表

**接口:** `GET /api/interview/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**响应:**
```json
{
  "code": 200,
  "message": "获取成功",
  "data": [
    {
      "id": 1,
      "job_id": 1,
      "job_description": "职位描述",
      "status": "completed",
      "total_score": 85,
      "created_at": "2026-03-03T10:00:00Z"
    }
  ],
  "total": 1
}
```

### 4.5 获取面试记录

**接口:** `GET /api/interview/{interview_id}/record`

**Headers:**
```
Authorization: Bearer <access_token>
```

**路径参数:**
- `interview_id`: 面试 ID

**响应:**
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "id": 1,
    "user_id": 1,
    "resume_id": 1,
    "job_id": 1,
    "job_description": "职位描述",
    "status": "completed",
    "total_score": 85,
    "questions": [ ... ],
    "conversation": [
      {
        "role": "interviewer",
        "content": "问题内容",
        "question_id": 1,
        "category": "技术",
        "difficulty": "中等",
        "type": null,
        "reason": null,
        "timestamp": "2026-03-03T10:00:00Z"
      },
      {
        "role": "candidate",
        "content": "回答内容",
        "question_id": 1,
        "timestamp": "2026-03-03T10:00:00Z"
      }
    ],
    "created_at": "2026-03-03T10:00:00Z"
  }
}
```

### 4.6 WebSocket 面试连接

**接口:** `WS /api/interview/ws/{interview_id}`

**功能:** 实时面试对话

**消息格式:**

发送回答:
```json
{
  "type": "answer",
  "answer": "回答内容"
}
```

结束面试:
```json
{
  "type": "end"
}
```

接收消息类型:
- `question`: 新问题
- `followup`: 追问
- `end`: 面试结束

---

## 5. 知识库模块 (`/api/knowledge`)

### 5.1 上传知识库文档

**接口:** `POST /api/knowledge/upload`

**Headers:**
```
Authorization: Bearer <access_token>
```

**请求体 (multipart/form-data):**
```
file: <文档文件>
```

**响应:**
```json
{
  "code": 201,
  "message": "文档上传成功",
  "data": {
    "id": 1,
    "user_id": 1,
    "file_name": "document.pdf",
    "file_type": "pdf",
    "category": null,
    "created_at": "2025-01-20T10:00:00Z"
  }
}
```

### 5.2 获取知识库文档列表

**接口:** `GET /api/knowledge/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**响应:**
```json
{
  "code": 200,
  "message": "获取成功",
  "data": [
    {
      "id": 1,
      "user_id": 1,
      "file_name": "document.pdf",
      "file_type": "pdf",
      "category": null,
      "created_at": "2025-01-20T10:00:00Z"
    }
  ],
  "total": 1
}
```

### 5.3 查询知识库

**接口:** `POST /api/knowledge/query`

**Headers:**
```
Authorization: Bearer <access_token>
```

**请求体:**
```json
{
  "query": "查询内容",
  "top_k": 5,
  "use_query_expansion": true,
  "use_hybrid_search": true,
  "use_reranking": true
}
```

**响应:**
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "query": "查询内容",
    "results": [
      {
        "content": "相关内容",
        "score": 0.95,
        "metadata": { ... }
      }
    ],
    "config": {
      "use_query_expansion": true,
      "use_hybrid_search": true,
      "use_reranking": true
    }
  }
}
```

### 5.4 获取文档分段预览

**接口:** `GET /api/knowledge/{doc_id}/preview`

**Headers:**
```
Authorization: Bearer <access_token>
```

**路径参数:**
- `doc_id`: 文档 ID

**功能:** 获取文档的分段预览内容，返回按 chunk_index 排序的所有分段

**响应（已分段文档）:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "chunks": [
      {
        "index": 0,
        "content": "第一个分段内容...",
        "parent_chunk_id": null
      },
      {
        "index": 1,
        "content": "第二个分段内容...",
        "parent_chunk_id": null
      }
    ],
    "total_chunks": 2,
    "chunk_strategy": "semantic"
  }
}
```

**响应（未分段文档）:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "chunks": [
      {
        "index": 0,
        "content": "文档原始内容..."
      }
    ],
    "total_chunks": 1,
    "chunk_strategy": "semantic"
  }
}
```

**字段说明:**
- `chunks`: 分段数组
  - `index`: 分段索引，从 0 开始
  - `content`: 分段文本内容
  - `parent_chunk_id`: 父块 ID（用于父子分段策略），null 表示无父块
- `total_chunks`: 分段总数
- `chunk_strategy`: 使用的分段策略
  - `semantic`: 语义分段
  - `parent_child`: 父子分段
  - `recursive`: 递归分段

### 5.5 更新文档分类

**接口:** `PUT /api/knowledge/{doc_id}/category`

**Headers:**
```
Authorization: Bearer <access_token>
```

**路径参数:**
- `doc_id`: 文档 ID

**请求体:**
```json
{
  "category": "分类名称"
}
```

**响应:**
```json
{
  "code": 200,
  "message": "分类更新成功"
}
```

### 5.6 获取查询历史

**接口:** `GET /api/knowledge/query/history`

**Headers:**
```
Authorization: Bearer <access_token>
```

**响应:**
```json
{
  "code": 200,
  "message": "success",
  "data": [
    "查询1",
    "查询2",
    "查询3"
  ]
}
```

### 5.7 保存查询历史

**接口:** `POST /api/knowledge/query/history`

**Headers:**
```
Authorization: Bearer <access_token>
```

**请求体:**
```json
{
  "query": "查询内容"
}
```

**响应:**
```json
{
  "code": 200,
  "message": "查询记录已保存"
}
```

### 5.8 清空查询历史

**接口:** `DELETE /api/knowledge/query/history`

**Headers:**
```
Authorization: Bearer <access_token>
```

**响应:**
```json
{
  "code": 200,
  "message": "历史记录已清空"
}
```

### 5.9 删除知识库文档

**接口:** `DELETE /api/knowledge/{doc_id}`

**Headers:**
```
Authorization: Bearer <access_token>
```

**路径参数:**
- `doc_id`: 文档 ID

**响应:**
```json
{
  "code": 200,
  "message": "删除成功"
}
```

---

## 6. 召回测试模块 (`/api/knowledge/recall-test`)

### 6.1 创建召回测试用例

**接口:** `POST /api/knowledge/recall-test/cases`

**Headers:**
```
Authorization: Bearer <access_token>
```

**请求体:**
```json
{
  "query": "查询问题",
  "expected_chunk_ids": [1, 2, 3],
  "description": "测试用例描述（可选）"
}
```

**字段说明:**
- `query`: 测试查询语句
- `expected_chunk_ids`: 期望召回的分段 ID 列表
- `description`: 测试用例描述（可选）

**响应:**
```json
{
  "code": 201,
  "message": "测试用例创建成功",
  "data": {
    "id": 1,
    "user_id": 1,
    "query": "查询问题",
    "expected_chunk_ids": [1, 2, 3],
    "description": "测试用例描述",
    "created_at": "2026-01-22T10:00:00Z"
  }
}
```

---

### 6.2 获取召回测试用例列表

**接口:** `GET /api/knowledge/recall-test/cases`

**Headers:**
```
Authorization: Bearer <access_token>
```

**响应:**
```json
{
  "code": 200,
  "message": "获取成功",
  "data": [
    {
      "id": 1,
      "user_id": 1,
      "query": "查询问题",
      "expected_chunk_ids": [1, 2, 3],
      "description": "测试用例描述",
      "created_at": "2026-01-22T10:00:00Z"
    }
  ],
  "total": 1
}
```

---

### 6.3 删除召回测试用例

**接口:** `DELETE /api/knowledge/recall-test/cases/{test_case_id}`

**Headers:**
```
Authorization: Bearer <access_token>
```

**路径参数:**
- `test_case_id`: 测试用例 ID

**响应:**
```json
{
  "code": 200,
  "message": "测试用例删除成功"
}
```

---

### 6.4 执行召回测试

**接口:** `POST /api/knowledge/recall-test/run`

**Headers:**
```
Authorization: Bearer <access_token>
```

**请求体:**
```json
{
  "test_case_id": 1,
  "top_k": 5,
  "use_query_expansion": true,
  "use_hybrid_search": true,
  "use_reranking": true
}
```

**字段说明:**
- `test_case_id`: 测试用例 ID
- `top_k`: 召回数量，默认 5
- `use_query_expansion`: 是否使用查询扩展（可选，默认使用配置值）
- `use_hybrid_search`: 是否使用混合检索（可选，默认使用配置值）
- `use_reranking`: 是否使用重排序（可选，默认使用配置值）

**响应:**
```json
{
  "code": 201,
  "message": "测试执行成功",
  "data": {
    "id": 1,
    "user_id": 1,
    "test_case_id": 1,
    "retrieved_chunk_ids": [1, 2, 4, 5, 6],
    "retrieved_scores": [0.95, 0.88, 0.82, 0.75, 0.70],
    "recall": 67,
    "precision": 40,
    "f1_score": 50,
    "mrr": 100,
    "use_query_expansion": true,
    "use_hybrid_search": true,
    "use_reranking": true,
    "top_k": 5,
    "created_at": "2026-01-22T10:00:00Z"
  }
}
```

**指标说明:**
- `recall`: 召回率（百分比）= 命中的期望分段数 / 总期望分段数
- `precision`: 精确率（百分比）= 命中的期望分段数 / 总召回分段数
- `f1_score`: F1 分数（百分比）= 2 * precision * recall / (precision + recall)
- `mrr`: 平均倒数排名（百分比）= 1 / 第一次命中的位置

---

### 6.5 获取召回测试结果

**接口:** `GET /api/knowledge/recall-test/results`

**Headers:**
```
Authorization: Bearer <access_token>
```

**查询参数:**
- `test_case_id` (可选): 测试用例 ID，不传则返回所有测试结果

**响应:**
```json
{
  "code": 200,
  "message": "获取成功",
  "data": [
    {
      "id": 1,
      "user_id": 1,
      "test_case_id": 1,
      "retrieved_chunk_ids": [1, 2, 4, 5, 6],
      "retrieved_scores": [0.95, 0.88, 0.82, 0.75, 0.70],
      "recall": 67,
      "precision": 40,
      "f1_score": 50,
      "mrr": 100,
      "use_query_expansion": true,
      "use_hybrid_search": true,
      "use_reranking": true,
      "top_k": 5,
      "created_at": "2026-01-22T10:00:00Z"
    }
  ],
  "total": 1
}
```

---

### 6.6 获取召回测试汇总统计

**接口:** `GET /api/knowledge/recall-test/summary`

**Headers:**
```
Authorization: Bearer <access_token>
```

**查询参数:**
- `test_case_id` (可选): 测试用例 ID，不传则返回所有测试的汇总

**响应:**
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "total_tests": 10,
    "avg_recall": 75.5,
    "avg_precision": 68.2,
    "avg_f1_score": 71.6,
    "avg_mrr": 85.3,
    "results": [
      {
        "id": 1,
        "user_id": 1,
        "test_case_id": 1,
        "retrieved_chunk_ids": [1, 2, 4, 5, 6],
        "retrieved_scores": [0.95, 0.88, 0.82, 0.75, 0.70],
        "recall": 67,
        "precision": 40,
        "f1_score": 50,
        "mrr": 100,
        "use_query_expansion": true,
        "use_hybrid_search": true,
        "use_reranking": true,
        "top_k": 5,
        "created_at": "2026-01-22T10:00:00Z"
      }
    ]
  }
}
```

---

## 6. LLM 配置管理模块 (`/api/llm-config`)

### 6.1 获取当前用户 LLM 配置

**接口:** `GET /api/llm-config/`

**认证:** 需要登录

**响应示例:**
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "id": 1,
    "user_id": 2,
    "provider": "dashscope",
    "model_name": "qwen-plus",
    "api_key": "sk-xxxxx",
    "api_base": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "is_active": true,
    "created_at": "2026-01-21T10:00:00Z",
    "updated_at": "2026-01-21T10:00:00Z"
  }
}
```

**无配置时响应:**
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "id": 0,
    "user_id": 2,
    "provider": "",
    "model_name": "",
    "api_key": null,
    "api_base": null,
    "is_active": false,
    "created_at": null,
    "updated_at": null
  }
}
```

---

### 6.2 创建 LLM 配置

**接口:** `POST /api/llm-config/`

**认证:** 需要登录

**请求体:**
```json
{
  "provider": "dashscope",
  "model_name": "qwen-plus",
  "api_key": "sk-xxxxx",
  "api_base": "https://dashscope.aliyuncs.com/compatible-mode/v1",
  "is_active": true
}
```

**响应示例:**
```json
{
  "code": 201,
  "message": "创建成功",
  "data": {
    "id": 1,
    "user_id": 2,
    "provider": "dashscope",
    "model_name": "qwen-plus",
    "api_key": "sk-xxxxx",
    "api_base": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "is_active": true,
    "created_at": "2026-01-21T10:00:00Z",
    "updated_at": "2026-01-21T10:00:00Z"
  }
}
```

---

### 6.3 更新 LLM 配置

**接口:** `PUT /api/llm-config/`

**认证:** 需要登录

**请求体:**
```json
{
  "provider": "dashscope",
  "model_name": "qwen-max",
  "api_key": "sk-new-key",
  "api_base": null,
  "is_active": true
}
```

**响应示例:**
```json
{
  "code": 200,
  "message": "更新成功",
  "data": {
    "id": 1,
    "user_id": 2,
    "provider": "dashscope",
    "model_name": "qwen-max",
    "api_key": "sk-new-key",
    "api_base": null,
    "is_active": true,
    "created_at": "2026-01-21T10:00:00Z",
    "updated_at": "2026-01-21T11:00:00Z"
  }
}
```

---

### 6.4 删除 LLM 配置

**接口:** `DELETE /api/llm-config/`

**认证:** 需要登录

**响应示例:**
```json
{
  "code": 200,
  "message": "删除成功",
  "data": null
}
```

---

### 6.5 测试 LLM 连接

**接口:** `POST /api/llm-config/test-connection`

**认证:** 需要登录

**请求体:**
```json
{
  "provider": "dashscope",
  "model_name": "qwen-plus",
  "api_key": "sk-xxxxx",
  "api_base": "https://dashscope.aliyuncs.com/compatible-mode/v1"
}
```

**响应示例:**
```json
{
  "code": 200,
  "message": "测试完成",
  "data": {
    "success": true,
    "message": "连接成功",
    "latency_ms": 234.5,
    "error": null
  }
}
```

**失败示例:**
```json
{
  "code": 200,
  "message": "测试完成",
  "data": {
    "success": false,
    "message": "连接失败",
    "latency_ms": null,
    "error": "Invalid API key"
  }
}
```

---

### 6.6 获取支持的 LLM 提供商

**接口:** `GET /api/llm-config/providers`

**认证:** 需要登录

**响应示例:**
```json
{
  "code": 200,
  "message": "获取成功",
  "data": [
    {
      "provider": "dashscope",
      "name": "通义千问",
      "models": ["qwen-turbo", "qwen-plus", "qwen-max", "qwen-long"],
      "description": "阿里云通义千问大模型"
    },
    {
      "provider": "ernie",
      "name": "文心一言",
      "models": ["ernie-bot", "ernie-bot-turbo", "ernie-bot-4"],
      "description": "百度文心一言大模型"
    },
    {
      "provider": "openai",
      "name": "OpenAI",
      "models": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
      "description": "OpenAI GPT 系列"
    },
    {
      "provider": "anthropic",
      "name": "Anthropic",
      "models": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
      "description": "Anthropic Claude 系列"
    },
    {
      "provider": "ollama",
      "name": "Ollama",
      "models": ["qwen2.5", "llama3", "mistral"],
      "description": "本地部署的开源模型"
    }
  ]
}
```

---

## 8. 配置中心模块 (`/api/prompt-config`)

配置中心用于管理各功能的 Prompt 模板，支持版本控制和 A/B 测试。

### 8.1 Prompt 配置管理

#### 8.1.1 创建 Prompt 配置

**接口:** `POST /api/prompt-config`

**Headers:**
```
Authorization: Bearer <access_token>
```

**请求体:**
```json
{
  "name": "interview_questions",
  "display_name": "面试问题生成",
  "description": "用于生成面试问题的提示词模板",
  "category": "interview",
  "tags": "面试,问题生成",
  "is_active": true,
  "initial_content": "你是一个专业的面试官...",
  "initial_version": "v1.0.0"
}
```

**字段说明:**
- `name`: 配置名称，唯一标识（必填）
- `display_name`: 显示名称（可选）
- `description`: 配置描述（可选）
- `category`: 配置分类，可选值：`interview`、`resume`、`evaluation`、`rag`、`game`、`other`
- `tags`: 标签，逗号分隔（可选）
- `is_active`: 是否启用，默认 `true`
- `initial_content`: 初始版本内容（可选）
- `initial_version`: 初始版本号，默认 `v1.0.0`

**响应:**
```json
{
  "code": 200,
  "message": "创建成功",
  "data": {
    "id": 1,
    "name": "interview_questions",
    "display_name": "面试问题生成",
    "description": "用于生成面试问题的提示词模板",
    "category": "interview",
    "active_version_id": 1,
    "enable_ab_test": false,
    "active_ab_test_id": null,
    "tags": "面试,问题生成",
    "is_active": true,
    "created_at": "2026-03-04T10:00:00Z",
    "updated_at": null,
    "created_by": 1,
    "active_version": {
      "id": 1,
      "version": "v1.0.0",
      "is_published": true,
      "created_at": "2026-03-04T10:00:00Z"
    },
    "version_count": 1
  }
}
```

#### 8.1.2 获取配置列表

**接口:** `GET /api/prompt-config`

**Headers:**
```
Authorization: Bearer <access_token>
```

**查询参数:**
- `category`: 分类过滤（可选）
- `is_active`: 是否启用过滤（可选）
- `search`: 搜索关键词（可选）
- `page`: 页码，默认 1
- `page_size`: 每页数量，默认 20

**响应:**
```json
{
  "code": 200,
  "message": "获取成功",
  "data": [
    {
      "id": 1,
      "name": "interview_questions",
      "display_name": "面试问题生成",
      "category": "interview",
      "is_active": true,
      "enable_ab_test": false,
      "active_version_id": 1,
      "version_count": 3,
      "created_at": "2026-03-04T10:00:00Z",
      "updated_at": "2026-03-04T11:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20
}
```

#### 8.1.3 获取配置详情

**接口:** `GET /api/prompt-config/{config_id}`

**Headers:**
```
Authorization: Bearer <access_token>
```

**路径参数:**
- `config_id`: 配置 ID

**响应:** 同创建响应

#### 8.1.4 更新配置

**接口:** `PUT /api/prompt-config/{config_id}`

**Headers:**
```
Authorization: Bearer <access_token>
```

**路径参数:**
- `config_id`: 配置 ID

**请求体:**
```json
{
  "display_name": "新的显示名称",
  "description": "新的描述",
  "category": "interview",
  "tags": "新标签",
  "is_active": true
}
```

**响应:** 同创建响应

#### 8.1.5 删除配置

**接口:** `DELETE /api/prompt-config/{config_id}`

**Headers:**
```
Authorization: Bearer <access_token>
```

**路径参数:**
- `config_id`: 配置 ID

**响应:**
```json
{
  "code": 200,
  "message": "删除成功"
}
```

#### 8.1.6 设置激活版本

**接口:** `POST /api/prompt-config/{config_id}/activate-version`

**Headers:**
```
Authorization: Bearer <access_token>
```

**路径参数:**
- `config_id`: 配置 ID

**请求体:**
```json
{
  "version_id": 2
}
```

**响应:**
```json
{
  "code": 200,
  "message": "设置成功"
}
```

---

### 8.2 版本管理

#### 8.2.1 创建版本

**接口:** `POST /api/prompt-config/{config_id}/versions`

**Headers:**
```
Authorization: Bearer <access_token>
```

**路径参数:**
- `config_id`: 配置 ID

**请求体:**
```json
{
  "version": "v1.1.0",
  "content": "优化后的 Prompt 内容...",
  "change_log": "优化了问题生成的逻辑"
}
```

**响应:**
```json
{
  "code": 200,
  "message": "创建成功",
  "data": {
    "id": 2,
    "config_id": 1,
    "version": "v1.1.0",
    "content": "优化后的 Prompt 内容...",
    "change_log": "优化了问题生成的逻辑",
    "is_published": false,
    "published_at": null,
    "usage_count": 0,
    "avg_score": null,
    "created_at": "2026-03-04T10:00:00Z",
    "created_by": 1
  }
}
```

#### 8.2.2 获取版本列表

**接口:** `GET /api/prompt-config/{config_id}/versions`

**Headers:**
```
Authorization: Bearer <access_token>
```

**路径参数:**
- `config_id`: 配置 ID

**查询参数:**
- `include_unpublished`: 是否包含未发布版本，默认 `true`

**响应:**
```json
{
  "code": 200,
  "message": "获取成功",
  "data": [
    {
      "id": 2,
      "config_id": 1,
      "version": "v1.1.0",
      "content": "优化后的 Prompt 内容...",
      "change_log": "优化了问题生成的逻辑",
      "is_published": true,
      "published_at": "2026-03-04T11:00:00Z",
      "usage_count": 10,
      "avg_score": 85.5,
      "created_at": "2026-03-04T10:00:00Z",
      "created_by": 1
    },
    {
      "id": 1,
      "config_id": 1,
      "version": "v1.0.0",
      "content": "初始 Prompt 内容...",
      "change_log": "初始版本",
      "is_published": true,
      "published_at": "2026-03-04T10:00:00Z",
      "usage_count": 50,
      "avg_score": 80.0,
      "created_at": "2026-03-04T09:00:00Z",
      "created_by": 1
    }
  ]
}
```

#### 8.2.3 获取版本详情

**接口:** `GET /api/prompt-config/versions/{version_id}`

**Headers:**
```
Authorization: Bearer <access_token>
```

**路径参数:**
- `version_id`: 版本 ID

**响应:** 同创建版本响应

#### 8.2.4 更新版本

**接口:** `PUT /api/prompt-config/versions/{version_id}`

**说明:** 仅未发布的版本可以更新

**Headers:**
```
Authorization: Bearer <access_token>
```

**路径参数:**
- `version_id`: 版本 ID

**请求体:**
```json
{
  "content": "修改后的内容",
  "change_log": "修改说明"
}
```

**响应:** 同创建版本响应

#### 8.2.5 发布版本

**接口:** `POST /api/prompt-config/versions/{version_id}/publish`

**Headers:**
```
Authorization: Bearer <access_token>
```

**路径参数:**
- `version_id`: 版本 ID

**响应:**
```json
{
  "code": 200,
  "message": "发布成功",
  "data": {
    "id": 2,
    "config_id": 1,
    "version": "v1.1.0",
    "content": "优化后的 Prompt 内容...",
    "change_log": "优化了问题生成的逻辑",
    "is_published": true,
    "published_at": "2026-03-04T11:00:00Z",
    "usage_count": 0,
    "avg_score": null,
    "created_at": "2026-03-04T10:00:00Z",
    "created_by": 1
  }
}
```

#### 8.2.6 删除版本

**接口:** `DELETE /api/prompt-config/versions/{version_id}`

**说明:** 仅未发布的版本可以删除

**Headers:**
```
Authorization: Bearer <access_token>
```

**路径参数:**
- `version_id`: 版本 ID

**响应:**
```json
{
  "code": 200,
  "message": "删除成功"
}
```

---

### 8.3 A/B 测试管理

#### 8.3.1 创建 A/B 测试

**接口:** `POST /api/prompt-config/{config_id}/ab-tests`

**Headers:**
```
Authorization: Bearer <access_token>
```

**路径参数:**
- `config_id`: 配置 ID

**请求体:**
```json
{
  "name": "问题生成优化测试",
  "description": "测试新版问题生成 Prompt 的效果",
  "control_version_id": 1,
  "experiment_version_id": 2,
  "traffic_ratio": 0.3,
  "start_time": "2026-03-04T10:00:00Z",
  "end_time": "2026-03-11T10:00:00Z"
}
```

**字段说明:**
- `name`: 测试名称（必填）
- `description`: 测试描述（可选）
- `control_version_id`: 对照组版本 ID（必填）
- `experiment_version_id`: 实验组版本 ID（必填）
- `traffic_ratio`: 实验组流量比例，0-1 之间，默认 0.5
- `start_time`: 开始时间（可选）
- `end_time`: 结束时间（可选）

**响应:**
```json
{
  "code": 200,
  "message": "创建成功",
  "data": {
    "id": 1,
    "config_id": 1,
    "name": "问题生成优化测试",
    "description": "测试新版问题生成 Prompt 的效果",
    "control_version_id": 1,
    "experiment_version_id": 2,
    "traffic_ratio": 0.3,
    "status": "draft",
    "start_time": "2026-03-04T10:00:00Z",
    "end_time": "2026-03-11T10:00:00Z",
    "control_samples": 0,
    "experiment_samples": 0,
    "created_at": "2026-03-04T09:00:00Z",
    "updated_at": null,
    "created_by": 1,
    "control_version": {
      "id": 1,
      "version": "v1.0.0",
      "is_published": true,
      "created_at": "2026-03-04T08:00:00Z"
    },
    "experiment_version": {
      "id": 2,
      "version": "v1.1.0",
      "is_published": true,
      "created_at": "2026-03-04T08:30:00Z"
    }
  }
}
```

#### 8.3.2 获取 A/B 测试列表

**接口:** `GET /api/prompt-config/{config_id}/ab-tests`

**Headers:**
```
Authorization: Bearer <access_token>
```

**路径参数:**
- `config_id`: 配置 ID

**查询参数:**
- `status`: 状态过滤（可选）
- `page`: 页码，默认 1
- `page_size`: 每页数量，默认 20

**响应:**
```json
{
  "code": 200,
  "message": "获取成功",
  "data": [
    {
      "id": 1,
      "name": "问题生成优化测试",
      "config_id": 1,
      "config_name": "interview_questions",
      "status": "running",
      "traffic_ratio": 0.3,
      "control_samples": 50,
      "experiment_samples": 20,
      "start_time": "2026-03-04T10:00:00Z",
      "end_time": "2026-03-11T10:00:00Z",
      "created_at": "2026-03-04T09:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20
}
```

#### 8.3.3 获取 A/B 测试详情

**接口:** `GET /api/prompt-config/ab-tests/{test_id}`

**Headers:**
```
Authorization: Bearer <access_token>
```

**路径参数:**
- `test_id`: 测试 ID

**响应:** 同创建响应

#### 8.3.4 更新 A/B 测试

**接口:** `PUT /api/prompt-config/ab-tests/{test_id}`

**说明:** 仅草稿状态可以更新

**Headers:**
```
Authorization: Bearer <access_token>
```

**路径参数:**
- `test_id`: 测试 ID

**请求体:**
```json
{
  "name": "新的测试名称",
  "description": "新的描述",
  "traffic_ratio": 0.5,
  "start_time": "2026-03-05T10:00:00Z",
  "end_time": "2026-03-12T10:00:00Z"
}
```

**响应:** 同创建响应

#### 8.3.5 变更 A/B 测试状态

**接口:** `POST /api/prompt-config/ab-tests/{test_id}/status`

**Headers:**
```
Authorization: Bearer <access_token>
```

**路径参数:**
- `test_id`: 测试 ID

**请求体:**
```json
{
  "status": "running"
}
```

**状态流转:**
- `draft` → `running`: 开始测试
- `running` → `paused`: 暂停测试
- `running` → `completed`: 完成测试
- `paused` → `running`: 恢复测试
- `paused` → `completed`: 完成测试
- `completed` → `archived`: 归档测试

**响应:**
```json
{
  "code": 200,
  "message": "状态变更成功",
  "data": {
    "id": 1,
    "config_id": 1,
    "name": "问题生成优化测试",
    "status": "running",
    "start_time": "2026-03-04T10:00:00Z",
    "control_samples": 0,
    "experiment_samples": 0,
    "created_at": "2026-03-04T09:00:00Z"
  }
}
```

#### 8.3.6 激活 A/B 测试

**接口:** `POST /api/prompt-config/{config_id}/activate-ab-test`

**说明:** 将测试应用到配置，开始分流

**Headers:**
```
Authorization: Bearer <access_token>
```

**路径参数:**
- `config_id`: 配置 ID

**请求体:**
```json
{
  "ab_test_id": 1
}
```

**响应:**
```json
{
  "code": 200,
  "message": "激活成功"
}
```

#### 8.3.7 停用 A/B 测试

**接口:** `POST /api/prompt-config/{config_id}/deactivate-ab-test`

**Headers:**
```
Authorization: Bearer <access_token>
```

**路径参数:**
- `config_id`: 配置 ID

**响应:**
```json
{
  "code": 200,
  "message": "停用成功"
}
```

#### 8.3.8 删除 A/B 测试

**接口:** `DELETE /api/prompt-config/ab-tests/{test_id}`

**说明:** 仅草稿状态可以删除

**Headers:**
```
Authorization: Bearer <access_token>
```

**路径参数:**
- `test_id`: 测试 ID

**响应:**
```json
{
  "code": 200,
  "message": "删除成功"
}
```

---

### 8.4 A/B 测试结果

#### 8.4.1 记录测试结果

**接口:** `POST /api/prompt-config/ab-tests/{test_id}/results`

**Headers:**
```
Authorization: Bearer <access_token>
```

**路径参数:**
- `test_id`: 测试 ID

**请求体:**
```json
{
  "variant": "control",
  "session_id": "interview_123",
  "metrics": "{\"response_time\": 1.5, \"quality_score\": 85}",
  "score": 85,
  "feedback": "问题质量很好"
}
```

**字段说明:**
- `variant`: 变体类型，`control` 或 `experiment`
- `session_id`: 会话 ID（用于追踪）
- `metrics`: 指标数据，JSON 字符串（可选）
- `score`: 评分（可选）
- `feedback`: 反馈信息（可选）

**响应:**
```json
{
  "code": 200,
  "message": "记录成功",
  "data": {
    "id": 1,
    "ab_test_id": 1,
    "variant": "control",
    "version_id": 1,
    "session_id": "interview_123",
    "user_id": 1,
    "metrics": "{\"response_time\": 1.5, \"quality_score\": 85}",
    "score": 85,
    "feedback": "问题质量很好",
    "created_at": "2026-03-04T10:00:00Z"
  }
}
```

#### 8.4.2 获取测试统计

**接口:** `GET /api/prompt-config/ab-tests/{test_id}/statistics`

**Headers:**
```
Authorization: Bearer <access_token>
```

**路径参数:**
- `test_id`: 测试 ID

**响应:**
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "total_samples": 100,
    "control_samples": 70,
    "experiment_samples": 30,
    "control_avg_score": 80.5,
    "experiment_avg_score": 85.2,
    "improvement_rate": 5.84
  }
}
```

**字段说明:**
- `total_samples`: 总样本数
- `control_samples`: 对照组样本数
- `experiment_samples`: 实验组样本数
- `control_avg_score`: 对照组平均分
- `experiment_avg_score`: 实验组平均分
- `improvement_rate`: 提升百分比

---

### 8.5 Prompt 获取

#### 8.5.1 获取生效的 Prompt

**接口:** `GET /api/prompt-config/resolve/{config_name}`

**功能:** 获取生效的 Prompt，自动处理 A/B 测试分流

**Headers:**
```
Authorization: Bearer <access_token>
```

**路径参数:**
- `config_name`: 配置名称

**查询参数:**
- `user_id`: 用户 ID（用于一致性分流，可选）
- `session_id`: 会话 ID（用于一致性分流，可选）

**响应:**
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "config_id": 1,
    "config_name": "interview_questions",
    "version_id": 2,
    "version": "v1.1.0",
    "content": "Prompt 内容...",
    "is_ab_test": true,
    "ab_test_variant": "experiment",
    "ab_test_id": 1
  }
}
```

**字段说明:**
- `is_ab_test`: 是否来自 A/B 测试
- `ab_test_variant`: 变体类型（`control` 或 `experiment`）
- `ab_test_id`: A/B 测试 ID

---

### 8.6 初始化

#### 8.6.1 从文件系统初始化

**接口:** `POST /api/prompt-config/init-from-files`

**功能:** 将 `prompts/` 目录下的文件导入数据库

**Headers:**
```
Authorization: Bearer <access_token>
```

**响应:**
```json
{
  "code": 200,
  "message": "成功导入 15 个配置",
  "data": {
    "imported_count": 15
  }
}
```

---

## 9. 评估反馈模块 (`/api/evaluation`)

### 9.1 获取面试评估报告

**接口:** `GET /api/evaluation/report/{interview_id}`

**Headers:**
```
Authorization: Bearer <access_token>
```

**路径参数:**
- `interview_id`: 面试 ID

**响应:**
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "interview_id": 1,
    "total_score": 85,
    "overall_feedback": "整体评价",
    "strengths": [ ... ],
    "weaknesses": [ ... ],
    "category_scores": {
      "技术能力": 80,
      "沟通能力": 90,
      "问题解决": 85
    },
    "detailed_feedback": [
      {
        "question": "问题内容",
        "answer": "回答内容",
        "score": 85,
        "feedback": "反馈意见"
      }
    ],
    "recommended_resources": [
      {
        "type": "article",
        "title": "资源标题",
        "url": "https://example.com"
      }
    ],
    "created_at": "2025-01-20T10:00:00Z"
  }
}
```

---

## 10. 统计数据模块 (`/api/statistics`)

### 10.1 获取仪表盘统计数据

**接口:** `GET /api/statistics/dashboard`

**Headers:**
```
Authorization: Bearer <access_token>
```

**响应:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "resume_count": 3,
    "interview_count": 10,
    "knowledge_count": 5,
    "avg_score": 82,
    "recent_interviews": [
      {
        "id": 1,
        "job_description": "职位描述",
        "total_score": 85,
        "status": "completed",
        "created_at": "2025-01-20T10:00:00Z"
      }
    ]
  }
}
```

---

## 11. 系统接口

### 11.1 健康检查

**接口:** `GET /health`

**响应:**
```json
{
  "status": "healthy"
}
```

### 11.2 根路径

**接口:** `GET /`

**响应:**
```json
{
  "message": "智能面试提升系统 API",
  "version": "1.0.0"
}
```

---

## 错误码说明

| HTTP 状态码 | 说明 |
|-----------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未授权（需要登录） |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 注意事项

1. 所有需要认证的接口都需要在请求头中携带 `Authorization: Bearer <access_token>`
2. Token 有效期由后端配置决定，过期后需要重新登录
3. 文件上传有大小限制，具体限制请参考后端配置
4. WebSocket 连接需要保持长连接，断开后需要重新连接
5. 面试问题生成是异步操作，创建面试后需要轮询状态接口检查生成进度