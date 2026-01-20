# 任务状态推送功能使用指南

## 概述

本系统提供基于 WebSocket 的异步任务状态实时推送功能，用于在面试问题生成、简历解析等耗时操作完成后，自动向前端推送任务状态更新。

## 架构说明

### 核心组件

1. **WebSocket 连接管理器** (`app/core/websocket_manager.py`)
   - 管理多个 WebSocket 连接
   - 支持按用户ID和任务ID分发消息
   - 处理连接建立、断开和消息推送

2. **任务通知服务** (`app/services/task_notification_service.py`)
   - 提供任务状态推送接口
   - 支持任务开始、进度、完成、失败等状态通知
   - 提供装饰器和上下文管理器简化集成

3. **任务通知 API** (`app/api/task_notification.py`)
   - WebSocket 端点：`/api/task/ws/task/{user_id}`
   - HTTP 轮询端点：`/api/task/task/{task_id}/status`
   - 任务管理端点：获取用户任务、清理任务等

## WebSocket 连接

### 连接地址

```
ws://localhost:8000/api/task/ws/task/{user_id}?token={jwt_token}
```

### 连接参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| user_id | int | 是 | 用户ID |
| token | string | 是 | JWT 认证令牌（通过 Query 参数传递） |

### 消息格式

#### 服务器 → 客户端

**连接成功消息：**
```json
{
  "type": "connected",
  "connection_id": "uuid-string",
  "message": "WebSocket 连接已建立",
  "timestamp": "2026-01-20T10:30:00"
}
```

**活跃任务列表：**
```json
{
  "type": "active_tasks",
  "tasks": [...],
  "count": 3
}
```

**任务状态更新：**
```json
{
  "type": "task_status",
  "task_id": "interview_123",
  "status": "running",
  "progress": 50,
  "message": "正在生成面试问题...",
  "step": "Step 3/10",
  "timestamp": "2026-01-20T10:30:00",
  "result": {...},  // 仅在完成时
  "error": null     // 仅在失败时
}
```

**心跳响应：**
```json
{
  "type": "pong",
  "timestamp": "2026-01-20T10:30:00"
}
```

#### 客户端 → 服务器

**订阅任务：**
```json
{
  "type": "subscribe",
  "task_id": "interview_123"
}
```

**取消订阅任务：**
```json
{
  "type": "unsubscribe",
  "task_id": "interview_123"
}
```

**心跳：**
```json
{
  "type": "ping"
}
```

## 任务状态类型

| 状态 | 说明 | 字段 |
|------|------|------|
| `pending` | 等待中 | message |
| `running` | 运行中 | message |
| `progress` | 进行中 | progress, message, step |
| `completed` | 已完成 | result, message |
| `failed` | 失败 | error, error_type |
| `cancelled` | 已取消 | message |

## 前端集成示例

### React 示例

```jsx
import { useEffect, useRef, useState } from 'react';
import { useAuth } from './auth';

const TaskNotification = () => {
  const { user, token } = useAuth();
  const wsRef = useRef(null);
  const [tasks, setTasks] = useState({});
  const [connectionStatus, setConnectionStatus] = useState('disconnected');

  useEffect(() => {
    if (!user || !token) return;

    // 建立 WebSocket 连接
    const wsUrl = `ws://localhost:8000/api/task/ws/task/${user.id}?token=${token}`;
    wsRef.current = new WebSocket(wsUrl);

    wsRef.current.onopen = () => {
      console.log('WebSocket 连接已建立');
      setConnectionStatus('connected');
    };

    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      switch (data.type) {
        case 'connected':
          console.log('连接成功:', data);
          break;
          
        case 'active_tasks':
          console.log('活跃任务:', data.tasks);
          data.tasks.forEach(task => {
            setTasks(prev => ({
              ...prev,
              [task.task_id]: task
            }));
          });
          break;
          
        case 'task_status':
          console.log('任务状态更新:', data);
          setTasks(prev => ({
            ...prev,
            [data.task_id]: data
          }));
          
          // 根据状态处理
          if (data.status === 'completed') {
            console.log('任务完成:', data.result);
            // 执行完成后的操作，如刷新数据
          } else if (data.status === 'failed') {
            console.error('任务失败:', data.error);
            // 显示错误提示
          }
          break;
          
        case 'pong':
          console.log('心跳响应');
          break;
          
        default:
          console.log('未知消息类型:', data);
      }
    };

    wsRef.current.onerror = (error) => {
      console.error('WebSocket 错误:', error);
      setConnectionStatus('error');
    };

    wsRef.current.onclose = () => {
      console.log('WebSocket 连接已关闭');
      setConnectionStatus('disconnected');
      
      // 自动重连（可选）
      setTimeout(() => {
        console.log('尝试重新连接...');
      }, 5000);
    };

    // 心跳机制
    const heartbeat = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: 'ping' }));
      }
    }, 30000);

    return () => {
      clearInterval(heartbeat);
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [user, token]);

  // 订阅特定任务
  const subscribeTask = (taskId) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'subscribe',
        task_id: taskId
      }));
    }
  };

  // 取消订阅任务
  const unsubscribeTask = (taskId) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'unsubscribe',
        task_id: taskId
      }));
    }
  };

  return (
    <div>
      <h3>任务状态</h3>
      <p>连接状态: {connectionStatus}</p>
      
      {Object.entries(tasks).map(([taskId, task]) => (
        <div key={taskId} style={{ marginBottom: '10px', padding: '10px', border: '1px solid #ccc' }}>
          <h4>任务ID: {taskId}</h4>
          <p>状态: {task.status}</p>
          <p>进度: {task.progress}%</p>
          <p>消息: {task.message}</p>
          {task.step && <p>步骤: {task.step}</p>}
          {task.error && <p style={{ color: 'red' }}>错误: {task.error}</p>}
        </div>
      ))}
    </div>
  );
};

