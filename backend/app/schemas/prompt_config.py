"""配置中心 Schema 定义"""
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from enum import Enum


# ============ 枚举定义 ============

class PromptCategorySchema(str, Enum):
    """Prompt 分类"""
    INTERVIEW = "interview"
    RESUME = "resume"
    EVALUATION = "evaluation"
    RAG = "rag"
    GAME = "game"
    OTHER = "other"


class ABTestStatus(str, Enum):
    """A/B 测试状态"""
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ABTestVariant(str, Enum):
    """A/B 测试变体"""
    CONTROL = "control"
    EXPERIMENT = "experiment"


# ============ Prompt 配置 Schemas ============

class PromptConfigBase(BaseModel):
    """Prompt 配置基类"""
    name: str = Field(..., min_length=1, max_length=100, description="配置名称")
    display_name: Optional[str] = Field(None, max_length=200, description="显示名称")
    description: Optional[str] = Field(None, description="配置描述")
    category: PromptCategorySchema = Field(PromptCategorySchema.OTHER, description="配置分类")
    tags: Optional[str] = Field(None, max_length=500, description="标签")
    is_active: bool = Field(True, description="是否启用")


class PromptConfigCreate(PromptConfigBase):
    """创建 Prompt 配置"""
    initial_content: Optional[str] = Field(None, description="初始版本内容")
    initial_version: Optional[str] = Field("v1.0.0", description="初始版本号")


class PromptConfigUpdate(BaseModel):
    """更新 Prompt 配置"""
    display_name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    category: Optional[PromptCategorySchema] = None
    tags: Optional[str] = None
    is_active: Optional[bool] = None


class PromptConfigResponse(PromptConfigBase):
    """Prompt 配置响应"""
    id: int
    active_version_id: Optional[int] = None
    enable_ab_test: bool = False
    active_ab_test_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    
    # 关联数据
    active_version: Optional["PromptVersionBrief"] = None
    version_count: int = 0
    
    class Config:
        from_attributes = True


class PromptConfigListResponse(BaseModel):
    """Prompt 配置列表响应"""
    id: int
    name: str
    display_name: Optional[str] = None
    category: PromptCategorySchema
    is_active: bool
    enable_ab_test: bool
    active_version_id: Optional[int] = None
    version_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============ Prompt 版本 Schemas ============

class PromptVersionBase(BaseModel):
    """Prompt 版本基类"""
    version: str = Field(..., min_length=1, max_length=50, description="版本号")
    content: str = Field(..., min_length=1, description="Prompt 内容")
    change_log: Optional[str] = Field(None, description="变更说明")


class PromptVersionCreate(PromptVersionBase):
    """创建 Prompt 版本"""
    pass


class PromptVersionUpdate(BaseModel):
    """更新 Prompt 版本"""
    content: Optional[str] = None
    change_log: Optional[str] = None


class PromptVersionResponse(PromptVersionBase):
    """Prompt 版本响应"""
    id: int
    config_id: int
    is_published: bool
    published_at: Optional[datetime] = None
    usage_count: int = 0
    avg_score: Optional[Decimal] = None
    created_at: datetime
    created_by: Optional[int] = None
    
    class Config:
        from_attributes = True


class PromptVersionBrief(BaseModel):
    """Prompt 版本简要信息"""
    id: int
    version: str
    is_published: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ A/B 测试 Schemas ============

class ABTestBase(BaseModel):
    """A/B 测试基类"""
    name: str = Field(..., min_length=1, max_length=200, description="测试名称")
    description: Optional[str] = Field(None, description="测试描述")
    control_version_id: int = Field(..., description="对照组版本ID")
    experiment_version_id: int = Field(..., description="实验组版本ID")
    traffic_ratio: Decimal = Field(Decimal("0.5"), ge=0, le=1, description="实验组流量比例")


class ABTestCreate(ABTestBase):
    """创建 A/B 测试"""
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")


class ABTestUpdate(BaseModel):
    """更新 A/B 测试"""
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    traffic_ratio: Optional[Decimal] = Field(None, ge=0, le=1)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class ABTestResponse(ABTestBase):
    """A/B 测试响应"""
    id: int
    config_id: int
    status: ABTestStatus
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    control_samples: int = 0
    experiment_samples: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    
    # 关联版本信息
    control_version: Optional[PromptVersionBrief] = None
    experiment_version: Optional[PromptVersionBrief] = None
    
    class Config:
        from_attributes = True


class ABTestListResponse(BaseModel):
    """A/B 测试列表响应"""
    id: int
    name: str
    config_id: int
    config_name: Optional[str] = None
    status: ABTestStatus
    traffic_ratio: Decimal
    control_samples: int
    experiment_samples: int
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ A/B 测试结果 Schemas ============

class ABTestResultCreate(BaseModel):
    """创建 A/B 测试结果"""
    variant: ABTestVariant
    session_id: Optional[str] = None
    metrics: Optional[str] = None  # JSON 字符串
    score: Optional[Decimal] = None
    feedback: Optional[str] = None


class ABTestResultResponse(ABTestResultCreate):
    """A/B 测试结果响应"""
    id: int
    ab_test_id: int
    version_id: int
    user_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ABTestStatistics(BaseModel):
    """A/B 测试统计"""
    total_samples: int
    control_samples: int
    experiment_samples: int
    control_avg_score: Optional[Decimal] = None
    experiment_avg_score: Optional[Decimal] = None
    improvement_rate: Optional[Decimal] = None  # 提升百分比


# ============ 操作请求 Schemas ============

class PublishVersionRequest(BaseModel):
    """发布版本请求"""
    pass


class ActivateABTestRequest(BaseModel):
    """激活 A/B 测试请求"""
    ab_test_id: int


class DeactivateABTestRequest(BaseModel):
    """停用 A/B 测试请求"""
    pass


class SetActiveVersionRequest(BaseModel):
    """设置激活版本请求"""
    version_id: int


class ABTestStatusChangeRequest(BaseModel):
    """A/B 测试状态变更请求"""
    status: ABTestStatus


# ============ Prompt 获取响应 ============

class ResolvedPromptResponse(BaseModel):
    """解析后的 Prompt 响应"""
    config_id: int
    config_name: str
    version_id: int
    version: str
    content: str
    is_ab_test: bool = False
    ab_test_variant: Optional[ABTestVariant] = None
    ab_test_id: Optional[int] = None


# 更新前向引用
PromptConfigResponse.model_rebuild()
