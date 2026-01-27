# 简历找茬挑战游戏 - 需求文档

## 文档信息

| 项目 | 内容 |
|------|------|
| 文档版本 | v1.0 |
| 创建日期 | 2026-01-23 |
| 项目名称 | 简历找茬挑战游戏 |
| 产品类型 | 游戏化学习功能 |
| 目标用户 | 求职者、简历优化需求者 |

---

## 1. 项目概述

### 1.1 背景

当前用户在使用面试助手系统时，主要通过模拟面试和简历优化功能提升求职能力。然而，学习过程较为枯燥，用户粘性不足。引入游戏化元素可以提升用户参与度，在娱乐中学习简历优化技巧。

### 1.2 目标

- 提升用户日活和留存率
- 帮助用户掌握简历优化技巧
- 收集用户简历识别能力数据
- 为后续简历智能检测功能积累数据

### 1.3 核心价值

| 价值维度 | 描述 |
|----------|------|
| 用户价值 | 在游戏中学习简历优化，提升求职竞争力 |
| 产品价值 | 增加用户粘性，提升产品竞争力 |
| 数据价值 | 收集用户行为数据，优化个性化推荐 |

---

## 2. 功能需求

### 2.1 核心功能

#### 2.1.1 游戏开始

**功能描述：** 用户选择难度后，系统生成一份带错误的简历用于找茬

**输入参数：**
- `difficulty`: 难度级别（easy/medium/hard）
- `user_id`: 用户ID

**输出内容：**
- `session_id`: 游戏会话ID
- `resume`: 带错误的简历数据
- `error_count`: 错误总数
- `time_limit`: 时间限制（秒）

**业务规则：**
- 简单模式：3-5个错误，时间限制3分钟
- 中等模式：5-8个错误，时间限制5分钟
- 困难模式：8-12个错误，时间限制8分钟

---

#### 2.1.2 答题交互

**功能描述：** 用户点击简历中的错误位置，系统判断是否正确

**输入参数：**
- `session_id`: 游戏会话ID
- `location`: 点击位置（如：experience[1].description）

**输出内容：**
- `is_correct`: 是否正确
- `error_detail`: 错误详情（如果正确）
- `score`: 当前得分
- `remaining_errors`: 剩余错误数

**业务规则：**
- 找到错误：+10分
- 点错位置：-5分
- 同一错误重复点击：不扣分，提示已找到

---

#### 2.1.3 使用提示

**功能描述：** 用户遇到困难时可以使用提示功能

**输入参数：**
- `session_id`: 游戏会话ID

**输出内容：**
- `hint`: 提示内容
- `remaining_hints`: 剩余提示次数

**业务规则：**
- 每局游戏最多使用3次提示
- 使用提示：-3分
- 提示内容逐步详细：
  - 第1次：错误类型
  - 第2次：错误位置范围
  - 第3次：直接高亮错误位置

---

#### 2.1.4 提交答案

**功能描述：** 用户完成游戏后提交答案

**输入参数：**
- `session_id`: 游戏会话ID

**输出内容：**
- `final_score`: 最终得分
- `found_errors`: 找到的错误列表
- `missed_errors`: 未找到的错误列表
- `time_used`: 用时（秒）
- `achievements_unlocked`: 解锁的成就

**业务规则：**
- 时间奖励：30秒内+20分，60秒内+10分
- 完美通关（全找到且无提示）：额外+50分
- 自动保存游戏记录

---

#### 2.1.5 排行榜

**功能描述：** 展示用户排名和积分

**输入参数：**
- `period`: 时间周期（daily/weekly/monthly/all）
- `limit`: 返回数量

**输出内容：**
- `rankings`: 排行榜列表
  - `rank`: 排名
  - `user_id`: 用户ID
  - `username`: 用户名
  - `score`: 积分
  - `avatar`: 头像

**业务规则：**
- 每日排行榜：每天0点重置
- 每周排行榜：每周一0点重置
- 每月排行榜：每月1号0点重置
- 全局排行榜：永不重置