export default TaskNotification;
```

### Vue 3 示例

```vue
<template>
  <div>
    <h3>任务状态</h3>
    <p>连接状态: {{ connectionStatus }}</p>
    
    <div v-for="(task, taskId) in tasks" :key="taskId" style="margin-bottom: 10px; padding: 10px; border: 1px solid #ccc;">
      <h4>任务ID: {{ taskId }}</h4>
      <p>状态: {{ task.status }}</p>
      <p>进度: {{ task.progress }}%</p>
      <p>消息: {{ task.message }}</p>
      <p v-if="task.step">步骤: {{ task.step }}</p>
      <p v-if="task.error" style="color: red;">错误: {{ task.error }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();
const ws = ref(null);
const tasks = ref({});
const connectionStatus = ref('disconnected');

const connectWebSocket = () => {
  const wsUrl = `ws://localhost:8000/api/task/ws/task/${authStore.user.id}?token=${authStore.token}`;
  ws.value = new WebSocket(wsUrl);

  ws.value.onopen = () => {
    console.log('WebSocket 连接已建立');
    connectionStatus.value = 'connected';
  };

  ws.value.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    switch (data.type) {
      case 'connected':
        console.log('连接成功:', data);
        break;
        
      case 'active_tasks':
        console.log('活跃任务:', data.tasks);
        data.tasks.forEach(task => {
          tasks.value[task.task_id] = task;
        });
        break;
        
      case 'task_status':
        console.log('任务状态更新:', data);
        tasks.value[data.task_id] = data;
        
        if (data.status === 'completed') {
          console.log('任务完成:', data.result);
          // 执行完成后的操作
        } else if (data.status === 'failed') {
          console.error('任务失败:', data.error);
        }
        break;
        
      case 'pong':
        console.log('心跳响应');
        break;
    }
  };

  ws.value.onerror = (error) => {
    console.error('WebSocket 错误:', error);
    connectionStatus.value = 'error';
  };

  ws.value.onclose = () => {
    console.log('WebSocket 连接已关闭');
    connectionStatus.value = 'disconnected';
  };
};

const subscribeTask = (taskId) => {
  if (ws.value?.readyState === WebSocket.OPEN) {
    ws.value.send(JSON.stringify({
      type: 'subscribe',
      task_id: taskId
    }));
  }
};

const unsubscribeTask = (taskId) => {
  if (ws.value?.readyState === WebSocket.OPEN) {
    ws.value.send(JSON.stringify({
      type: 'unsubscribe',
      task_id: taskId
    }));
  }
};

// 心跳机制
let heartbeatInterval;
const startHeartbeat = () => {
  heartbeatInterval = setInterval(() => {
    if (ws.value?.readyState === WebSocket.OPEN) {
      ws.value.send(JSON.stringify({ type: 'ping' }));
    }
  }, 30000);
};

onMounted(() => {
  connectWebSocket();
  startHeartbeat();
});

onUnmounted(() => {
  if (heartbeatInterval) {
    clearInterval(heartbeatInterval);
  }
  if (ws.value) {
    ws.value.close();
  }
});
</script>
```

### JavaScript 示例

```javascript
class TaskNotificationClient {
  constructor(userId, token) {
    this.userId = userId;
    this.token = token;
    this.ws = null;
    this.tasks = {};
    this.eventHandlers = {};
  }

