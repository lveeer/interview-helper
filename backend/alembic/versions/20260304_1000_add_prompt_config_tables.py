"""添加配置中心相关表

Revision ID: 20260304_1000
Revises: 
Create Date: 2026-03-04

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_prompt_config_tables'
down_revision = 'add_job_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Step 1: 创建 prompt_configs 表（先不添加外键到 prompt_versions 和 ab_tests）
    op.create_table(
        'prompt_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('display_name', sa.String(200), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.Enum('interview', 'resume', 'evaluation', 'rag', 'game', 'other', name='prompt_cat'), nullable=True),
        sa.Column('active_version_id', sa.Integer(), nullable=True),
        sa.Column('enable_ab_test', sa.Boolean(), nullable=True, default=False),
        sa.Column('active_ab_test_id', sa.Integer(), nullable=True),
        sa.Column('tags', sa.String(500), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.UniqueConstraint('name')
    )
    op.create_index('ix_prompt_configs_name', 'prompt_configs', ['name'])
    op.create_index('ix_prompt_configs_category', 'prompt_configs', ['category'])

    # Step 2: 创建 prompt_versions 表
    op.create_table(
        'prompt_versions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('config_id', sa.Integer(), nullable=False),
        sa.Column('version', sa.String(50), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('change_log', sa.Text(), nullable=True),
        sa.Column('is_published', sa.Boolean(), nullable=True, default=False),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('usage_count', sa.Integer(), nullable=True, default=0),
        sa.Column('avg_score', sa.Numeric(5, 2), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['config_id'], ['prompt_configs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_prompt_versions_config_id', 'prompt_versions', ['config_id'])

    # Step 3: 创建 ab_tests 表
    op.create_table(
        'ab_tests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('config_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('control_version_id', sa.Integer(), nullable=False),
        sa.Column('experiment_version_id', sa.Integer(), nullable=False),
        sa.Column('traffic_ratio', sa.Numeric(3, 2), nullable=True, default=0.5),
        sa.Column('status', sa.Enum('draft', 'running', 'paused', 'completed', 'archived', name='ab_test_status'), nullable=True, default='draft'),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('control_samples', sa.Integer(), nullable=True, default=0),
        sa.Column('experiment_samples', sa.Integer(), nullable=True, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['config_id'], ['prompt_configs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['control_version_id'], ['prompt_versions.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['experiment_version_id'], ['prompt_versions.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_ab_tests_config_id', 'ab_tests', ['config_id'])
    op.create_index('ix_ab_tests_status', 'ab_tests', ['status'])

    # Step 4: 创建 ab_test_results 表
    op.create_table(
        'ab_test_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ab_test_id', sa.Integer(), nullable=False),
        sa.Column('variant', sa.Enum('control', 'experiment', name='ab_test_variant'), nullable=False),
        sa.Column('version_id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(100), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('metrics', sa.Text(), nullable=True),
        sa.Column('score', sa.Numeric(5, 2), nullable=True),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['ab_test_id'], ['ab_tests.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['version_id'], ['prompt_versions.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_ab_test_results_ab_test_id', 'ab_test_results', ['ab_test_id'])
    op.create_index('ix_ab_test_results_session_id', 'ab_test_results', ['session_id'])

    # Step 5: 添加 prompt_configs 的外键约束（现在 prompt_versions 和 ab_tests 已存在）
    op.create_foreign_key(
        'fk_prompt_configs_active_version_id',
        'prompt_configs',
        'prompt_versions',
        ['active_version_id'],
        ['id'],
        ondelete='SET NULL'
    )
    op.create_foreign_key(
        'fk_prompt_configs_active_ab_test_id',
        'prompt_configs',
        'ab_tests',
        ['active_ab_test_id'],
        ['id'],
        ondelete='SET NULL'
    )


def downgrade():
    # 先删除外键约束
    op.drop_constraint('fk_prompt_configs_active_ab_test_id', 'prompt_configs', type_='foreignkey')
    op.drop_constraint('fk_prompt_configs_active_version_id', 'prompt_configs', type_='foreignkey')
    
    # 删除表（按依赖顺序）
    op.drop_index('ix_ab_test_results_session_id', 'ab_test_results')
    op.drop_index('ix_ab_test_results_ab_test_id', 'ab_test_results')
    op.drop_table('ab_test_results')
    
    op.drop_index('ix_ab_tests_status', 'ab_tests')
    op.drop_index('ix_ab_tests_config_id', 'ab_tests')
    op.drop_table('ab_tests')
    
    op.drop_index('ix_prompt_versions_config_id', 'prompt_versions')
    op.drop_table('prompt_versions')
    
    op.drop_index('ix_prompt_configs_category', 'prompt_configs')
    op.drop_index('ix_prompt_configs_name', 'prompt_configs')
    op.drop_table('prompt_configs')
    
    # 删除枚举类型
    op.execute("DROP TYPE IF EXISTS ab_test_variant")
    op.execute("DROP TYPE IF EXISTS ab_test_status")
    op.execute("DROP TYPE IF EXISTS prompt_cat")
