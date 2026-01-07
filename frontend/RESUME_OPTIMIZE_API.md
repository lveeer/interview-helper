# 简历优化功能 API 文档

## 基础信息

- **Base URL**: `/api`
- **Content-Type**: `application/json`
- **认证方式**: Bearer Token

---

## 1. 分析简历

**接口描述**: 对指定简历进行智能分析，生成多维度评分和分析报告

**请求方式**: `POST`

**请求路径**: `/resume/{id}/analyze`

**路径参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | integer | 是 | 简历ID |

**请求示例**:
```http
POST /api/resume/1/analyze
Authorization: Bearer {token}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "分析成功",
  "data": {
    "overall_score": 72,
    "content_score": 75,
    "match_score": 68,
    "clarity_score": 74,
    "strengths": [
      "工作经历描述详细，有具体的项目经验",
      "技能列表清晰，涵盖多个技术栈",
      "教育背景信息完整"
    ],
    "weaknesses": [
      "缺少量化成果和数据支撑",
      "自我评价部分过于简单",
      "部分项目描述缺少技术细节"
    ],
    "personal_analysis": {
      "status": "good",
      "message": "个人信息完整",
      "included": ["姓名", "联系方式", "邮箱"],
      "missing": []
    },
    "education_analysis": {
      "status": "good",
      "message": "教育背景清晰",
      "suggestions": "建议添加在校期间的重要课程或获奖经历"
    },
    "experience_analysis": {
      "status": "warning",
      "message": "工作经历描述需要优化",
      "issues": "部分工作经历缺乏量化成果，项目描述不够具体",
      "suggestions": "建议使用STAR法则描述项目经历，添加具体的数据和成果"
    },
    "skills_analysis": {
      "status": "good",
      "message": "技能描述清晰",
      "hard_skills": ["JavaScript", "Vue.js", "Python", "MySQL"],
      "soft_skills": ["团队协作", "沟通能力", "问题解决"],
      "suggestions": "建议添加技能熟练度等级"
    }
  }
}
```

**响应字段说明**:
| 字段 | 类型 | 说明 |
|------|------|------|
| overall_score | integer | 综合评分（0-100） |
| content_score | integer | 内容完整性评分（0-100） |
| match_score | integer | 专业匹配度评分（0-100） |
| clarity_score | integer | 表达清晰度评分（0-100） |
| strengths | array<string> | 简历优势列表 |
| weaknesses | array<string> | 需要改进项列表 |
| personal_analysis | object | 个人信息分析 |
| education_analysis | object | 教育背景分析 |
| experience_analysis | object | 工作经历分析 |
| skills_analysis | object | 技能分析 |

---

## 2. 获取优化建议

**接口描述**: 获取指定简历的优化建议列表

**请求方式**: `GET`

**请求路径**: `/resume/{id}/suggestions`

**路径参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | integer | 是 | 简历ID |

**请求示例**:
```http
GET /api/resume/1/suggestions
Authorization: Bearer {token}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "获取成功",
  "data": [
    {
      "id": 1,
      "priority": "high",
      "title": "添加量化成果",
      "description": "在工作经历中添加具体的数字和成果，如\"提升性能50%\"、\"管理10人团队\"等",
      "before": "负责项目开发，提升了系统性能",
      "after": "负责核心模块开发，通过优化数据库查询和缓存策略，将系统响应时间从500ms降低到250ms，性能提升50%",
      "reason": "量化成果能让HR更直观地了解你的能力和贡献"
    },
    {
      "id": 2,
      "priority": "high",
      "title": "优化项目描述",
      "description": "使用STAR法则（情境-任务-行动-结果）重新组织项目经历",
      "before": "参与了电商平台的开发",
      "after": "在电商平台项目中（情境），负责用户模块开发（任务），使用Vue.js和Node.js构建了完整的用户注册登录功能（行动），支持日均10万+用户访问（结果）",
      "reason": "STAR法则能让项目经历更有条理，突出你的贡献和成果"
    },
    {
      "id": 3,
      "priority": "medium",
      "title": "丰富自我评价",
      "description": "在自我评价中添加更多个人特质和职业目标",
      "before": "吃苦耐劳，积极向上",
      "after": "拥有5年前端开发经验，擅长Vue.js生态，对性能优化有深入研究。具备良好的团队协作能力，曾带领5人小组完成多个项目。目标是成为一名全栈开发工程师，持续学习新技术",
      "reason": "详细的自我评价能展现你的职业规划和个人特色"
    }
  ]
}
```

**响应字段说明**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | integer | 建议ID |
| priority | string | 优先级：high（重要）、medium（中等）、low（建议） |
| title | string | 建议标题 |
| description | string | 建议描述 |
| before | string | 优化前的内容（可选） |
| after | string | 优化后的内容（可选） |
| reason | string | 优化原因说明 |

---

## 3. 应用优化建议

**接口描述**: 将选中的优化建议应用到简历中

**请求方式**: `POST`

**请求路径**: `/resume/{id}/optimize`

**路径参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | integer | 是 | 简历ID |

**请求体**:
```json
{
  "suggestions": [
    {
      "id": 1,
      "priority": "high",
      "title": "添加量化成果",
      "description": "在工作经历中添加具体的数字和成果",
      "before": "负责项目开发，提升了系统性能",
      "after": "负责核心模块开发，通过优化数据库查询和缓存策略，将系统响应时间从500ms降低到250ms，性能提升50%",
      "reason": "量化成果能让HR更直观地了解你的能力和贡献"
    }
  ]
}
```

