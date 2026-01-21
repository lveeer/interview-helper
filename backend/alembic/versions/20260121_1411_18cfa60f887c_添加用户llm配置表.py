"""添加用户LLM配置表

Revision ID: 18cfa60f887c
Revises: 878ad60d0802
Create Date: 2026-01-21 14:11:53.847707

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '18cfa60f887c'
down_revision = '878ad60d0802'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'user_llm_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('provider', sa.String(length=100), nullable=False, comment='LLM 提供商，如 dashscope/qwen-turbo'),
        sa.Column('model_name', sa.String(length=100), nullable=False, comment='模型名称'),
        sa.Column('api_key', sa.Text(), nullable=True, comment='加密存储的 API Key'),
        sa.Column('api_base', sa.String(length=500), nullable=True, comment='自定义 API 端点'),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true', comment='是否启用'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_llm_configs_id'), 'user_llm_configs', ['id'], unique=False)
    op.create_index(op.f('ix_user_llm_configs_user_id'), 'user_llm_configs', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_user_llm_configs_user_id'), table_name='user_llm_configs')
    op.drop_index(op.f('ix_user_llm_configs_id'), table_name='user_llm_configs')
    op.drop_table('user_llm_configs')