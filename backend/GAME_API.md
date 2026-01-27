# 简历找茬游戏 API 文档

## 概述

简历找茬游戏是一个游戏化的简历优化学习功能，用户通过在简历中找出错误来学习简历优化技巧。

## 认证

所有API端点都需要用户认证（JWT Token）。

## API 端点

### 1. 开始游戏

**端点：** `POST /api/game/resume-finder/start`

**请求体：**
```json
{
  "difficulty": "medium"  // easy/medium/hard
}
```

**响应：**
```json
{
  "code": 200,
  "message": "游戏创建成功",
  "data": {
    "session_id": 1,
    "resume": {
      "personal_info": {...},
      "education": [...],
      "experience": [...],
      "skills": [...],
      "projects": [...]
    },
    "error_count": 5,
    "time_limit": 300,
    "started_at": "2026-01-23T10:00:00Z"
  }
}
```

**难度配置：**
- 简单（easy）：3-5个错误，时间限制3分钟
- 中等（medium）：5-8个错误，时间限制5分钟
- 困难（hard）：8-12个错误，时间限制8分钟

---

### 2. 提交答案

**端点：** `POST /api/game/resume-finder/submit`

**请求体：**
```json
{
  "session_id": 1,
  "location": "experience[0].description"
}
```

**响应：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "is_correct": true,
    "error_detail": {
      "id": 0,
      "type": "vague_description",
      "location": "experience[0].description",
      "hint": "使用具体数字说明成果",
      "correct_text": "主导了后端系统开发，优化数据库查询，将响应时间从2s降低到0.5s，用户从10万增长到50万"
    },
    "score": 10,
    "remaining_errors": 4
  }
}
```

**计分规则：**
- 找到错误：+10分
- 点错位置：-5分
- 同一错误重复点击：不扣分

---

### 3. 使用提示

**端点：** `POST /api/game/resume-finder/hint`

**请求体：**
```json
{
  "session_id": 1
}
```

**响应：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "hint": "错误类型：描述空洞",
    "remaining_hints": 2,
    "score": -3
  }
}
```

**提示规则：**
- 每局游戏最多使用3次提示
- 使用提示：-3分
- 提示逐步详细：
  - 第1次：错误类型
  - 第2次：错误位置范围
  - 第3次：直接高亮错误位置

---

### 4. 完成游戏

**端点：** `POST /api/game/resume-finder/complete`

**请求体：**
```json
{
  "session_id": 1
}
```

**响应：**
```json
{
  "code": 200,
  "message": "游戏完成",
  "data": {
    "final_score": 85,
    "found_errors": [...],
    "missed_errors": [...],
    "time_used": 180,
    "achievements_unlocked": [
      {
        "id": "perfectionist",
        "name": "完美主义者",
        "icon": "✨"
      }
    ],
    "rank_change": "+3"
  }
}
```

**奖励规则：**
- 时间奖励：30秒内+20分，60秒内+10分
- 完美通关（全找到且无提示）：额外+50分

---

### 5. 获取用户统计

**端点：** `GET /api/game/resume-finder/stats`

**响应：**
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "total_games": 25,
    "total_found": 120,
    "total_score": 1850,
    "win_rate": 0.72,
    "best_time": 45,
    "current_streak": 5,
    "max_streak": 10,
    "weak_points": [...]
  }
}
```

---

### 6. 获取排行榜

**端点：** `GET /api/game/resume-finder/leaderboard`

**查询参数：**
- `period`: 时间周期（daily/weekly/monthly/all）
- `limit`: 返回数量（默认10）

**响应：**
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "period": "weekly",
    "rankings": [
      {
        "rank": 1,
        "user_id": 1,
        "username": "求职达人",
        "score": 520,
        "avatar": "https://..."
      }
    ],
    "my_rank": 15,
    "my_score": 320
  }
}
```

**排行榜周期：**
- 每日排行榜：每天0点重置
- 每周排行榜：每周一0点重置
- 每月排行榜：每月1号0点重置
- 全局排行榜：永不重置

---

### 7. 获取成就列表

**端点：** `GET /api/game/resume-finder/achievements`

**响应：**
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "total": 7,
    "unlocked": 3,
    "achievements": [
      {
        "id": "first_find",
        "name": "初露锋芒",
        "description": "第一次找到简历错误",
        "icon": "🔍",
        "unlocked": true,
        "unlocked_at": "2026-01-20T10:00:00Z"
      },
      {
        "id": "bug_hunter",
        "name": "简历侦探",
        "description": "累计找到50个错误",
        "icon": "🕵️",
        "unlocked": false,
        "progress": 35,
        "total": 50
      }
    ]
  }
}
```

**成就列表：**

| 成就ID | 名称 | 描述 | 图标 |
|--------|------|------|------|
| first_find | 初露锋芒 | 第一次找到简历错误 | 🔍 |
| bug_hunter | 简历侦探 | 累计找到50个错误 | 🕵️ |
| perfectionist | 完美主义者 | 连续3局完美通关 | ✨ |
| speed_demon | 闪电侠 | 困难模式快速通关 | ⚡ |
| master | 简历大师 | 困难模式通关10次 | 👑 |
| streak_king | 连胜之王 | 连续获胜10次 | 🏆 |
| night_owl | 夜猫子 | 凌晨玩游戏 | 🦉 |

---

### 8. 获取错误类型列表

**端点：** `GET /api/game/resume-finder/error-types`

**响应：**
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "error_types": [
      {
        "type_id": "vague_description",
        "name": "描述空洞",
        "description": "缺乏量化数据",
        "example": "负责项目开发，提升了系统性能",
        "correct": "负责项目开发，优化数据库查询，将响应时间从2s降低到0.5s",
        "tips": "使用具体数字说明成果"
      }
    ]
  }
}
```

