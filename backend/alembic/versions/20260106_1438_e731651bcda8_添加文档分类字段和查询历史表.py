"""添加文档分类字段和查询历史表

Revision ID: e731651bcda8
Revises: 1c0cdf27f7d7
Create Date: 2026-01-06 14:38:59.289941

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e731651bcda8'
down_revision = '1c0cdf27f7d7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 在 knowledge_documents 表中添加 category 字段
    op.add_column('knowledge_documents', sa.Column('category', sa.String(50), server_default='', nullable=False))

    # 创建 query_history 表
    op.create_table(
        'query_history',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('query_text', sa.String(500), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # 创建索引
    op.create_index(op.f('ix_query_history_user_id'), 'query_history', ['user_id'], unique=False)
    op.create_index(op.f('ix_query_history_created_at'), 'query_history', ['created_at'], unique=False)


def downgrade() -> None:
    # 删除索引
    op.drop_index(op.f('ix_query_history_created_at'), table_name='query_history')
    op.drop_index(op.f('ix_query_history_user_id'), table_name='query_history')

    # 删除 query_history 表
    op.drop_table('query_history')

    # 删除 knowledge_documents 表中的 category 字段
    op.drop_column('knowledge_documents', 'category')