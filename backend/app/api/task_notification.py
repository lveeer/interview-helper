"""
任务状态推送 API
提供 WebSocket 端点用于接收异步任务状态更新
"""
import uuid
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.core.websocket_manager import manager
from app.services.task_notification_service import task_notification_service
from app.models.user import User
from app.api.auth import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/task/{user_id}")
async def task_notification_websocket(
    websocket: WebSocket,
    user_id: int,
    token: str = Query(..., description="JWT 认证令牌")
):
    """
    任务状态推送 WebSocket 端点
    
    连接格式: ws://localhost:8000/api/task/ws/task/{user_id}?token={jwt_token}
    
    消息格式:
    服务器 -> 客户端:
    {
        "type": "task_status",
        "task_id": "interview_123",
        "status": "running",
        "progress": 50,
        "message": "正在生成面试问题...",
        "step": "Step 3/10",
        "timestamp": "2026-01-20T10:30:00",
        "result": {...},  # 仅在完成时
        "error": null     # 仅在失败时
    }
    
    客户端 -> 服务器:
    {
        "type": "subscribe",
        "task_id": "interview_123"
    }
    
    {
        "type": "unsubscribe",
        "task_id": "interview_123"
    }
    
    {
        "type": "ping"
    }
    """
    # 生成唯一连接ID
    connection_id = str(uuid.uuid4())
    
    try:
        # 验证用户身份
        user_data = decode_access_token(token)
        if not user_data:
            await websocket.close(code=4001, reason="认证失败")
            return
        
        # 获取用户名并查询用户ID
        username = user_data.get("sub")
        if not username:
            await websocket.close(code=4001, reason="认证失败")
            return
        
        # 验证用户ID是否匹配
        if str(user_id) != username:
            # 通过用户名查询用户ID
            from app.models.user import User
            from app.core.database import get_db
            db_gen = get_db()
            db = next(db_gen)
            try:
                user = db.query(User).filter(User.username == username).first()
                if not user or user.id != user_id:
                    await websocket.close(code=4001, reason="认证失败")
                    return
            finally:
                db.close()
        
        # 建立 WebSocket 连接
        await manager.connect(websocket, user_id, connection_id)
        
        # 发送连接成功消息
        await websocket.send_json({
            "type": "connected",
            "connection_id": connection_id,
            "message": "WebSocket 连接已建立",
            "timestamp": task_notification_service._tasks.get(connection_id, {}).get("created_at")
        })
        
        # 发送用户当前活跃任务状态
        user_tasks = task_notification_service.get_user_tasks(user_id)
        if user_tasks:
            await websocket.send_json({
                "type": "active_tasks",
                "tasks": user_tasks,
                "count": len(user_tasks)
            })
        
        # 监听客户端消息
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type")
            
            if message_type == "subscribe":
                # 订阅特定任务
                task_id = data.get("task_id")
                if task_id:
                    manager.subscribe_task(task_id, user_id)
                    # 发送当前任务状态
                    task_status = task_notification_service.get_task_status(task_id)
                    if task_status:
                        await websocket.send_json({
                            "type": "task_status",
                            **task_status
                        })
            
            elif message_type == "unsubscribe":
                # 取消订阅任务
                task_id = data.get("task_id")
                if task_id:
                    manager.unsubscribe_task(task_id, user_id)
            
            elif message_type == "ping":
                # 心跳响应
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": task_notification_service._tasks.get(connection_id, {}).get("updated_at")
                })
            
            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"未知消息类型: {message_type}"
                })
    
    except WebSocketDisconnect:
        # 正常断开连接
        manager.disconnect(websocket, connection_id)
        logger.info(f"WebSocket 正常断开: user_id={user_id}")
    
    except Exception as e:
        # 异常断开连接
        manager.disconnect(websocket, connection_id)
        logger.error(f"WebSocket 异常断开: user_id={user_id}, error={e}")
        try:
            await websocket.close(code=4000, reason=f"服务器错误: {str(e)}")
        except:
            pass