  connect() {
    const wsUrl = `ws://localhost:8000/api/task/ws/task/${this.userId}?token=${this.token}`;
    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log('WebSocket 连接已建立');
      this.emit('connected');
    };

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      switch (data.type) {
        case 'connected':
          this.emit('connected', data);
          break;
          
        case 'active_tasks':
          data.tasks.forEach(task => {
            this.tasks[task.task_id] = task;
          });
          this.emit('active_tasks', data.tasks);
          break;
          
        case 'task_status':
          this.tasks[data.task_id] = data;
          this.emit('task_status', data);
          
          if (data.status === 'completed') {
            this.emit('task_completed', data);
          } else if (data.status === 'failed') {
            this.emit('task_failed', data);
          }
          break;
          
        case 'pong':
          this.emit('pong');
          break;
      }
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket 错误:', error);
      this.emit('error', error);
    };

    this.ws.onclose = () => {
      console.log('WebSocket 连接已关闭');
      this.emit('disconnected');
    };

    // 心跳机制
    this.heartbeatInterval = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.send({ type: 'ping' });
      }
    }, 30000);
  }

  send(data) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }

  subscribeTask(taskId) {
    this.send({ type: 'subscribe', task_id: taskId });
  }

  unsubscribeTask(taskId) {
    this.send({ type: 'unsubscribe', task_id: taskId });
  }

  on(event, handler) {
    if (!this.eventHandlers[event]) {
      this.eventHandlers[event] = [];
    }
    this.eventHandlers[event].push(handler);
  }

  emit(event, data) {
    if (this.eventHandlers[event]) {
      this.eventHandlers[event].forEach(handler => handler(data));
    }
  }

  disconnect() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
    }
    if (this.ws) {
      this.ws.close();
    }
  }
}

// 使用示例
const client = new TaskNotificationClient(userId, token);

client.on('connected', () => {
  console.log('已连接到服务器');
});

client.on('task_status', (task) => {
  console.log('任务状态更新:', task);
});

client.on('task_completed', (task) => {
  console.log('任务完成:', task.result);
  // 刷新数据或执行其他操作
});

client.on('task_failed', (task) => {
  console.error('任务失败:', task.error);
  // 显示错误提示
});

client.connect();
```

## HTTP 轮询方式（备用方案）

如果 WebSocket 不可用，可以使用 HTTP 轮询方式获取任务状态：

```javascript
async function getTaskStatus(taskId) {
  const response = await fetch(`/api/task/task/${taskId}/status`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  const result = await response.json();
  return result.data;
}

// 轮询示例
async function pollTaskStatus(taskId) {
  const interval = setInterval(async () => {
    const status = await getTaskStatus(taskId);
    
    if (status.status === 'completed') {
      clearInterval(interval);
      console.log('任务完成:', status.result);
    } else if (status.status === 'failed') {
      clearInterval(interval);
      console.error('任务失败:', status.error);
    }
  }, 2000); // 每2秒轮询一次
}
```

## 后端集成示例

### 在异步任务中使用任务通知

```python
from app.services.task_notification_service import task_notification_service, TaskProgressContext

# 方式1：使用装饰器
@task_notifier(
    task_id="interview_123",
    user_id=1,
    task_type="interview_generation",
    metadata={"interview_id": 123}
)
async def generate_interview_questions(...):
    # 任务逻辑
    questions = await llm.generate(...)
    return questions

# 方式2：手动推送
async def generate_interview_questions(...):
    task_id = "interview_123"
    
    # 注册任务
    task_notification_service.register_task(
        task_id=task_id,
        user_id=1,
        task_type="interview_generation"
    )
    
    try:
        # 通知开始
        await task_notification_service.notify_started(task_id)
        
        # 通知进度
        await task_notification_service.notify_progress(
            task_id,
            progress=50,
            message="正在生成问题..."
        )
        
        # 执行任务
        result = await do_something()
        
        # 通知完成
        await task_notification_service.notify_completed(
            task_id,
            result=result
        )
        
        return result
        
    except Exception as e:
        # 通知失败
        await task_notification_service.notify_failed(
            task_id,
            error=str(e)
        )
        raise

# 方式3：使用上下文管理器
async def generate_interview_questions(...):
    task_id = "interview_123"
    
    async with TaskProgressContext(task_id, total_steps=10) as progress:
        await progress.increment("步骤1: 准备数据")
        await progress.increment("步骤2: 调用LLM")
        # ...
```

## 最佳实践

1. **心跳机制**：定期发送 ping 消息保持连接活跃
2. **自动重连**：连接断开后自动尝试重连
3. **错误处理**：妥善处理连接错误和消息解析错误
4. **资源清理**：组件卸载时关闭 WebSocket 连接
5. **状态管理**：使用状态管理工具（如 Redux、Vuex）管理任务状态
6. **用户体验**：显示进度条、加载动画等提升用户体验

## 注意事项

1. WebSocket 连接需要有效的 JWT 令牌
2. 任务ID格式建议：`{task_type}_{resource_id}`，如 `interview_123`
3. 服务重启后任务状态会丢失，建议使用 HTTP 轮询作为备用方案
4. 前端需要处理网络异常和连接断开的情况
5. 避免频繁创建和销毁 WebSocket 连接

## API 文档

详细的 API 文档请访问：`http://localhost:8000/docs`

查看任务通知相关的 API 端点：
- WebSocket: `/api/task/ws/task/{user_id}`
- GET `/api/task/task/{task_id}/status` - 获取任务状态
- GET `/api/task/tasks` - 获取用户所有任务
- DELETE `/api/task/task/{task_id}` - 清理任务记录