**错误类型分类：**

#### 格式类错误
- 格式不一致：日期、电话等格式不统一
- 间距问题：段落间距不一致
- 字体混用：中英文字体不统一

#### 内容类错误
- 描述空洞：缺乏量化数据
- 缺少量化成果：没有具体数字
- 动词力度弱：使用被动或弱动词

#### 逻辑类错误
- 时间线冲突：工作时间重叠
- 技能与经历不匹配：技能与项目经历不符
- 学历与工作年限矛盾：时间逻辑有问题

#### 专业性错误
- 负面语言：抱怨前公司或项目
- 过度夸大：与职位级别不符
- 歧视性词汇：违反就业平等原则

---

## 数据库表结构

### 1. resume_finder_sessions（游戏会话表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| user_id | Integer | 用户ID |
| difficulty | String(20) | 难度级别 |
| buggy_resume | JSON | 带错误的简历 |
| errors | JSON | 错误列表 |
| status | String(20) | 游戏状态 |
| score | Integer | 得分 |
| found_errors | Integer | 找到的错误数 |
| hints_used | Integer | 使用的提示次数 |
| time_limit | Integer | 时间限制（秒） |
| time_used | Integer | 用时（秒） |
| started_at | DateTime | 开始时间 |
| completed_at | DateTime | 完成时间 |

### 2. user_points（用户积分表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| user_id | Integer | 用户ID（唯一） |
| total_score | Integer | 总积分 |
| daily_score | Integer | 日积分 |
| weekly_score | Integer | 周积分 |
| monthly_score | Integer | 月积分 |
| total_games | Integer | 总游戏次数 |
| total_found | Integer | 总找到错误数 |
| best_score | Integer | 最佳得分 |
| best_time | Integer | 最佳用时 |
| current_streak | Integer | 当前连胜 |
| max_streak | Integer | 最大连胜 |

### 3. user_achievements（用户成就表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| user_id | Integer | 用户ID |
| achievement_id | String(50) | 成就ID |
| earned_at | DateTime | 获得时间 |

### 4. leaderboard_snapshots（排行榜快照表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| period | String(20) | 周期（daily/weekly/monthly） |
| snapshot_date | Date | 快照日期 |
| rankings | JSON | 排名数据 |

---

## 使用示例

### 完整游戏流程

```bash
# 1. 开始游戏
curl -X POST http://localhost:8000/api/game/resume-finder/start \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"difficulty": "medium"}'

# 2. 提交答案
curl -X POST http://localhost:8000/api/game/resume-finder/submit \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"session_id": 1, "location": "experience[0].description"}'

# 3. 使用提示（可选）
curl -X POST http://localhost:8000/api/game/resume-finder/hint \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"session_id": 1}'

# 4. 完成游戏
curl -X POST http://localhost:8000/api/game/resume-finder/complete \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"session_id": 1}'

# 5. 查看统计
curl -X GET http://localhost:8000/api/game/resume-finder/stats \
  -H "Authorization: Bearer <token>"

# 6. 查看排行榜
curl -X GET http://localhost:8000/api/game/resume-finder/leaderboard?period=weekly&limit=10 \
  -H "Authorization: Bearer <token>"

# 7. 查看成就
curl -X GET http://localhost:8000/api/game/resume-finder/achievements \
  -H "Authorization: Bearer <token>"
```

---

## 技术实现

### 文件结构

```
backend/
├── alembic/versions/
│   └── 20260123_1000_add_resume_finder_game_tables.py  # 数据库迁移
├── app/
│   ├── models/
│   │   └── game.py                                     # 数据模型
│   ├── schemas/
│   │   └── game.py                                     # API Schema
│   ├── api/
│   │   └── game.py                                     # API路由
│   └── services/
│       └── game_service.py                             # 游戏服务
├── prompts/
│   ├── buggy_resume_generation.txt                     # 简历生成Prompt
│   ├── error_explanation.txt                           # 错误解释Prompt
│   └── improvement_suggestion.txt                      # 改进建议Prompt
└── main.py                                             # 主应用（已注册路由）
```

### 核心功能

1. **游戏会话管理**
   - 创建游戏会话
   - 生成带错误的简历
   - 管理游戏状态

2. **答案验证**
   - 验证用户点击位置
   - 计算得分
   - 提供错误详情

3. **提示系统**
   - 分级提示（3级）
   - 提示次数限制
   - 提示扣分机制

4. **成就系统**
   - 7个成就类型
   - 自动解锁机制
   - 进度追踪

5. **排行榜**
   - 多周期排行榜（日/周/月/全局）
   - 排名变化追踪
   - 快照机制

6. **统计分析**
   - 用户游戏统计
   - 薄弱环节分析
   - 学习建议

---

## 后续优化

### V1.1 规划
- 多人对战模式
- 真实简历案例库
- AI简历医生功能

### V2.0 规划
- 视频简历找茬
- 语音交互支持
- 行业定制化错误类型

---

## 注意事项

1. 所有API端点都需要JWT认证
2. 游戏会话有超时机制（根据难度设置）
3. 排行榜定期重置（日/周/月）
4. 成就解锁后无法重复获得
5. 提示功能每局游戏限制3次

---

## 联系方式

如有问题或建议，请联系开发团队。