---

### 2.2 辅助功能

#### 2.2.1 游戏统计

**功能描述：** 展示用户游戏统计数据

**输出内容：**
- `total_games`: 总游戏次数
- `total_found`: 总找到错误数
- `total_score`: 总积分
- `win_rate`: 胜率（找到所有错误的次数/总次数）
- `best_time`: 最佳用时
- `current_streak`: 当前连胜次数
- `max_streak`: 最大连胜次数
- `weak_points`: 薄弱环节分析

---

#### 2.2.2 成就系统

**功能描述：** 用户完成特定条件后解锁成就

**成就列表：**

| 成就ID | 名称 | 描述 | 条件 | 图标 |
|--------|------|------|------|------|
| first_find | 初露锋芒 | 第一次找到简历错误 | 累计找到1个错误 | 🔍 |
| bug_hunter | 简历侦探 | 累计找到50个错误 | 累计找到50个错误 | 🕵️ |
| perfectionist | 完美主义者 | 连续3局完美通关 | 连续3局全找到且无提示 | ✨ |
| speed_demon | 闪电侠 | 困难模式快速通关 | 困难模式30秒内完成 | ⚡ |
| master | 简历大师 | 困难模式通关10次 | 困难模式获胜10次 | 👑 |
| streak_king | 连胜之王 | 连续获胜10次 | 连续获胜10次 | 🏆 |
| night_owl | 夜猫子 | 凌晨玩游戏 | 凌晨0-6点完成游戏 | 🦉 |

---

#### 2.2.3 错误类型学习

**功能描述：** 展示所有错误类型的详细说明和正确写法

**输出内容：**
- `error_types`: 错误类型列表
  - `type_id`: 类型ID
  - `name`: 名称
  - `description`: 描述
  - `example`: 错误示例
  - `correct`: 正确写法
  - `tips`: 优化建议

---

## 3. 非功能需求

### 3.1 性能要求

| 指标 | 要求 |
|------|------|
| 游戏生成响应时间 | < 3秒 |
| 答题判断响应时间 | < 500ms |
| 排行榜查询响应时间 | < 1秒 |
| 并发支持 | 支持100+用户同时游戏 |

### 3.2 可用性要求

| 指标 | 要求 |
|------|------|
| 系统可用性 | 99.5% |
| 数据持久化 | 游戏记录永久保存 |
| 跨平台支持 | 支持PC和移动端浏览器 |

### 3.3 安全要求

| 指标 | 要求 |
|------|------|
| 用户认证 | 需要登录才能游戏 |
| 数据隔离 | 用户数据完全隔离 |
| 防作弊 | 服务端验证答案，防止前端作弊 |

---

## 4. 用户故事

### 4.1 核心用户故事

| ID | 用户故事 | 优先级 |
|----|----------|--------|
| US1 | 作为求职者，我想通过找茬游戏学习简历优化，以便提升求职竞争力 | P0 |
| US2 | 作为玩家，我想选择不同难度，以便逐步提升能力 | P0 |
| US3 | 作为玩家，我想查看排行榜，以便与其他玩家竞争 | P1 |
| US4 | 作为玩家，我想使用提示功能，以便在遇到困难时获得帮助 | P1 |
| US5 | 作为玩家，我想查看我的游戏统计，以便了解自己的进步 | P2 |
| US6 | 作为玩家，我想解锁成就，以便获得成就感 | P2 |

### 4.2 用户故事详情

#### US1: 求职者学习简历优化

**作为** 求职者
**我想要** 通过找茬游戏学习简历优化
**以便** 提升求职竞争力

**验收标准：**
- [ ] 用户可以开始新的游戏
- [ ] 系统生成带错误的简历
- [ ] 用户点击错误位置后获得正确答案和解释
- [ ] 游戏完成后显示总结报告

---

## 5. 错误类型定义