**请求示例**:
```http
POST /api/resume/1/optimize
Authorization: Bearer {token}
Content-Type: application/json

{
  "suggestions": [
    {
      "id": 1,
      "priority": "high",
      "title": "添加量化成果",
      "description": "在工作经历中添加具体的数字和成果",
      "before": "负责项目开发，提升了系统性能",
      "after": "负责核心模块开发，通过优化数据库查询和缓存策略，将系统响应时间从500ms降低到250ms，性能提升50%",
      "reason": "量化成果能让HR更直观地了解你的能力和贡献"
    }
  ]
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "优化应用成功",
  "data": {
    "version": "v2.0",
    "optimized_at": "2026-01-07T15:30:00Z",
    "applied_count": 1
  }
}
```

**响应字段说明**:
| 字段 | 类型 | 说明 |
|------|------|------|
| version | string | 新版本号 |
| optimized_at | string | 优化时间（ISO 8601格式） |
| applied_count | integer | 应用的建议数量 |

---

## 4. 获取优化历史

**接口描述**: 获取指定简历的优化历史记录

**请求方式**: `GET`

**请求路径**: `/resume/{id}/optimization-history`

**路径参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | integer | 是 | 简历ID |

**请求示例**:
```http
GET /api/resume/1/optimization-history
Authorization: Bearer {token}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "获取成功",
  "data": [
    {
      "id": 1,
      "version": "v2.0",
      "version_before": "v1.0",
      "version_after": "v2.0",
      "title": "应用优化建议",
      "description": "应用了1条优化建议：添加量化成果",
      "status": "success",
      "created_at": "2026-01-07T15:30:00Z"
    },
    {
      "id": 2,
      "version": "v1.0",
      "version_before": null,
      "version_after": "v1.0",
      "title": "初始上传",
      "description": "简历首次上传",
      "status": "success",
      "created_at": "2026-01-07T10:00:00Z"
    }
  ]
}
```

**响应字段说明**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | integer | 历史记录ID |
| version | string | 当前版本号 |
| version_before | string | 优化前版本号 |
| version_after | string | 优化后版本号 |
| title | string | 操作标题 |
| description | string | 操作描述 |
| status | string | 状态：success、failed |
| created_at | string | 创建时间（ISO 8601格式） |

---

## 5. 导出优化后的简历

**接口描述**: 导出优化后的简历文件

**请求方式**: `GET`

**请求路径**: `/resume/{id}/export`

**路径参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | integer | 是 | 简历ID |

**查询参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| format | string | 否 | 导出格式：pdf（默认）、docx |

**请求示例**:
```http
GET /api/resume/1/export?format=pdf
Authorization: Bearer {token}
```

**响应**:
- **Content-Type**: `application/pdf` 或 `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
- **Content-Disposition**: `attachment; filename="optimized_resume.pdf"`

---

## 6. 比较简历版本

**接口描述**: 比较两个版本的简历差异

**请求方式**: `GET`

**请求路径**: `/resume/{id}/compare`

**路径参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | integer | 是 | 简历ID |

**查询参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| version1 | string | 是 | 版本1 |
| version2 | string | 是 | 版本2 |

**请求示例**:
```http
GET /api/resume/1/compare?version1=v1.0&version2=v2.0
Authorization: Bearer {token}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "对比成功",
  "data": {
    "before": "负责项目开发，提升了系统性能",
    "after": "负责核心模块开发，通过优化数据库查询和缓存策略，将系统响应时间从500ms降低到250ms，性能提升50%",
    "diff": [
      {
        "type": "modified",
        "section": "工作经历",
        "content": {
          "old": "负责项目开发，提升了系统性能",
          "new": "负责核心模块开发，通过优化数据库查询和缓存策略，将系统响应时间从500ms降低到250ms，性能提升50%"
        }
      }
    ]
  }
}
```

**响应字段说明**:
| 字段 | 类型 | 说明 |
|------|------|------|
| before | string | 版本1的完整内容 |
| after | string | 版本2的完整内容 |
| diff | array<object> | 差异详情 |
| diff[].type | string | 差异类型：added、deleted、modified |
| diff[].section | string | 差异所在章节 |
| diff[].content | object | 差异内容详情 |

---

## 7. 恢复到历史版本

**接口描述**: 将简历恢复到指定的历史版本

**请求方式**: `POST`

**请求路径**: `/resume/{id}/restore`

**路径参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | integer | 是 | 简历ID |

**请求体**:
```json
{
  "version": "v1.0"
}
```

**请求示例**:
```http
POST /api/resume/1/restore
Authorization: Bearer {token}
Content-Type: application/json

{
  "version": "v1.0"
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "恢复成功",
  "data": {
    "version": "v1.0",
    "restored_at": "2026-01-07T16:00:00Z"
  }
}
```

**响应字段说明**:
| 字段 | 类型 | 说明 |
|------|------|------|
| version | string | 恢复到的版本号 |
| restored_at | string | 恢复时间（ISO 8601格式） |

---

## 错误码说明

| 错误码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## 通用响应格式

所有接口均遵循以下响应格式：

```json
{
  "code": 200,
  "message": "操作成功",
  "data": {}
}
```

**字段说明**:
| 字段 | 类型 | 说明 |
|------|------|------|
| code | integer | 响应状态码 |
| message | string | 响应消息 |
| data | object/array/null | 响应数据 |