# 前端推送通知组件示例

## 功能说明

本示例展示如何在前端实现任务推送通知功能，包括：
- WebSocket 实时接收任务状态
- 弹窗显示任务完成通知
- 自动跳转到相关页面
- 查看历史推送记录
- 未读通知数量显示

## React 完整示例

### 1. 通知组件 (NotificationProvider.jsx)

```jsx
import React, { createContext, useContext, useState, useEffect, useRef } from 'react';
import { useAuth } from './auth';
import { message, Modal, Badge, Drawer, List, Tag, Button } from 'antd';

const NotificationContext = createContext();

export const useNotification = () => useContext(NotificationContext);

export const NotificationProvider = ({ children }) => {
  const { user, token } = useAuth();
  const wsRef = useRef(null);
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [drawerVisible, setDrawerVisible] = useState(false);
  const [historyNotifications, setHistoryNotifications] = useState([]);

  // WebSocket 连接
  useEffect(() => {
    if (!user || !token) return;

    const wsUrl = `ws://localhost:8000/api/task/ws/task/${user.id}?token=${token}`;
    wsRef.current = new WebSocket(wsUrl);

    wsRef.current.onopen = () => {
      console.log('WebSocket 连接已建立');
    };

    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handleNotification(data);
    };

    wsRef.current.onerror = (error) => {
      console.error('WebSocket 错误:', error);
    };

    wsRef.current.onclose = () => {
      console.log('WebSocket 连接已关闭');
      // 自动重连
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

    // 加载历史通知
    loadHistoryNotifications();

    return () => {
      clearInterval(heartbeat);
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [user, token]);

  // 处理通知
  const handleNotification = (data) => {
    switch (data.type) {
      case 'connected':
        console.log('连接成功:', data);
        break;

      case 'active_tasks':
        console.log('活跃任务:', data.tasks);
        break;

      case 'task_status':
        console.log('任务状态更新:', data);
        
        // 添加到通知列表
        setNotifications(prev => [
          {
            id: Date.now(),
            ...data,
            timestamp: new Date()
          },
          ...prev
        ]);

        // 任务完成时弹窗
        if (data.status === 'completed') {
          showTaskCompletedNotification(data);
        } else if (data.status === 'failed') {
          showTaskFailedNotification(data);
        }
        break;

      case 'pong':
        console.log('心跳响应');
        break;
    }
  };

  // 显示任务完成通知
  const showTaskCompletedNotification = (data) => {
    const key = `task_${data.task_id}`;
    
    // 使用 Ant Design Message
    message.success({
      key,
      content: (
        <div>
          <div style={{ fontWeight: 'bold', marginBottom: 4 }}>
            {data.message || '任务已完成'}
          </div>
          <div style={{ fontSize: 12, color: '#666' }}>
            {data.result && Object.entries(data.result).map(([k, v]) => (
              <div key={k}>{k}: {v}</div>
            ))}
          </div>
          {data.redirect_url && (
            <Button 
              type="link" 
              size="small"
              onClick={() => handleRedirect(data)}
              style={{ padding: 0, marginTop: 8 }}
            >
              查看详情 →
            </Button>
          )}
        </div>
      ),
      duration: 5,
      onClick: () => handleRedirect(data)
    });

    // 3秒后自动跳转（可选）
    setTimeout(() => {
      if (data.redirect_url) {
        handleRedirect(data);
      }
    }, 3000);
  };

  // 显示任务失败通知
  const showTaskFailedNotification = (data) => {
    message.error({
      key: `task_${data.task_id}`,
      content: (
        <div>
          <div style={{ fontWeight: 'bold', marginBottom: 4 }}>
            {data.message || '任务执行失败'}
          </div>
          <div style={{ fontSize: 12, color: '#666' }}>
            {data.error}
          </div>
        </div>
      ),
      duration: 5
    });
  };

  // 处理跳转
  const handleRedirect = (data) => {
    if (data.redirect_url) {
      // 使用 React Router 跳转
      window.location.href = data.redirect_url;
      // 或者使用 history.push（如果使用 React Router）
      // history.push(data.redirect_url, data.redirect_params);
    }
  };

  // 加载历史通知
  const loadHistoryNotifications = async () => {
    try {
      const response = await fetch('/api/task/notifications', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      const result = await response.json();
      if (result.code === 200) {
        setHistoryNotifications(result.data.notifications);
        setUnreadCount(result.data.notifications.filter(n => n.status !== 'read').length);
      }
    } catch (error) {
      console.error('加载历史通知失败:', error);
    }
  };

  // 标记通知为已读
  const markAsRead = async (notificationId) => {
    try {
      await fetch(`/api/task/notifications/${notificationId}/read`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      // 更新本地状态
      setHistoryNotifications(prev =>
        prev.map(n => n.id === notificationId ? { ...n, status: 'read' } : n)
      );
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (error) {
      console.error('标记已读失败:', error);
    }
  };

  // 标记所有为已读
  const markAllAsRead = async () => {
    try {
      await fetch('/api/task/notifications/read-all', {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      setHistoryNotifications(prev =>
        prev.map(n => ({ ...n, status: 'read' }))
      );
      setUnreadCount(0);
    } catch (error) {
      console.error('标记全部已读失败:', error);
    }
  };

  // 删除通知
  const deleteNotification = async (notificationId) => {
    try {
      await fetch(`/api/task/notifications/${notificationId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      setHistoryNotifications(prev =>
        prev.filter(n => n.id !== notificationId)
      );
    } catch (error) {
      console.error('删除通知失败:', error);
    }
  };

  // 获取通知类型标签颜色
  const getNotificationTypeColor = (type) => {
    const colors = {
      success: 'success',
      error: 'error',
      warning: 'warning',
      info: 'default'
    };
    return colors[type] || 'default';
  };

  // 获取任务类型显示名称
  const getTaskTypeName = (type) => {
    const names = {
      interview_generation: '面试问题生成',
      resume_upload: '简历上传',
      resume_parse: '简历解析',
      resume_optimize: '简历优化',
      knowledge_upload: '知识库上传',
      evaluation_generate: '评估报告生成',
      job_match: '岗位匹配分析'
    };
    return names[type] || type;
  };

  return (
    <NotificationContext.Provider value={{
      notifications,
      historyNotifications,
      unreadCount,
      loadHistoryNotifications,
      markAsRead,
      markAllAsRead,
      deleteNotification,
      setDrawerVisible
    }}>
      {children}

      {/* 通知铃铛图标 */}
      <Badge count={unreadCount} overflowCount={99}>
        <Button 
          type="text" 
          icon={<BellOutlined />}
          onClick={() => setDrawerVisible(true)}
        >
          通知
        </Button>
      </Badge>

      {/* 历史通知抽屉 */}
      <Drawer
        title="通知历史"
        placement="right"
        width={480}
        visible={drawerVisible}
        onClose={() => setDrawerVisible(false)}
        extra={
          <Button 
            type="link" 
            onClick={markAllAsRead}
            disabled={unreadCount === 0}
          >
            全部标为已读
          </Button>
        }
      >
        <List
          dataSource={historyNotifications}
          renderItem={(item) => (
            <List.Item
              key={item.id}
              style={{
                backgroundColor: item.status !== 'read' ? '#f0f7ff' : 'transparent',
                padding: '12px',
                marginBottom: '8px',
                borderRadius: '4px'
              }}
              actions={[
                item.redirect_url && (
                  <Button 
                    type="link" 
                    size="small"
                    onClick={() => {
                      window.location.href = item.redirect_url;
                      markAsRead(item.id);
                    }}
                  >
                    查看
                  </Button>
                ),
                <Button 
                  type="text" 
                  size="small"
                  danger
                  onClick={() => deleteNotification(item.id)}
                >
                  删除
                </Button>
              ]}
            >
              <List.Item.Meta
                title={
                  <div>
                    <Tag color={getNotificationTypeColor(item.notification_type)}>
                      {getTaskTypeName(item.task_type)}
                    </Tag>
                    <span style={{ marginLeft: 8, fontWeight: item.status !== 'read' ? 'bold' : 'normal' }}>
                      {item.task_title}
                    </span>
                  </div>
                }
                description={
                  <div>
                    <div style={{ marginBottom: 4 }}>{item.message}</div>
                    <div style={{ fontSize: 12, color: '#999' }}>
                      {new Date(item.created_at).toLocaleString('zh-CN')}
                    </div>
                  </div>
                }
              />
            </List.Item>
          )}
        />
      </Drawer>
    </NotificationContext.Provider>
  );
};
```

### 2. 在应用中使用

```jsx
import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { NotificationProvider } from './NotificationProvider';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';

function App() {
  return (
    <ConfigProvider locale={zhCN}>
      <NotificationProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/interview/:id" element={<InterviewDetail />} />
            <Route path="/resume/:id" element={<ResumeDetail />} />
            {/* 其他路由 */}
          </Routes>
        </BrowserRouter>
      </NotificationProvider>
    </ConfigProvider>
  );
}

export default App;
```

### 3. 在页面中显示通知按钮

```jsx
import React from 'react';
import { Layout, Menu } from 'antd';
import { useNotification } from './NotificationProvider';

const { Header } = Layout;

const AppHeader = () => {
  const { unreadCount, setDrawerVisible } = useNotification();

  return (
    <Header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
      <div className="logo" />
      <Menu theme="dark" mode="horizontal" />
      
      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        {/* 通知按钮会自动渲染 */}
        {/* 其他用户信息 */}
      </div>
    </Header>
  );
};

export default AppHeader;
```

## Vue 3 完整示例

### 1. 通知组件 (NotificationPlugin.js)

```javascript
import { createApp } from 'vue';
import { ElMessage, ElNotification, ElBadge, ElButton, ElDrawer, ElList, ElTag } from 'element-plus';

class NotificationManager {
  constructor() {
    this.ws = null;
    this.notifications = [];
    this.historyNotifications = [];
    this.unreadCount = 0;
    this.listeners = [];
  }

  connect(userId, token) {
    const wsUrl = `ws://localhost:8000/api/task/ws/task/${userId}?token=${token}`;
    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log('WebSocket 连接已建立');
      this.emit('connected');
    };

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.handleNotification(data);
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket 错误:', error);
      this.emit('error', error);
    };

    this.ws.onclose = () => {
      console.log('WebSocket 连接已关闭');
      this.emit('disconnected');
      // 自动重连
      setTimeout(() => this.connect(userId, token), 5000);
    };

    // 心跳机制
    this.heartbeatInterval = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ type: 'ping' }));
      }
    }, 30000);

    // 加载历史通知
    this.loadHistoryNotifications(token);
  }

  handleNotification(data) {
    switch (data.type) {
      case 'connected':
        this.emit('connected', data);
        break;

      case 'active_tasks':
        this.emit('active_tasks', data.tasks);
        break;

      case 'task_status':
        this.notifications.unshift({
          id: Date.now(),
          ...data,
          timestamp: new Date()
        });

        if (data.status === 'completed') {
          this.showTaskCompletedNotification(data);
        } else if (data.status === 'failed') {
          this.showTaskFailedNotification(data);
        }

        this.emit('task_status', data);
        break;

      case 'pong':
        this.emit('pong');
        break;
    }
  }

  showTaskCompletedNotification(data) {
    ElNotification({
      title: '任务完成',
      message: (
        <div>
          <div style={{ fontWeight: 'bold', marginBottom: 8 }}>
            {data.message || '任务已完成'}
          </div>
          {data.result && Object.entries(data.result).map(([k, v]) => (
            <div key={k} style={{ fontSize: 12, color: '#666' }}>
              {k}: {v}
            </div>
          ))}
          {data.redirect_url && (
            <el-button
              type="primary"
              size="small"
              onClick={() => this.handleRedirect(data)}
              style={{ marginTop: 12 }}
            >
              查看详情
            </el-button>
          )}
        </div>
      ),
      type: 'success',
      duration: 5000,
      onClick: () => this.handleRedirect(data)
    });
  }

  showTaskFailedNotification(data) {
    ElNotification({
      title: '任务失败',
      message: (
        <div>
          <div style={{ fontWeight: 'bold', marginBottom: 8 }}>
            {data.message || '任务执行失败'}
          </div>
          <div style={{ fontSize: 12, color: '#666' }}>
            {data.error}
          </div>
        </div>
      ),
      type: 'error',
      duration: 5000
    });
  }

  handleRedirect(data) {
    if (data.redirect_url) {
      window.location.href = data.redirect_url;
    }
  }

  async loadHistoryNotifications(token) {
    try {
      const response = await fetch('/api/task/notifications', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      const result = await response.json();
      if (result.code === 200) {
        this.historyNotifications = result.data.notifications;
        this.unreadCount = result.data.notifications.filter(n => n.status !== 'read').length;
        this.emit('history_loaded', this.historyNotifications);
      }
    } catch (error) {
      console.error('加载历史通知失败:', error);
    }
  }

  async markAsRead(notificationId, token) {
    try {
      await fetch(`/api/task/notifications/${notificationId}/read`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      const notification = this.historyNotifications.find(n => n.id === notificationId);
      if (notification) {
        notification.status = 'read';
        this.unreadCount = Math.max(0, this.unreadCount - 1);
      }
    } catch (error) {
      console.error('标记已读失败:', error);
    }
  }

  async markAllAsRead(token) {
    try {
      await fetch('/api/task/notifications/read-all', {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      this.historyNotifications.forEach(n => n.status = 'read');
      this.unreadCount = 0;
    } catch (error) {
      console.error('标记全部已读失败:', error);
    }
  }

  async deleteNotification(notificationId, token) {
    try {
      await fetch(`/api/task/notifications/${notificationId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      this.historyNotifications = this.historyNotifications.filter(n => n.id !== notificationId);
    } catch (error) {
      console.error('删除通知失败:', error);
    }
  }

  on(event, callback) {
    this.listeners.push({ event, callback });
  }

  emit(event, data) {
    this.listeners
      .filter(l => l.event === event)
      .forEach(l => l.callback(data));
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

export const notificationManager = new NotificationManager();

export const NotificationPlugin = {
  install(app) {
    app.config.globalProperties.$notification = notificationManager;
    app.provide('notification', notificationManager);
  }
};
```

### 2. 在 Vue 应用中使用

```javascript
// main.js
import { createApp } from 'vue';
import { NotificationPlugin } from './NotificationPlugin';
import App from './App.vue';

const app = createApp(App);
app.use(NotificationPlugin);
app.mount('#app');
```

```vue
<!-- App.vue -->
<template>
  <div id="app">
    <el-container>
      <el-header>
        <el-badge :value="unreadCount" :hidden="unreadCount === 0">
          <el-button @click="drawerVisible = true">
            <el-icon><Bell /></el-icon>
            通知
          </el-button>
        </el-badge>
      </el-header>
      
      <el-drawer
        v-model="drawerVisible"
        title="通知历史"
        size="480px"
      >
        <template #header>
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span>通知历史</span>
            <el-button
              type="primary"
              link
              @click="markAllAsRead"
              :disabled="unreadCount === 0"
            >
              全部标为已读
            </el-button>
          </div>
        </template>
        
        <el-list :data="historyNotifications">
          <template #default="{ item }">
            <el-list-item
              :style="{
                backgroundColor: item.status !== 'read' ? '#f0f7ff' : 'transparent',
                padding: '12px',
                marginBottom: '8px',
                borderRadius: '4px'
              }"
            >
              <template #default>
                <div style="flex: 1;">
                  <div style="margin-bottom: 8px;">
                    <el-tag :type="getNotificationTypeColor(item.notification_type)">
                      {{ getTaskTypeName(item.task_type) }}
                    </el-tag>
                    <span style="margin-left: 8px; font-weight: item.status !== 'read' ? 'bold' : 'normal'">
                      {{ item.task_title }}
                    </span>
                  </div>
                  <div style="margin-bottom: 4px;">{{ item.message }}</div>
                  <div style="font-size: 12px; color: #999;">
                    {{ new Date(item.created_at).toLocaleString('zh-CN') }}
                  </div>
                </div>
                
                <div style="display: flex; gap: 8px;">
                  <el-button
                    v-if="item.redirect_url"
                    type="primary"
                    link
                    @click="handleRedirect(item)"
                  >
                    查看
                  </el-button>
                  <el-button
                    type="danger"
                    link
                    @click="deleteNotification(item.id)"
                  >
                    删除
                  </el-button>
                </div>
              </template>
            </el-list-item>
          </template>
        </el-list>
      </el-drawer>
      
      <router-view />
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted, inject } from 'vue';
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();
const notification = inject('notification');

const drawerVisible = ref(false);
const unreadCount = ref(0);
const historyNotifications = ref([]);

onMounted(() => {
  if (authStore.user && authStore.token) {
    notification.connect(authStore.user.id, authStore.token);
    
    notification.on('history_loaded', (notifications) => {
      historyNotifications.value = notifications;
      unreadCount.value = notifications.filter(n => n.status !== 'read').length;
    });
    
    notification.on('task_status', (data) => {
      if (data.status === 'completed' || data.status === 'failed') {
        loadHistoryNotifications();
      }
    });
  }
});

const loadHistoryNotifications = async () => {
  await notification.loadHistoryNotifications(authStore.token);
  historyNotifications.value = notification.historyNotifications;
  unreadCount.value = notification.unreadCount;
};

const markAsRead = async (notificationId) => {
  await notification.markAsRead(notificationId, authStore.token);
  loadHistoryNotifications();
};

const markAllAsRead = async () => {
  await notification.markAllAsRead(authStore.token);
  loadHistoryNotifications();
};

const deleteNotification = async (notificationId) => {
  await notification.deleteNotification(notificationId, authStore.token);
  loadHistoryNotifications();
};

const handleRedirect = (item) => {
  if (item.redirect_url) {
    window.location.href = item.redirect_url;
    markAsRead(item.id);
  }
};

const getNotificationTypeColor = (type) => {
  const colors = {
    success: 'success',
    error: 'danger',
    warning: 'warning',
    info: 'info'
  };
  return colors[type] || 'info';
};

const getTaskTypeName = (type) => {
  const names = {
    interview_generation: '面试问题生成',
    resume_upload: '简历上传',
    resume_parse: '简历解析',
    resume_optimize: '简历优化',
    knowledge_upload: '知识库上传',
    evaluation_generate: '评估报告生成',
    job_match: '岗位匹配分析'
  };
  return names[type] || type;
};
</script>
```

## API 使用说明

### 1. 获取通知列表

```javascript
const response = await fetch('/api/task/notifications?skip=0&limit=20&unread_only=false', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
const result = await response.json();
```

### 2. 标记通知为已读

```javascript
await fetch(`/api/task/notifications/${notificationId}/read`, {
  method: 'PUT',
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

### 3. 标记所有通知为已读

```javascript
await fetch('/api/task/notifications/read-all', {
  method: 'PUT',
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

### 4. 删除通知

```javascript
await fetch(`/api/task/notifications/${notificationId}`, {
  method: 'DELETE',
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

### 5. 获取未读数量

```javascript
const response = await fetch('/api/task/notifications/unread-count', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
const result = await response.json();
console.log('未读数量:', result.data.unread_count);
```

## 注意事项

1. **WebSocket 连接**：确保在用户登录后建立连接，登出时关闭连接
2. **自动重连**：连接断开后自动尝试重连，避免用户感知
3. **心跳机制**：定期发送 ping 消息保持连接活跃
4. **错误处理**：妥善处理网络异常和连接错误
5. **性能优化**：历史通知分页加载，避免一次性加载过多数据
6. **用户体验**：任务完成后自动跳转，提升用户体验
7. **权限验证**：所有 API 请求都需要携带有效的 JWT 令牌

## 部署说明

1. **数据库迁移**：运行 `alembic upgrade head` 创建任务通知表
2. **环境变量**：确保 WebSocket 端口可访问
3. **CORS 配置**：允许前端域名访问 WebSocket
4. **测试**：使用 WebSocket 测试工具验证连接正常