@router.get("/task/{task_id}/status")
async def get_task_status(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取任务状态（HTTP 轮询方式）
    
    适用于不支持 WebSocket 的场景，或作为备用方案
    """
    task_status = task_notification_service.get_task_status(task_id)
    
    if not task_status:
        return {
            "code": 404,
            "message": "任务不存在",
            "data": None
        }
    
    # 验证任务所有权
    if task_status.get("user_id") != current_user.id:
        return {
            "code": 403,
            "message": "无权访问此任务",
            "data": None
        }
    
    return {
        "code": 200,
        "message": "获取成功",
        "data": task_status
    }


@router.get("/tasks")
async def get_user_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取用户的所有任务
    """
    user_tasks = task_notification_service.get_user_tasks(current_user.id)
    
    return {
        "code": 200,
        "message": "获取成功",
        "data": {
            "tasks": user_tasks,
            "count": len(user_tasks)
        }
    }


@router.delete("/task/{task_id}")
async def cleanup_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    清理已完成或失败的任务记录
    """
    task_status = task_notification_service.get_task_status(task_id)
    
    if not task_status:
        return {
            "code": 404,
            "message": "任务不存在",
            "data": None
        }
    
    # 验证任务所有权
    if task_status.get("user_id") != current_user.id:
        return {
            "code": 403,
            "message": "无权访问此任务",
            "data": None
        }
    
    # 清理任务
    task_notification_service.cleanup_task(task_id, current_user.id)
    
    return {
        "code": 200,
        "message": "任务已清理",
        "data": {"task_id": task_id}
    }


@router.get("/notifications")
async def get_notifications(
    skip: int = 0,
    limit: int = 20,
    status: Optional[str] = None,
    task_type: Optional[str] = None,
    unread_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取用户的任务通知历史记录
    
    参数:
    - skip: 跳过记录数（分页）
    - limit: 返回记录数（分页）
    - status: 过滤状态（pending/sent/read/failed）
    - task_type: 过滤任务类型
    - unread_only: 仅返回未读通知
    """
    from app.models.task_notification import TaskNotification, NotificationStatus, TaskType
    
    query = db.query(TaskNotification).filter(
        TaskNotification.user_id == current_user.id
    )
    
    # 过滤条件
    if status:
        try:
            query = query.filter(TaskNotification.status == NotificationStatus(status))
        except ValueError:
            pass
    
    if task_type:
        try:
            query = query.filter(TaskNotification.task_type == TaskType(task_type))
        except ValueError:
            pass
    
    if unread_only:
        query = query.filter(TaskNotification.status != NotificationStatus.READ)
    
    # 排序和分页
    query = query.order_by(TaskNotification.created_at.desc())
    total = query.count()
    notifications = query.offset(skip).limit(limit).all()
    
    return {
        "code": 200,
        "message": "获取成功",
        "data": {
            "notifications": [n.to_dict() for n in notifications],
            "total": total,
            "skip": skip,
            "limit": limit
        }
    }


@router.put("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    标记通知为已读
    """
    from app.models.task_notification import TaskNotification, NotificationStatus
    from datetime import datetime, timezone
    
    notification = db.query(TaskNotification).filter(
        TaskNotification.id == notification_id,
        TaskNotification.user_id == current_user.id
    ).first()
    
    if not notification:
        return {
            "code": 404,
            "message": "通知不存在",
            "data": None
        }
    
    notification.status = NotificationStatus.READ
    notification.read_at = datetime.now(timezone.utc)
    db.commit()
    
    return {
        "code": 200,
        "message": "标记成功",
        "data": notification.to_dict()
    }


@router.put("/notifications/read-all")
async def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    标记所有通知为已读
    """
    from app.models.task_notification import TaskNotification, NotificationStatus
    from datetime import datetime, timezone
    
    notifications = db.query(TaskNotification).filter(
        TaskNotification.user_id == current_user.id,
        TaskNotification.status != NotificationStatus.READ
    ).all()
    
    for notification in notifications:
        notification.status = NotificationStatus.READ
        notification.read_at = datetime.now(timezone.utc)
    
    db.commit()
    
    return {
        "code": 200,
        "message": f"已标记 {len(notifications)} 条通知为已读",
        "data": {"count": len(notifications)}
    }


@router.delete("/notifications/{notification_id}")
async def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除通知记录
    """
    from app.models.task_notification import TaskNotification
    
    notification = db.query(TaskNotification).filter(
        TaskNotification.id == notification_id,
        TaskNotification.user_id == current_user.id
    ).first()
    
    if not notification:
        return {
            "code": 404,
            "message": "通知不存在",
            "data": None
        }
    
    db.delete(notification)
    db.commit()
    
    return {
        "code": 200,
        "message": "删除成功",
        "data": {"notification_id": notification_id}
    }


@router.get("/notifications/unread-count")
async def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取未读通知数量
    """
    from app.models.task_notification import TaskNotification, NotificationStatus
    
    count = db.query(TaskNotification).filter(
        TaskNotification.user_id == current_user.id,
        TaskNotification.status != NotificationStatus.READ
    ).count()
    
    return {
        "code": 200,
        "message": "获取成功",
        "data": {"unread_count": count}
    }
