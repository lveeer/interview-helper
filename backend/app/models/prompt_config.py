"""配置中心数据模型 - Prompt 配置、版本控制、A/B 测试"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class PromptCategory(str, enum.Enum):
    """Prompt 分类"""
    INTERVIEW = "interview"  # 面试相关
    RESUME = "resume"  # 简历相关
    EVALUATION = "evaluation"  # 评估相关
    RAG = "rag"  # RAG 相关
    GAME = "game"  # 游戏相关
    OTHER = "other"  # 其他
    
    @classmethod
    def _missing_(cls, value):
        """支持大小写不敏感的查找"""
        if isinstance(value, str):
            value_lower = value.lower()
            for member in cls:
                if member.value == value_lower:
                    return member
        return None


class PromptConfig(Base):
    """Prompt 配置主表"""
    __tablename__ = "prompt_configs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True, comment="配置名称，如 interview_questions")
    display_name = Column(String(200), comment="显示名称")
    description = Column(Text, comment="配置描述")
    category = Column(
        Enum(PromptCategory, name='prompt_cat', values_callable=lambda obj: [e.value for e in obj]),
        default=PromptCategory.OTHER,
        comment="配置分类"
    )
    
    # 当前激活版本
    active_version_id = Column(Integer, ForeignKey("prompt_versions.id"), nullable=True)
    
    # A/B 测试配置
    enable_ab_test = Column(Boolean, default=False, comment="是否启用 A/B 测试")
    active_ab_test_id = Column(Integer, ForeignKey("ab_tests.id"), nullable=True)
    
    # 元数据
    tags = Column(String(500), comment="标签，逗号分隔")
    is_active = Column(Boolean, default=True, comment="是否启用")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # 关联关系
    versions = relationship("PromptVersion", back_populates="config", foreign_keys="PromptVersion.config_id")
    active_version = relationship("PromptVersion", foreign_keys=[active_version_id])
    ab_tests = relationship("ABTest", back_populates="config", foreign_keys="ABTest.config_id")
    active_ab_test = relationship("ABTest", foreign_keys=[active_ab_test_id])


class PromptVersion(Base):
    """Prompt 版本表"""
    __tablename__ = "prompt_versions"

    id = Column(Integer, primary_key=True, index=True)
    config_id = Column(Integer, ForeignKey("prompt_configs.id", ondelete="CASCADE"), nullable=False, index=True)
    
    version = Column(String(50), nullable=False, comment="版本号，如 v1.0.0")
    content = Column(Text, nullable=False, comment="Prompt 内容")
    change_log = Column(Text, comment="变更说明")
    
    # 状态
    is_published = Column(Boolean, default=False, comment="是否已发布")
    published_at = Column(DateTime(timezone=True), nullable=True, comment="发布时间")
    
    # 统计数据（可选，用于版本效果追踪）
    usage_count = Column(Integer, default=0, comment="使用次数")
    avg_score = Column(Numeric(5, 2), nullable=True, comment="平均评分（如有）")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # 关联关系
    config = relationship("PromptConfig", back_populates="versions", foreign_keys=[config_id])
    
    # 唯一约束：同一配置下版本号唯一
    __table_args__ = (
        # 版本号在配置内唯一
        # 注意：需要数据库层面约束，这里用索引暗示
    )


class ABTest(Base):
    """A/B 测试配置表"""
    __tablename__ = "ab_tests"

    id = Column(Integer, primary_key=True, index=True)
    config_id = Column(Integer, ForeignKey("prompt_configs.id", ondelete="CASCADE"), nullable=False, index=True)
    
    name = Column(String(200), nullable=False, comment="测试名称")
    description = Column(Text, comment="测试描述")
    
    # 测试变体
    control_version_id = Column(Integer, ForeignKey("prompt_versions.id"), nullable=False, comment="对照组版本")
    experiment_version_id = Column(Integer, ForeignKey("prompt_versions.id"), nullable=False, comment="实验组版本")
    
    # 流量分配
    traffic_ratio = Column(Numeric(3, 2), default=0.5, comment="实验组流量比例，0-1")
    
    # 状态
    status = Column(
        Enum("draft", "running", "paused", "completed", "archived", name="ab_test_status"),
        default="draft",
        comment="测试状态"
    )
    
    # 时间控制
    start_time = Column(DateTime(timezone=True), nullable=True, comment="开始时间")
    end_time = Column(DateTime(timezone=True), nullable=True, comment="结束时间")
    
    # 统计数据
    control_samples = Column(Integer, default=0, comment="对照组样本数")
    experiment_samples = Column(Integer, default=0, comment="实验组样本数")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # 关联关系
    config = relationship("PromptConfig", back_populates="ab_tests", foreign_keys=[config_id])
    control_version = relationship("PromptVersion", foreign_keys=[control_version_id])
    experiment_version = relationship("PromptVersion", foreign_keys=[experiment_version_id])


class ABTestResult(Base):
    """A/B 测试结果记录"""
    __tablename__ = "ab_test_results"

    id = Column(Integer, primary_key=True, index=True)
    ab_test_id = Column(Integer, ForeignKey("ab_tests.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # 分组信息
    variant = Column(Enum("control", "experiment", name="ab_test_variant"), nullable=False, comment="变体类型")
    version_id = Column(Integer, ForeignKey("prompt_versions.id"), nullable=False)
    
    # 上下文信息
    session_id = Column(String(100), comment="会话ID（如面试ID）")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # 结果数据
    metrics = Column(Text, comment="指标数据（JSON格式）")
    score = Column(Numeric(5, 2), comment="评分（如有）")
    feedback = Column(Text, comment="反馈信息")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关联关系
    ab_test = relationship("ABTest")
    version = relationship("PromptVersion")
