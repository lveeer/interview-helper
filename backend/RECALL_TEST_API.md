# 召回测试功能 - 前端对接文档

## 概述

召回测试功能用于评估知识库检索系统的性能，通过创建测试用例并执行测试，计算召回率、精确率、F1 分数和 MRR 等指标。

## API 基础信息

- **Base URL**: `http://localhost:8000`
- **认证方式**: Bearer Token (JWT)
- **所有接口需要在请求头中携带**: `Authorization: Bearer <access_token>`

---

## 1. 创建召回测试用例

### 接口信息
- **URL**: `POST /api/knowledge/recall-test/cases`
- **Content-Type**: `application/json`

### 请求参数

```typescript
interface RecallTestCaseCreate {
  query: string;                    // 测试查询语句
  expected_chunk_ids: number[];     // 期望召回的分段 ID 列表
  description?: string;             // 测试用例描述（可选）
}
```

### 请求示例

```javascript
const createTestCase = async () => {
  const response = await fetch('http://localhost:8000/api/knowledge/recall-test/cases', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      query: '什么是 Python 的装饰器？',
      expected_chunk_ids: [1, 2, 3],
      description: '测试关于 Python 装饰器知识的召回效果'
    })
  });
  return await response.json();
};
```

### 响应示例

```json
{
  "code": 201,
  "message": "测试用例创建成功",
  "data": {
    "id": 1,
    "user_id": 1,
    "query": "什么是 Python 的装饰器？",
    "expected_chunk_ids": [1, 2, 3],
    "description": "测试关于 Python 装饰器知识的召回效果",
    "created_at": "2026-01-22T10:00:00Z"
  }
}
```

---

## 2. 获取召回测试用例列表

### 接口信息
- **URL**: `GET /api/knowledge/recall-test/cases`

### 请求示例

```javascript
const getTestCases = async () => {
  const response = await fetch('http://localhost:8000/api/knowledge/recall-test/cases', {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  return await response.json();
};
```

### 响应示例

```json
{
  "code": 200,
  "message": "获取成功",
  "data": [
    {
      "id": 1,
      "user_id": 1,
      "query": "什么是 Python 的装饰器？",
      "expected_chunk_ids": [1, 2, 3],
      "description": "测试关于 Python 装饰器知识的召回效果",
      "created_at": "2026-01-22T10:00:00Z"
    },
    {
      "id": 2,
      "user_id": 1,
      "query": "如何使用 React Hooks？",
      "expected_chunk_ids": [4, 5],
      "description": "测试 React Hooks 相关内容",
      "created_at": "2026-01-22T11:00:00Z"
    }
  ],
  "total": 2
}
```

---

## 3. 删除召回测试用例

### 接口信息
- **URL**: `DELETE /api/knowledge/recall-test/cases/{test_case_id}`

### 路径参数
- `test_case_id`: 测试用例 ID

### 请求示例