### 5.1 格式类错误

| 类型ID | 名称 | 描述 | 示例 |
|--------|------|------|------|
| format_inconsistency | 格式不一致 | 日期、电话等格式不统一 | 2023.01 / 2023-01 混用 |
| spacing_issue | 间距问题 | 段落间距不一致 | 项目描述间距混乱 |
| font_mismatch | 字体混用 | 中英文字体不统一 | 中文字体与英文不匹配 |

### 5.2 内容类错误

| 类型ID | 名称 | 描述 | 示例 |
|--------|------|------|------|
| vague_description | 描述空洞 | 缺少量化数据 | "负责项目开发，提升了系统性能" |
| missing_quantification | 缺少量化成果 | 没有具体数字 | "用户增长显著" |
| action_verb_weak | 动词力度弱 | 使用被动或弱动词 | "参与了项目" |

### 5.3 逻辑类错误

| 类型ID | 名称 | 描述 | 示例 |
|--------|------|------|------|
| timeline_conflict | 时间线冲突 | 工作时间重叠 | 2020-2022在A公司，同时2021-2023在B公司 |
| skill_experience_mismatch | 技能与经历不匹配 | 技能与项目经历不符 | 技能写精通Python，但工作经历全是Java |
| education_work_gap | 学历与工作年限矛盾 | 时间逻辑有问题 | 2023年毕业，但有5年工作经验 |

### 5.4 专业性错误

| 类型ID | 名称 | 描述 | 示例 |
|--------|------|------|------|
| negative_language | 负面语言 | 抱怨前公司或项目 | "前公司管理混乱，项目失败" |
| over_claim | 过度夸大 | 与职位级别不符 | "主导千万级项目，影响亿级用户" |
| discriminatory_terms | 歧视性词汇 | 违反就业平等原则 | "年轻团队、男性优先" |

---

## 6. 数据库设计

### 6.1 游戏会话表

```sql
CREATE TABLE resume_finder_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    difficulty VARCHAR(20) NOT NULL,  -- easy/medium/hard
    buggy_resume JSONB NOT NULL,       -- 带错误的简历
    errors JSONB NOT NULL,             -- 错误列表
    status VARCHAR(20) DEFAULT 'in_progress',  -- in_progress/completed/abandoned
    score INTEGER DEFAULT 0,
    found_errors INTEGER DEFAULT 0,
    hints_used INTEGER DEFAULT 0,
    time_limit INTEGER NOT NULL,
    time_used INTEGER DEFAULT 0,
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_resume_finder_user_id ON resume_finder_sessions(user_id);
CREATE INDEX idx_resume_finder_status ON resume_finder_sessions(status);
CREATE INDEX idx_resume_finder_created_at ON resume_finder_sessions(created_at DESC);
```

### 6.2 用户积分表

```sql
CREATE TABLE user_points (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE REFERENCES users(id),
    total_score INTEGER DEFAULT 0,
    daily_score INTEGER DEFAULT 0,
    weekly_score INTEGER DEFAULT 0,
    monthly_score INTEGER DEFAULT 0,
    total_games INTEGER DEFAULT 0,
    total_found INTEGER DEFAULT 0,
    best_score INTEGER DEFAULT 0,
    best_time INTEGER DEFAULT 0,
    current_streak INTEGER DEFAULT 0,
    max_streak INTEGER DEFAULT 0,
    last_played_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 6.3 用户成就表

```sql
CREATE TABLE user_achievements (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    achievement_id VARCHAR(50) NOT NULL,
    earned_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, achievement_id)
);

