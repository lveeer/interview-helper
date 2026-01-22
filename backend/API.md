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

## 3. 岗位匹配模块 (`/api/job`)

### 3.1 岗位匹配分析

**接口:** `POST /api/job/match`

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
    "matched_skills": [ ... ],
    "missing_skills": [ ... ],
    "suggestions": [ ... ]
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
  "knowledge_doc_ids": [1, 2, 3]
}
```

**响应:**
```json
{
  "code": 201,
  "message": "面试创建成功，正在生成面试问题，请稍后刷新查看",
  "data": {
    "id": 1,
    "user_id": 1,
    "resume_id": 1,
    "job_description": "职位描述",
    "status": "initializing",
    "total_score": null,
    "questions": [],
    "conversation": [],
    "created_at": "2025-01-20T10:00:00Z"
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
    "job_description": "职位描述",
    "status": "pending",
    "total_score": null,
    "questions": [
      {
        "id": 1,
        "question": "问题内容",
        "category": "技术",
        "difficulty": "中等"
      }
    ],
    "conversation": [],
    "created_at": "2025-01-20T10:00:00Z"
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
      "job_description": "职位描述",
      "status": "completed",
      "total_score": 85,
      "created_at": "2025-01-20T10:00:00Z"
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
        "timestamp": "2025-01-20T10:00:00Z"
      },
      {
        "role": "candidate",
        "content": "回答内容",
        "question_id": 1,
        "timestamp": "2025-01-20T10:00:00Z"
      }
    ],
    "created_at": "2025-01-20T10:00:00Z"
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

## 7. 评估反馈模块 (`/api/evaluation`)

### 6.1 获取面试评估报告

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

## 7. 统计数据模块 (`/api/statistics`)

### 7.1 获取仪表盘统计数据

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

## 8. 系统接口

### 8.1 健康检查

**接口:** `GET /health`

**响应:**
```json
{
  "status": "healthy"
}
```

### 8.2 根路径

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