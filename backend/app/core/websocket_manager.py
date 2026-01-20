"""
WebSocket 连接管理器
用于管理多个 WebSocket 连接，支持按用户ID和任务ID分发消息
"""
from typing import Dict, Set, Optional
from fastapi import WebSocket
import json
import logging

logger = logging.getLogger(__name__)


class WebSocketManager:
    """WebSocket 连接管理器"""

    def __init__(self):
        # 活跃连接: {user_id: set(connections)}
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        
        # 用户ID到连接ID的映射: {connection_id: user_id}
        self.connection_user_map: Dict[str, int] = {}
        
        # 任务订阅: {task_id: set(user_ids)}
        self.task_subscribers: Dict[str, Set[int]] = {}

    async def connect(self, websocket: WebSocket, user_id: int, connection_id: str):
        """建立 WebSocket 连接"""
        await websocket.accept()
        
        # 添加到用户连接集合
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        
        # 记录连接映射
        self.connection_user_map[connection_id] = user_id
        
        logger.info(f"WebSocket 连接已建立: user_id={user_id}, connection_id={connection_id}")

    def disconnect(self, websocket: WebSocket, connection_id: str):
        """断开 WebSocket 连接"""
        # 获取用户ID
        user_id = self.connection_user_map.get(connection_id)
        
        if user_id and user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            # 如果用户没有其他连接，删除用户记录
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        
        # 移除连接映射
        if connection_id in self.connection_user_map:
            del self.connection_user_map[connection_id]
        
        logger.info(f"WebSocket 连接已断开: user_id={user_id}, connection_id={connection_id}")

    async def send_personal_message(self, message: dict, user_id: int):
        """向指定用户发送消息"""
        if user_id not in self.active_connections:
            logger.warning(f"用户 {user_id} 没有活跃的 WebSocket 连接")
            return
        
        # 向用户的所有连接发送消息
        disconnected_connections = []
        for connection in self.active_connections[user_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"发送消息失败: {e}")
                disconnected_connections.append(connection)
        
        # 移除断开的连接
        for conn in disconnected_connections:
            self.active_connections[user_id].discard(conn)

    async def broadcast(self, message: dict):
        """向所有连接广播消息"""
        for user_id in list(self.active_connections.keys()):
            await self.send_personal_message(message, user_id)

    def subscribe_task(self, task_id: str, user_id: int):
        """订阅任务状态更新"""
        if task_id not in self.task_subscribers:
            self.task_subscribers[task_id] = set()
        self.task_subscribers[task_id].add(user_id)
        logger.info(f"用户 {user_id} 订阅任务 {task_id}")

    def unsubscribe_task(self, task_id: str, user_id: int):
        """取消订阅任务状态更新"""
        if task_id in self.task_subscribers:
            self.task_subscribers[task_id].discard(user_id)
            # 如果没有订阅者，删除任务记录
            if not self.task_subscribers[task_id]:
                del self.task_subscribers[task_id]
        logger.info(f"用户 {user_id} 取消订阅任务 {task_id}")

    async def notify_task_status(self, task_id: str, status: dict):
        """通知任务状态更新"""
        if task_id not in self.task_subscribers:
            logger.warning(f"任务 {task_id} 没有订阅者")
            return
        
        # 向所有订阅该任务的用户发送消息
        for user_id in self.task_subscribers[task_id]:
            message = {
                "type": "task_status",
                "task_id": task_id,
                **status
            }
            await self.send_personal_message(message, user_id)
        
        logger.info(f"任务 {task_id} 状态已通知: {status.get('status')}")

    def get_connection_count(self, user_id: Optional[int] = None) -> int:
        """获取连接数量"""
        if user_id:
            return len(self.active_connections.get(user_id, set()))
        return sum(len(conns) for conns in self.active_connections.values())

    def get_active_users(self) -> Set[int]:
        """获取所有活跃用户ID"""
        return set(self.active_connections.keys())


# 全局 WebSocket 管理器实例
manager = WebSocketManager()