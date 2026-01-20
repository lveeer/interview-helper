"""
任务状态推送服务
用于在异步任务执行过程中推送状态更新
"""
import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

from app.core.websocket_manager import manager

logger = logging.getLogger(__name__)


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"           # 等待中
    RUNNING = "running"           # 运行中
    PROGRESS = "progress"         # 进行中（带进度）
    COMPLETED = "completed"       # 已完成
    FAILED = "failed"             # 失败
    CANCELLED = "cancelled"       # 已取消


class TaskNotificationService:
    """任务状态推送服务"""

    def __init__(self):
        self._tasks: Dict[str, Dict[str, Any]] = {}

    async def register_task(
        self,
        task_id: str,
        user_id: int,
        task_type: str,
        task_title: str = None,
        extra_data: Optional[Dict[str, Any]] = None,
        db = None
    ):
        """注册任务"""
        self._tasks[task_id] = {
            "task_id": task_id,
            "user_id": user_id,
            "task_type": task_type,
            "task_title": task_title or f"{task_type}",
            "status": TaskStatus.PENDING,
            "progress": 0,
            "message": "任务已创建",
            "result": None,
            "error": None,
            "extra_data": extra_data or {},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # 订阅任务状态更新
        manager.subscribe_task(task_id, user_id)
        
        # 保存到数据库历史记录（异步执行，不阻塞）
        if db:
            import asyncio
            asyncio.create_task(
                asyncio.to_thread(
                    self._save_notification_to_db,
                    db=db,
                    task_id=task_id,
                    user_id=user_id,
                    task_type=task_type,
                    task_title=task_title or f"{task_type}",
                    status="pending",
                    message="任务已创建",
                    notification_type="info",
                    extra_data=extra_data
                )
            )
        
        logger.info(f"任务已注册: {task_id}, type={task_type}, user={user_id}")

    async def notify_started(self, task_id: str, message: str = "任务开始执行"):
        """通知任务开始"""
        if task_id not in self._tasks:
            logger.warning(f"任务 {task_id} 未注册")
            return

        self._tasks[task_id].update({
            "status": TaskStatus.RUNNING,
            "message": message,
            "updated_at": datetime.now().isoformat()
        })

        await manager.notify_task_status(task_id, {
            "status": TaskStatus.RUNNING,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })

        logger.info(f"任务开始: {task_id}")

    async def notify_progress(
        self,
        task_id: str,
        progress: int,
        message: Optional[str] = None,
        step: Optional[str] = None
    ):
        """通知任务进度"""
        if task_id not in self._tasks:
            logger.warning(f"任务 {task_id} 未注册")
            return

        progress = max(0, min(100, progress))
        status_msg = message or f"任务进行中: {progress}%"

        self._tasks[task_id].update({
            "status": TaskStatus.PROGRESS,
            "progress": progress,
            "message": status_msg,
            "step": step,
            "updated_at": datetime.now().isoformat()
        })

        await manager.notify_task_status(task_id, {
            "status": TaskStatus.PROGRESS,
            "progress": progress,
            "message": status_msg,
            "step": step,
            "timestamp": datetime.now().isoformat()
        })

        logger.info(f"任务进度: {task_id} - {progress}% - {step}")

    async def notify_completed(
        self,
        task_id: str,
        result: Optional[Dict[str, Any]] = None,
        message: str = "任务已完成",
        redirect_url: Optional[str] = None,
        redirect_params: Optional[Dict[str, Any]] = None,
        extra_data: Optional[Dict[str, Any]] = None,
        db = None
    ):
        """通知任务完成"""
        if task_id not in self._tasks:
            logger.warning(f"任务 {task_id} 未注册")
            return

        task = self._tasks[task_id]
        task.update({
            "status": TaskStatus.COMPLETED,
            "progress": 100,
            "message": message,
            "result": result,
            "updated_at": datetime.now().isoformat()
        })

        # WebSocket 推送
        await manager.notify_task_status(task_id, {
            "status": TaskStatus.COMPLETED,
            "progress": 100,
            "message": message,
            "result": result,
            "redirect_url": redirect_url,
            "redirect_params": redirect_params,
            "timestamp": datetime.now().isoformat()
        })

        # 保存到数据库（异步执行，不阻塞）
        if db:
            import asyncio
            asyncio.create_task(
                asyncio.to_thread(
                    self._save_notification_to_db,
                    db=db,
                    task_id=task_id,
                    user_id=task["user_id"],
                    task_type=task["task_type"],
                    task_title=task.get("task_title", task["task_type"]),
                    status="sent",
                    message=message,
                    notification_type="success",
                    result=result,
                    progress=100,
                    redirect_url=redirect_url,
                    redirect_params=redirect_params,
                    extra_data=extra_data or task.get("extra_data")
                )
            )

        logger.info(f"任务完成: {task_id}")

    async def notify_failed(
        self,
        task_id: str,
        error: str,
        error_type: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None,
        db = None
    ):
        """通知任务失败"""
        if task_id not in self._tasks:
            logger.warning(f"任务 {task_id} 未注册")
            return

        task = self._tasks[task_id]
        task.update({
            "status": TaskStatus.FAILED,
            "message": "任务执行失败",
            "error": error,
            "error_type": error_type or type(error).__name__ if isinstance(error, Exception) else "Error",
            "updated_at": datetime.now().isoformat()
        })

        # WebSocket 推送
        await manager.notify_task_status(task_id, {
            "status": TaskStatus.FAILED,
            "message": "任务执行失败",
            "error": str(error),
            "error_type": error_type or type(error).__name__ if isinstance(error, Exception) else "Error",
            "timestamp": datetime.now().isoformat()
        })

        # 保存到数据库（异步执行，不阻塞）
        if db:
            import asyncio
            asyncio.create_task(
                asyncio.to_thread(
                    self._save_notification_to_db,
                    db=db,
                    task_id=task_id,
                    user_id=task["user_id"],
                    task_type=task["task_type"],
                    task_title=task.get("task_title", task["task_type"]),
                    status="sent",
                    message="任务执行失败",
                    notification_type="error",
                    error=error,
                    extra_data=extra_data or task.get("extra_data")
                )
            )

        logger.error(f"任务失败: {task_id} - {error}")

    async def notify_cancelled(self, task_id: str, message: str = "任务已取消"):
        """通知任务取消"""
        if task_id not in self._tasks:
            logger.warning(f"任务 {task_id} 未注册")
            return

        self._tasks[task_id].update({
            "status": TaskStatus.CANCELLED,
            "message": message,
            "updated_at": datetime.now().isoformat()
        })

        await manager.notify_task_status(task_id, {
            "status": TaskStatus.CANCELLED,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })

        logger.info(f"任务取消: {task_id}")

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        return self._tasks.get(task_id)

    def get_user_tasks(self, user_id: int) -> List[Dict[str, Any]]:
        """获取用户的所有任务"""
        return [
            task for task in self._tasks.values()
            if task.get("user_id") == user_id
        ]

    def cleanup_task(self, task_id: str, user_id: int):
        """清理任务记录"""
        if task_id in self._tasks:
            del self._tasks[task_id]
            manager.unsubscribe_task(task_id, user_id)
            logger.info(f"任务已清理: {task_id}")

    def _save_notification_to_db(
        self,
        db,
        task_id: str,
        user_id: int,
        task_type: str,
        task_title: str,
        status: str,
        message: str,
        notification_type: str = "info",
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        progress: int = 0,
        redirect_url: Optional[str] = None,
        redirect_params: Optional[Dict[str, Any]] = None,
        extra_data: Optional[Dict[str, Any]] = None
    ):
        """保存通知到数据库"""
        try:
            from app.models.task_notification import TaskNotification, NotificationStatus
            
            # 查找是否已存在记录
            notification = db.query(TaskNotification).filter(
                TaskNotification.task_id == task_id
            ).first()
            
            if notification:
                # 更新现有记录
                notification.status = NotificationStatus(status)
                notification.message = message
                notification.notification_type = notification_type
                notification.progress = progress
                notification.updated_at = datetime.now()
                
                if result is not None:
                    notification.result = json.dumps(result, ensure_ascii=False)
                if error is not None:
                    notification.error = error
                if redirect_url is not None:
                    notification.redirect_url = redirect_url
                if redirect_params is not None:
                    notification.redirect_params = json.dumps(redirect_params, ensure_ascii=False)
            else:
                # 创建新记录
                notification = TaskNotification(
                    user_id=user_id,
                    task_id=task_id,
                    task_type=task_type,
                    task_title=task_title,
                    status=NotificationStatus(status),
                    message=message,
                    notification_type=notification_type,
                    progress=progress,
                    redirect_url=redirect_url,
                    redirect_params=json.dumps(redirect_params, ensure_ascii=False) if redirect_params else None,
                    extra_data=json.dumps(extra_data, ensure_ascii=False) if extra_data else None
                )
                
                if result is not None:
                    notification.result = json.dumps(result, ensure_ascii=False)
                if error is not None:
                    notification.error = error
                
                db.add(notification)
            
            db.commit()
            logger.info(f"通知已保存到数据库: {task_id}, status={status}")
            
        except Exception as e:
            logger.error(f"保存通知到数据库失败: {e}")
            db.rollback()


# 全局任务推送服务实例
task_notification_service = TaskNotificationService()


# 装饰器：自动推送任务状态
def task_notifier(
    task_id: str,
    user_id: int,
    task_type: str,
    extra_data: Optional[Dict[str, Any]] = None
):
    """
    任务通知装饰器
    自动包装异步任务，推送开始、进度、完成、失败状态
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # 注册任务
            await task_notification_service.register_task(
                task_id=task_id,
                user_id=user_id,
                task_type=task_type,
                extra_data=extra_data
            )
            
            try:
                # 通知任务开始
                await task_notification_service.notify_started(task_id)
                
                # 执行任务
                result = await func(*args, **kwargs)
                
                # 通知任务完成
                await task_notification_service.notify_completed(
                    task_id=task_id,
                    result=result
                )
                
                return result
                
            except Exception as e:
                # 通知任务失败
                await task_notification_service.notify_failed(
                    task_id=task_id,
                    error=str(e),
                    error_type=type(e).__name__,
                    extra_data={"resume_id": resume_id, "file_name": file_name},
                    db=db
                )
                raise
        
        return wrapper
    return decorator


# 上下文管理器：用于推送任务进度
class TaskProgressContext:
    """任务进度上下文管理器"""

    def __init__(self, task_id: str, total_steps: int = 100):
        self.task_id = task_id
        self.total_steps = total_steps
        self.current_step = 0

    async def update(self, step: int, message: Optional[str] = None):
        """更新进度"""
        self.current_step = step
        progress = int((step / self.total_steps) * 100)
        await task_notification_service.notify_progress(
            task_id=self.task_id,
            progress=progress,
            message=message,
            step=f"Step {step}/{self.total_steps}"
        )

    async def increment(self, message: Optional[str] = None):
        """递增进度"""
        self.current_step += 1
        await self.update(self.current_step, message)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await task_notification_service.notify_failed(
                task_id=self.task_id,
                error=str(exc_val),
                error_type=exc_type.__name__
            )
        return False