```javascript
const deleteTestCase = async (testCaseId) => {
  const response = await fetch(`http://localhost:8000/api/knowledge/recall-test/cases/${testCaseId}`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  return await response.json();
};
```

### 响应示例

```json
{
  "code": 200,
  "message": "测试用例删除成功"
}
```

---

## 4. 执行召回测试

### 接口信息
- **URL**: `POST /api/knowledge/recall-test/run`
- **Content-Type**: `application/json`

### 请求参数

```typescript
interface RecallTestRunRequest {
  test_case_id: number;           // 测试用例 ID
  top_k?: number;                 // 召回数量，默认 5
  use_query_expansion?: boolean;  // 是否使用查询扩展（可选）
  use_hybrid_search?: boolean;    // 是否使用混合检索（可选）
  use_reranking?: boolean;        // 是否使用重排序（可选）
}
```

### 请求示例

```javascript
const runRecallTest = async (testCaseId) => {
  const response = await fetch('http://localhost:8000/api/knowledge/recall-test/run', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      test_case_id: testCaseId,
      top_k: 5,
      use_query_expansion: true,
      use_hybrid_search: true,
      use_reranking: true
    })
  });
  return await response.json();
};
```

### 响应示例

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

### 指标说明

| 指标 | 说明 | 计算公式 |
|------|------|----------|
| `recall` | 召回率（百分比） | 命中的期望分段数 / 总期望分段数 × 100 |
| `precision` | 精确率（百分比） | 命中的期望分段数 / 总召回分段数 × 100 |
| `f1_score` | F1 分数（百分比） | 2 × precision × recall / (precision + recall) × 100 |
| `mrr` | 平均倒数排名（百分比） | 1 / 第一次命中的位置 × 100 |

---

## 5. 获取召回测试结果

### 接口信息
- **URL**: `GET /api/knowledge/recall-test/results`

### 查询参数
- `test_case_id` (可选): 测试用例 ID，不传则返回所有测试结果

### 请求示例

```javascript
// 获取所有测试结果
const getAllResults = async () => {
  const response = await fetch('http://localhost:8000/api/knowledge/recall-test/results', {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  return await response.json();
};

// 获取指定测试用例的结果
const getTestCaseResults = async (testCaseId) => {
  const response = await fetch(
    `http://localhost:8000/api/knowledge/recall-test/results?test_case_id=${testCaseId}`,
    {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );
  return await response.json();
};
```

### 响应示例

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

## 6. 获取召回测试汇总统计

### 接口信息
- **URL**: `GET /api/knowledge/recall-test/summary`

### 查询参数
- `test_case_id` (可选): 测试用例 ID，不传则返回所有测试的汇总

### 请求示例

```javascript
// 获取所有测试的汇总
const getAllSummary = async () => {
  const response = await fetch('http://localhost:8000/api/knowledge/recall-test/summary', {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  return await response.json();
};

// 获取指定测试用例的汇总
const getTestCaseSummary = async (testCaseId) => {
  const response = await fetch(
    `http://localhost:8000/api/knowledge/recall-test/summary?test_case_id=${testCaseId}`,
    {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );
  return await response.json();
};
```

### 响应示例

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

## 前端实现建议

### 1. API 服务封装

```typescript
// src/api/recallTest.ts
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api/knowledge/recall-test';

export interface RecallTestCase {
  id: number;
  user_id: number;
  query: string;
  expected_chunk_ids: number[];
  description?: string;
  created_at: string;
}

export interface RecallTestResult {
  id: number;
  user_id: number;
  test_case_id: number;
  retrieved_chunk_ids: number[];
  retrieved_scores: number[];
  recall: number;
  precision: number;
  f1_score: number;
  mrr: number;
  use_query_expansion: boolean;
  use_hybrid_search: boolean;
  use_reranking: boolean;
  top_k: number;
  created_at: string;
}

export interface RecallTestSummary {
  total_tests: number;
  avg_recall: number;
  avg_precision: number;
  avg_f1_score: number;
  avg_mrr: number;
  results: RecallTestResult[];
}

export const recallTestApi = {
  // 创建测试用例
  createTestCase: (data: {
    query: string;
    expected_chunk_ids: number[];
    description?: string;
  }) => axios.post(`${API_BASE}/cases`, data),

  // 获取测试用例列表
  getTestCases: () => axios.get<{ data: RecallTestCase[]; total: number }>(`${API_BASE}/cases`),

  // 删除测试用例
  deleteTestCase: (id: number) => axios.delete(`${API_BASE}/cases/${id}`),

  // 执行测试
  runTest: (data: {
    test_case_id: number;
    top_k?: number;
    use_query_expansion?: boolean;
    use_hybrid_search?: boolean;
    use_reranking?: boolean;
  }) => axios.post<{ data: RecallTestResult }>(`${API_BASE}/run`, data),

  // 获取测试结果
  getResults: (testCaseId?: number) =>
    axios.get<{ data: RecallTestResult[]; total: number }>(`${API_BASE}/results`, {
      params: testCaseId ? { test_case_id: testCaseId } : undefined
    }),

  // 获取汇总统计
  getSummary: (testCaseId?: number) =>
    axios.get<{ data: RecallTestSummary }>(`${API_BASE}/summary`, {
      params: testCaseId ? { test_case_id: testCaseId } : undefined
    })
};
```

### 2. Vue 组件示例

```vue
<template>
  <div class="recall-test">
    <h2>召回测试</h2>

    <!-- 创建测试用例表单 -->
    <div class="create-form">
      <h3>创建测试用例</h3>
      <form @submit.prevent="createTestCase">
        <div>
          <label>查询语句：</label>
          <input v-model="newCase.query" type="text" required />
        </div>
        <div>
          <label>期望分段 ID（逗号分隔）：</label>
          <input v-model="expectedChunkIdsStr" type="text" required />
        </div>
        <div>
          <label>描述：</label>
          <input v-model="newCase.description" type="text" />
        </div>
        <button type="submit">创建</button>
      </form>
    </div>

    <!-- 测试用例列表 -->
    <div class="test-cases">
      <h3>测试用例列表</h3>
      <div v-for="testCase in testCases" :key="testCase.id" class="test-case">
        <div class="case-info">
          <strong>{{ testCase.query }}</strong>
          <span>ID: {{ testCase.id }}</span>
          <span>{{ testCase.description }}</span>
        </div>
        <div class="case-actions">
          <button @click="runTest(testCase.id)">运行测试</button>
          <button @click="deleteTestCase(testCase.id)">删除</button>
        </div>
      </div>
    </div>

    <!-- 测试结果 -->
    <div class="test-results" v-if="summary.total_tests > 0">
      <h3>测试汇总</h3>
      <div class="summary-stats">
        <div>总测试数: {{ summary.total_tests }}</div>
        <div>平均召回率: {{ summary.avg_recall }}%</div>
        <div>平均精确率: {{ summary.avg_precision }}%</div>
        <div>平均 F1 分数: {{ summary.avg_f1_score }}%</div>
        <div>平均 MRR: {{ summary.avg_mrr }}%</div>
      </div>
      <div class="results-list">
        <div v-for="result in summary.results" :key="result.id" class="result">
          <div>测试用例 ID: {{ result.test_case_id }}</div>
          <div>召回率: {{ result.recall }}%</div>
          <div>精确率: {{ result.precision }}%</div>
          <div>F1 分数: {{ result.f1_score }}%</div>
          <div>MRR: {{ result.mrr }}%</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { recallTestApi } from '@/api/recallTest';

const testCases = ref([]);
const summary = ref({
  total_tests: 0,
  avg_recall: 0,
  avg_precision: 0,
  avg_f1_score: 0,
  avg_mrr: 0,
  results: []
});

const newCase = ref({
  query: '',
  expected_chunk_ids: [],
  description: ''
});

const expectedChunkIdsStr = ref('');

// 加载测试用例
const loadTestCases = async () => {
  const response = await recallTestApi.getTestCases();
  testCases.value = response.data.data;
};

// 创建测试用例
const createTestCase = async () => {
  newCase.value.expected_chunk_ids = expectedChunkIdsStr.value
    .split(',')
    .map(id => parseInt(id.trim()))
    .filter(id => !isNaN(id));

  await recallTestApi.createTestCase(newCase.value);
  newCase.value = { query: '', expected_chunk_ids: [], description: '' };
  expectedChunkIdsStr.value = '';
  loadTestCases();
};

// 删除测试用例
const deleteTestCase = async (id) => {
  await recallTestApi.deleteTestCase(id);
  loadTestCases();
};

// 运行测试
const runTest = async (testCaseId) => {
  await recallTestApi.runTest({
    test_case_id: testCaseId,
    top_k: 5,
    use_query_expansion: true,
    use_hybrid_search: true,
    use_reranking: true
  });
  loadSummary();
};

// 加载汇总统计
const loadSummary = async () => {
  const response = await recallTestApi.getSummary();
  summary.value = response.data.data;
};

onMounted(() => {
  loadTestCases();
  loadSummary();
});
</script>

<style scoped>
.recall-test {
  padding: 20px;
}

.create-form,
.test-cases,
.test-results {
  margin-bottom: 30px;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.test-case {
  padding: 10px;
  margin-bottom: 10px;
  border: 1px solid #eee;
  border-radius: 4px;
}

.case-info {
  margin-bottom: 10px;
}

.case-actions button {
  margin-right: 10px;
}

.summary-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 10px;
  margin-bottom: 20px;
}

.summary-stats div {
  padding: 10px;
  background: #f5f5f5;
  border-radius: 4px;
}

.result {
  padding: 10px;
  margin-bottom: 10px;
  border: 1px solid #eee;
  border-radius: 4px;
}
</style>
```

### 3. 路由配置

```typescript
// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router';
import RecallTest from '@/views/RecallTest.vue';

const routes = [
  // ... 其他路由
  {
    path: '/recall-test',
    name: 'RecallTest',
    component: RecallTest,
    meta: { requiresAuth: true }
  }
];
```

---

## 注意事项

1. **认证**: 所有接口都需要在请求头中携带有效的 JWT Token
2. **分段 ID 获取**: 在创建测试用例前，需要先通过知识库文档预览接口获取分段 ID
3. **异步操作**: 执行测试是异步操作，建议添加加载状态提示
4. **错误处理**: 建议添加统一的错误处理机制
5. **数据刷新**: 执行测试后需要刷新汇总数据

---

## 相关接口

- **文档预览**: `GET /api/knowledge/{doc_id}/preview` - 获取文档分段信息
- **知识库查询**: `POST /api/knowledge/query` - 测试检索功能