CREATE INDEX idx_user_achievements_user_id ON user_achievements(user_id);
```

### 6.4 排行榜快照表

```sql
CREATE TABLE leaderboard_snapshots (
    id SERIAL PRIMARY KEY,
    period VARCHAR(20) NOT NULL,  -- daily/weekly/monthly
    snapshot_date DATE NOT NULL,
    rankings JSONB NOT NULL,       -- 排名数据
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(period, snapshot_date)
);
```

---

## 7. API设计

### 7.1 游戏管理接口

#### 7.1.1 开始游戏

```
POST /api/game/resume-finder/start
```

**请求体：**
```json
{
  "difficulty": "medium"
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
      "skills": [...]
    },
    "error_count": 5,
    "time_limit": 300,
    "started_at": "2026-01-23T10:00:00Z"
  }
}
```

---

#### 7.1.2 提交答案

```
POST /api/game/resume-finder/submit
```

**请求体：**
```json
{
  "session_id": 1,
  "location": "experience[1].description"
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
      "id": 1,
      "type": "vague_description",
      "hint": "缺少量化数据，应该用具体数字说明成果",
      "correct_text": "负责项目开发，优化数据库查询，将响应时间从2s降低到0.5s"
    },
    "score": 10,
    "remaining_errors": 4
  }
}
```

---

#### 7.1.3 使用提示

```
POST /api/game/resume-finder/hint
```

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

---

#### 7.1.4 完成游戏

```
POST /api/game/resume-finder/complete
```

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
    "found_errors": 5,
    "missed_errors": 0,
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

---

### 7.2 统计与排行榜接口

#### 7.2.1 获取用户统计

```
GET /api/game/resume-finder/stats
```

**响应：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total_games": 25,
    "total_found": 120,
    "total_score": 1850,
    "win_rate": 0.72,
    "best_time": 45,
    "current_streak": 5,
    "max_streak": 10,
    "weak_points": [
      {
        "type": "vague_description",
        "detection_rate": 0.65,
        "suggestion": "多关注量化数据的表达"
      }
    ]
  }
}
```

---

#### 7.2.2 获取排行榜

```
GET /api/game/resume-finder/leaderboard?period=weekly&limit=10
```

