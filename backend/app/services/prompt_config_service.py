"""配置中心服务层 - Prompt 配置、版本控制、A/B 测试管理"""
import random
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from decimal import Decimal
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.prompt_config import (
    PromptConfig,
    PromptVersion,
    PromptCategory,
    ABTest,
    ABTestResult
)
from app.schemas.prompt_config import (
    PromptConfigCreate,
    PromptConfigUpdate,
    PromptConfigResponse,
    PromptConfigListResponse,
    PromptVersionCreate,
    PromptVersionUpdate,
    PromptVersionResponse,
    PromptVersionBrief,
    ABTestCreate,
    ABTestUpdate,
    ABTestResponse,
    ABTestListResponse,
    ABTestResultCreate,
    ABTestResultResponse,
    ABTestStatistics,
    ABTestStatus,
    ABTestVariant,
    ResolvedPromptResponse
)


class PromptConfigService:
    """Prompt 配置服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ============ Prompt 配置管理 ============
    
    async def create_config(
        self,
        config_data: PromptConfigCreate,
        user_id: Optional[int] = None
    ) -> PromptConfig:
        """创建 Prompt 配置"""
        # 创建配置
        config = PromptConfig(
            name=config_data.name,
            display_name=config_data.display_name,
            description=config_data.description,
            category=PromptCategory(config_data.category.value),
            tags=config_data.tags,
            is_active=config_data.is_active,
            created_by=user_id
        )
        self.db.add(config)
        await self.db.flush()
        
        # 如果有初始内容，创建第一个版本
        if config_data.initial_content:
            version = PromptVersion(
                config_id=config.id,
                version=config_data.initial_version or "v1.0.0",
                content=config_data.initial_content,
                change_log="初始版本",
                is_published=True,
                published_at=datetime.utcnow(),
                created_by=user_id
            )
            self.db.add(version)
            await self.db.flush()
            config.active_version_id = version.id
        
        await self.db.commit()
        await self.db.refresh(config)
        return config
    
    async def get_config(self, config_id: int) -> Optional[PromptConfig]:
        """获取单个配置"""
        result = await self.db.execute(
            select(PromptConfig)
            .options(selectinload(PromptConfig.active_version))
            .where(PromptConfig.id == config_id)
        )
        return result.scalar_one_or_none()
    
    async def get_config_by_name(self, name: str) -> Optional[PromptConfig]:
        """根据名称获取配置"""
        result = await self.db.execute(
            select(PromptConfig)
            .options(selectinload(PromptConfig.active_version))
            .where(PromptConfig.name == name)
        )
        return result.scalar_one_or_none()
    
    async def list_configs(
        self,
        category: Optional[str] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[PromptConfig], int]:
        """获取配置列表"""
        query = select(PromptConfig)
        
        # 过滤条件
        conditions = []
        if category:
            conditions.append(PromptConfig.category == PromptCategory(category))
        if is_active is not None:
            conditions.append(PromptConfig.is_active == is_active)
        if search:
            search_pattern = f"%{search}%"
            conditions.append(
                or_(
                    PromptConfig.name.ilike(search_pattern),
                    PromptConfig.display_name.ilike(search_pattern),
                    PromptConfig.description.ilike(search_pattern)
                )
            )
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # 统计总数
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar()
        
        # 分页
        query = query.order_by(PromptConfig.updated_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        configs = result.scalars().all()
        
        return list(configs), total
    
    async def update_config(
        self,
        config_id: int,
        config_data: PromptConfigUpdate
    ) -> Optional[PromptConfig]:
        """更新配置"""
        config = await self.get_config(config_id)
        if not config:
            return None
        
        update_data = config_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "category" and value:
                value = PromptCategory(value.value)
            setattr(config, field, value)
        
        await self.db.commit()
        await self.db.refresh(config)
        return config
    
    async def delete_config(self, config_id: int) -> bool:
        """删除配置（级联删除版本和测试）"""
        config = await self.get_config(config_id)
        if not config:
            return False
        
        await self.db.delete(config)
        await self.db.commit()
        return True
    
    async def set_active_version(
        self,
        config_id: int,
        version_id: int
    ) -> Optional[PromptConfig]:
        """设置激活版本"""
        config = await self.get_config(config_id)
        if not config:
            return None
        
        # 验证版本存在且属于该配置
        version = await self.get_version(version_id)
        if not version or version.config_id != config_id:
            return None
        
        config.active_version_id = version_id
        await self.db.commit()
        await self.db.refresh(config)
        return config
    
    # ============ 版本管理 ============
    
    async def create_version(
        self,
        config_id: int,
        version_data: PromptVersionCreate,
        user_id: Optional[int] = None
    ) -> Optional[PromptVersion]:
        """创建新版本"""
        config = await self.get_config(config_id)
        if not config:
            return None
        
        # 检查版本号是否已存在
        existing = await self.db.execute(
            select(PromptVersion).where(
                and_(
                    PromptVersion.config_id == config_id,
                    PromptVersion.version == version_data.version
                )
            )
        )
        if existing.scalar_one_or_none():
            return None  # 版本号已存在
        
        version = PromptVersion(
            config_id=config_id,
            version=version_data.version,
            content=version_data.content,
            change_log=version_data.change_log,
            created_by=user_id
        )
        self.db.add(version)
        await self.db.commit()
        await self.db.refresh(version)
        return version
    
    async def get_version(self, version_id: int) -> Optional[PromptVersion]:
        """获取版本详情"""
        result = await self.db.execute(
            select(PromptVersion).where(PromptVersion.id == version_id)
        )
        return result.scalar_one_or_none()
    
    async def list_versions(
        self,
        config_id: int,
        include_unpublished: bool = True
    ) -> List[PromptVersion]:
        """获取版本列表"""
        query = select(PromptVersion).where(PromptVersion.config_id == config_id)
        
        if not include_unpublished:
            query = query.where(PromptVersion.is_published == True)
        
        query = query.order_by(PromptVersion.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def update_version(
        self,
        version_id: int,
        version_data: PromptVersionUpdate
    ) -> Optional[PromptVersion]:
        """更新版本（仅未发布版本）"""
        version = await self.get_version(version_id)
        if not version or version.is_published:
            return None
        
        update_data = version_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(version, field, value)
        
        await self.db.commit()
        await self.db.refresh(version)
        return version
    
    async def publish_version(self, version_id: int) -> Optional[PromptVersion]:
        """发布版本"""
        version = await self.get_version(version_id)
        if not version:
            return None
        
        version.is_published = True
        version.published_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(version)
        return version
    
    async def delete_version(self, version_id: int) -> bool:
        """删除版本（仅未发布版本）"""
        version = await self.get_version(version_id)
        if not version or version.is_published:
            return False
        
        await self.db.delete(version)
        await self.db.commit()
        return True
    
    # ============ A/B 测试管理 ============
    
    async def create_ab_test(
        self,
        config_id: int,
        test_data: ABTestCreate,
        user_id: Optional[int] = None
    ) -> Optional[ABTest]:
        """创建 A/B 测试"""
        config = await self.get_config(config_id)
        if not config:
            return None
        
        # 验证版本存在
        control = await self.get_version(test_data.control_version_id)
        experiment = await self.get_version(test_data.experiment_version_id)
        if not control or not experiment:
            return None
        if control.config_id != config_id or experiment.config_id != config_id:
            return None
        
        ab_test = ABTest(
            config_id=config_id,
            name=test_data.name,
            description=test_data.description,
            control_version_id=test_data.control_version_id,
            experiment_version_id=test_data.experiment_version_id,
            traffic_ratio=test_data.traffic_ratio,
            start_time=test_data.start_time,
            end_time=test_data.end_time,
            created_by=user_id
        )
        self.db.add(ab_test)
        await self.db.commit()
        await self.db.refresh(ab_test)
        return ab_test
    
    async def get_ab_test(self, test_id: int) -> Optional[ABTest]:
        """获取 A/B 测试详情"""
        result = await self.db.execute(
            select(ABTest)
            .options(
                selectinload(ABTest.control_version),
                selectinload(ABTest.experiment_version)
            )
            .where(ABTest.id == test_id)
        )
        return result.scalar_one_or_none()
    
    async def list_ab_tests(
        self,
        config_id: Optional[int] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[ABTest], int]:
        """获取 A/B 测试列表"""
        query = select(ABTest)
        
        conditions = []
        if config_id:
            conditions.append(ABTest.config_id == config_id)
        if status:
            conditions.append(ABTest.status == status)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # 统计总数
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar()
        
        # 分页
        query = query.order_by(ABTest.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        tests = result.scalars().all()
        
        return list(tests), total
    
    async def update_ab_test(
        self,
        test_id: int,
        test_data: ABTestUpdate
    ) -> Optional[ABTest]:
        """更新 A/B 测试配置"""
        ab_test = await self.get_ab_test(test_id)
        if not ab_test or ab_test.status != ABTestStatus.DRAFT.value:
            return None
        
        update_data = test_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(ab_test, field, value)
        
        await self.db.commit()
        await self.db.refresh(ab_test)
        return ab_test
    
    async def change_ab_test_status(
        self,
        test_id: int,
        status: ABTestStatus
    ) -> Optional[ABTest]:
        """变更 A/B 测试状态"""
        ab_test = await self.get_ab_test(test_id)
        if not ab_test:
            return None
        
        # 状态转换验证
        valid_transitions = {
            ABTestStatus.DRAFT: [ABTestStatus.RUNNING],
            ABTestStatus.RUNNING: [ABTestStatus.PAUSED, ABTestStatus.COMPLETED],
            ABTestStatus.PAUSED: [ABTestStatus.RUNNING, ABTestStatus.COMPLETED],
            ABTestStatus.COMPLETED: [ABTestStatus.ARCHIVED],
        }
        
        current_status = ABTestStatus(ab_test.status)
        if status not in valid_transitions.get(current_status, []):
            return None
        
        ab_test.status = status.value
        
        if status == ABTestStatus.RUNNING and not ab_test.start_time:
            ab_test.start_time = datetime.utcnow()
        elif status == ABTestStatus.COMPLETED and not ab_test.end_time:
            ab_test.end_time = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(ab_test)
        return ab_test
    
    async def activate_ab_test(
        self,
        config_id: int,
        test_id: int
    ) -> Optional[PromptConfig]:
        """激活 A/B 测试（配置级别）"""
        config = await self.get_config(config_id)
        ab_test = await self.get_ab_test(test_id)
        
        if not config or not ab_test:
            return None
        if ab_test.config_id != config_id:
            return None
        if ab_test.status != ABTestStatus.RUNNING.value:
            return None
        
        config.enable_ab_test = True
        config.active_ab_test_id = test_id
        
        await self.db.commit()
        await self.db.refresh(config)
        return config
    
    async def deactivate_ab_test(self, config_id: int) -> Optional[PromptConfig]:
        """停用 A/B 测试"""
        config = await self.get_config(config_id)
        if not config:
            return None
        
        config.enable_ab_test = False
        config.active_ab_test_id = None
        
        await self.db.commit()
        await self.db.refresh(config)
        return config
    
    async def delete_ab_test(self, test_id: int) -> bool:
        """删除 A/B 测试（仅草稿状态）"""
        ab_test = await self.get_ab_test(test_id)
        if not ab_test or ab_test.status != ABTestStatus.DRAFT.value:
            return False
        
        await self.db.delete(ab_test)
        await self.db.commit()
        return True
    
    # ============ A/B 测试结果 ============
    
    async def record_ab_test_result(
        self,
        test_id: int,
        result_data: ABTestResultCreate,
        user_id: Optional[int] = None
    ) -> Optional[ABTestResult]:
        """记录 A/B 测试结果"""
        ab_test = await self.get_ab_test(test_id)
        if not ab_test or ab_test.status != ABTestStatus.RUNNING.value:
            return None
        
        # 确定版本
        if result_data.variant == ABTestVariant.CONTROL:
            version_id = ab_test.control_version_id
            ab_test.control_samples += 1
        else:
            version_id = ab_test.experiment_version_id
            ab_test.experiment_samples += 1
        
        result = ABTestResult(
            ab_test_id=test_id,
            variant=result_data.variant.value,
            version_id=version_id,
            session_id=result_data.session_id,
            user_id=user_id,
            metrics=result_data.metrics,
            score=result_data.score,
            feedback=result_data.feedback
        )
        self.db.add(result)
        await self.db.commit()
        await self.db.refresh(result)
        return result
    
    async def get_ab_test_statistics(self, test_id: int) -> Optional[ABTestStatistics]:
        """获取 A/B 测试统计"""
        ab_test = await self.get_ab_test(test_id)
        if not ab_test:
            return None
        
        # 计算平均分
        control_avg = await self.db.execute(
            select(func.avg(ABTestResult.score))
            .where(and_(
                ABTestResult.ab_test_id == test_id,
                ABTestResult.variant == ABTestVariant.CONTROL.value,
                ABTestResult.score.isnot(None)
            ))
        )
        control_avg_score = control_avg.scalar()
        
        experiment_avg = await self.db.execute(
            select(func.avg(ABTestResult.score))
            .where(and_(
                ABTestResult.ab_test_id == test_id,
                ABTestResult.variant == ABTestVariant.EXPERIMENT.value,
                ABTestResult.score.isnot(None)
            ))
        )
        experiment_avg_score = experiment_avg.scalar()
        
        # 计算提升率
        improvement_rate = None
        if control_avg_score and experiment_avg_score:
            improvement_rate = Decimal(str(
                (float(experiment_avg_score) - float(control_avg_score)) / float(control_avg_score) * 100
            ))
        
        return ABTestStatistics(
            total_samples=ab_test.control_samples + ab_test.experiment_samples,
            control_samples=ab_test.control_samples,
            experiment_samples=ab_test.experiment_samples,
            control_avg_score=control_avg_score,
            experiment_avg_score=experiment_avg_score,
            improvement_rate=improvement_rate
        )
    
    # ============ Prompt 获取（核心方法）============
    
    async def get_effective_prompt(
        self,
        config_name: str,
        user_id: Optional[int] = None,
        session_id: Optional[str] = None
    ) -> Optional[ResolvedPromptResponse]:
        """
        获取生效的 Prompt（考虑 A/B 测试）
        
        Args:
            config_name: 配置名称
            user_id: 用户ID（用于一致性分流）
            session_id: 会话ID（用于一致性分流）
        
        Returns:
            解析后的 Prompt 响应，包含版本信息和 A/B 测试标记
        """
        config = await self.get_config_by_name(config_name)
        if not config or not config.is_active:
            return None
        
        # 检查是否启用 A/B 测试
        if config.enable_ab_test and config.active_ab_test_id:
            ab_test = await self.get_ab_test(config.active_ab_test_id)
            
            if ab_test and ab_test.status == ABTestStatus.RUNNING.value:
                # 一致性分流（基于用户ID或会话ID）
                seed = user_id or hash(session_id) if session_id else random.randint(1, 1000000)
                random.seed(seed)
                
                # 根据流量比例决定变体
                is_experiment = random.random() < float(ab_test.traffic_ratio)
                
                if is_experiment:
                    version = await self.get_version(ab_test.experiment_version_id)
                    variant = ABTestVariant.EXPERIMENT
                else:
                    version = await self.get_version(ab_test.control_version_id)
                    variant = ABTestVariant.CONTROL
                
                if version:
                    # 更新使用计数
                    version.usage_count += 1
                    await self.db.commit()
                    
                    return ResolvedPromptResponse(
                        config_id=config.id,
                        config_name=config.name,
                        version_id=version.id,
                        version=version.version,
                        content=version.content,
                        is_ab_test=True,
                        ab_test_variant=variant,
                        ab_test_id=ab_test.id
                    )
        
        # 未启用 A/B 测试，返回激活版本
        if config.active_version_id:
            version = await self.get_version(config.active_version_id)
            if version:
                version.usage_count += 1
                await self.db.commit()
                
                return ResolvedPromptResponse(
                    config_id=config.id,
                    config_name=config.name,
                    version_id=version.id,
                    version=version.version,
                    content=version.content,
                    is_ab_test=False
                )
        
        return None
    
    async def format_prompt(
        self,
        config_name: str,
        user_id: Optional[int] = None,
        session_id: Optional[str] = None,
        **kwargs
    ) -> Optional[str]:
        """
        获取并格式化 Prompt
        
        Args:
            config_name: 配置名称
            user_id: 用户ID
            session_id: 会话ID
            **kwargs: 格式化参数
        
        Returns:
            格式化后的 Prompt 内容
        """
        resolved = await self.get_effective_prompt(config_name, user_id, session_id)
        if not resolved:
            return None
        
        content = resolved.content
        for key, value in kwargs.items():
            placeholder = "{" + key + "}"
            content = content.replace(placeholder, str(value))
        
        return content
    
    # ============ 辅助方法 ============
    
    async def get_version_count(self, config_id: int) -> int:
        """获取配置的版本数量"""
        result = await self.db.execute(
            select(func.count()).where(PromptVersion.config_id == config_id)
        )
        return result.scalar() or 0
    
    async def init_from_file_system(self) -> int:
        """
        从文件系统初始化配置（将 prompts/ 目录下的文件导入数据库）
        
        Returns:
            导入的配置数量
        """
        import os
        
        prompts_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "prompts"
        )
        
        if not os.path.exists(prompts_dir):
            return 0
        
        count = 0
        for filename in os.listdir(prompts_dir):
            if not filename.endswith(".txt"):
                continue
            
            name = filename[:-4]  # 移除 .txt 后缀
            
            # 检查是否已存在
            existing = await self.get_config_by_name(name)
            if existing:
                continue
            
            # 读取文件内容
            filepath = os.path.join(prompts_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            
            # 根据名称推断分类
            category = self._infer_category(name)
            
            # 创建配置
            config = PromptConfig(
                name=name,
                display_name=self._get_display_name(name),
                category=category,
                is_active=True
            )
            self.db.add(config)
            await self.db.flush()
            
            # 创建初始版本
            version = PromptVersion(
                config_id=config.id,
                version="v1.0.0",
                content=content,
                change_log="从文件系统导入",
                is_published=True,
                published_at=datetime.utcnow()
            )
            self.db.add(version)
            await self.db.flush()
            
            config.active_version_id = version.id
            count += 1
        
        await self.db.commit()
        return count
    
    def _infer_category(self, name: str) -> PromptCategory:
        """根据名称推断分类"""
        if any(kw in name for kw in ["interview", "followup", "question"]):
            return PromptCategory.INTERVIEW
        elif any(kw in name for kw in ["resume", "education", "experience", "skills"]):
            return PromptCategory.RESUME
        elif any(kw in name for kw in ["evaluation", "report"]):
            return PromptCategory.EVALUATION
        elif any(kw in name for kw in ["query", "rerank", "rag"]):
            return PromptCategory.RAG
        elif any(kw in name for kw in ["game", "buggy"]):
            return PromptCategory.GAME
        return PromptCategory.OTHER
    
    def _get_display_name(self, name: str) -> str:
        """生成显示名称"""
        return name.replace("_", " ").title()