**响应：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "period": "weekly",
    "rankings": [
      {
        "rank": 1,
        "user_id": 1,
        "username": "求职达人",
        "score": 520,
        "avatar": "https://..."
      },
      {
        "rank": 2,
        "user_id": 2,
        "username": "简历专家",
        "score": 480,
        "avatar": "https://..."
      }
    ],
    "my_rank": 15,
    "my_score": 320
  }
}
```

---

#### 7.2.3 获取成就列表

```
GET /api/game/resume-finder/achievements
```

**响应：**
```json
{
  "code": 200,
  "message": "success",
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

---

## 8. 技术方案

### 8.1 技术架构

```
┌─────────────────────────────────────────────┐
│              前端 (React + TypeScript)      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ 游戏界面 │  │ 排行榜   │  │ 统计页面 │  │
│  └──────────┘  └──────────┘  └──────────┘  │
└─────────────────────────────────────────────┘
                    ↓ HTTP/WebSocket
┌─────────────────────────────────────────────┐
│           后端 (FastAPI + Python)           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ 游戏服务 │  │ LLM服务  │  │ 数据服务 │  │
│  └──────────┘  └──────────┘  └──────────┘  │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│         数据库 (PostgreSQL + pgvector)      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ 游戏数据 │  │ 用户数据 │  │ 简历数据 │  │
│  └──────────┘  └──────────┘  └──────────┘  │
└─────────────────────────────────────────────┘
```

### 8.2 核心模块

#### 8.2.1 游戏服务 (game_service.py)

**职责：**
- 生成带错误的简历
- 验证用户答案
- 计算游戏得分
- 管理游戏会话

**核心方法：**
```python
class ResumeFinderService:
    async def generate_buggy_resume(user_id, difficulty)
    async def check_answer(session_id, location)
    async def get_hint(session_id)
    async def complete_game(session_id)
    async def get_user_stats(user_id)
    async def get_leaderboard(period, limit)
```

---

#### 8.2.2 LLM集成

**职责：**
- 生成带错误的简历
- 生成错误解释
- 生成个性化建议

**Prompt模板：**
```
prompts/
├── buggy_resume_generation.txt
├── error_explanation.txt
└── improvement_suggestion.txt
```

---

### 8.3 性能优化

#### 8.3.1 缓存策略

- **排行榜缓存：** Redis缓存排行榜数据，5分钟更新
- **用户统计缓存：** 缓存用户统计数据，1分钟更新
- **简历模板缓存：** 缓存常用简历模板，减少LLM调用

#### 8.3.2 数据库优化

- **索引优化：** 为user_id、status、created_at创建索引
- **分页查询：** 排行榜使用分页，避免全表扫描
- **数据归档：** 定期归档历史游戏数据

---

## 9. 测试计划

### 9.1 单元测试

| 模块 | 测试用例数 | 覆盖率目标 |
|------|-----------|-----------|
| 游戏服务 | 20 | 90% |
| LLM集成 | 10 | 80% |
| 数据服务 | 15 | 85% |

### 9.2 集成测试

| 测试场景 | 测试内容 |
|----------|----------|
| 完整游戏流程 | 开始游戏→答题→完成→统计 |
| 排行榜更新 | 游戏完成后排行榜实时更新 |
| 成就解锁 | 达成条件后自动解锁成就 |

### 9.3 性能测试

| 测试项 | 目标 |
|--------|------|
| 并发用户 | 100+用户同时游戏 |
| 响应时间 | 游戏生成<3秒，答题判断<500ms |
| 数据库查询 | 排行榜查询<1秒 |

---

## 10. 上线计划

### 10.1 开发阶段

| 阶段 | 时间 | 任务 |
|------|------|------|
| 第一阶段 | Week 1 | 数据库设计、游戏服务开发 |
| 第二阶段 | Week 2 | API开发、LLM集成 |
| 第三阶段 | Week 3 | 前端开发、联调测试 |
| 第四阶段 | Week 4 | 性能优化、Bug修复 |

### 10.2 灰度发布

| 阶段 | 用户比例 | 时间 |
|------|----------|------|
| 灰度1 | 5% | 3天 |
| 灰度2 | 20% | 3天 |
| 灰度3 | 50% | 3天 |
| 全量 | 100% | - |

### 10.3 监控指标

| 指标 | 目标 |
|------|------|
| 日活用户 | +20% |
| 平均游戏时长 | 5分钟 |
| 游戏完成率 | 70% |
| 用户满意度 | 4.5/5.0 |

---

## 11. 风险与应对

### 11.1 技术风险

| 风险 | 概率 | 影响 | 应对措施 |
|------|------|------|----------|
| LLM生成质量不稳定 | 中 | 高 | 多轮验证，错误类型库兜底 |
| 并发性能不足 | 低 | 中 | 缓存优化，数据库索引优化 |
| 前端兼容性问题 | 低 | 低 | 多浏览器测试，降级方案 |

### 11.2 产品风险

| 风险 | 概率 | 影响 | 应对措施 |
|------|------|------|----------|
| 用户参与度低 | 中 | 高 | 引入奖励机制，社交分享 |
| 游戏难度不合适 | 中 | 中 | 动态难度调整，用户反馈收集 |

---

## 12. 后续迭代

### 12.1 V1.1 规划

- 多人对战模式
- 真实简历案例库
- AI简历医生功能

### 12.2 V2.0 规划

- 视频简历找茬
- 语音交互支持
- 行业定制化错误类型

---

## 13. 附录

### 13.1 术语表

| 术语 | 解释 |
|------|------|
| 简历找茬 | 用户在简历中找出错误的互动游戏 |
| 错误类型 | 简历中常见的错误分类 |
| 游戏会话 | 一次完整的游戏过程 |
| 成就系统 | 用户完成特定条件后获得的奖励 |

### 13.2 参考资料

- [现有系统API文档](./API.md)
- [简历优化服务文档](./README.md)
- [LLM服务文档](./app/services/llm_service.py)

---

**文档结束**