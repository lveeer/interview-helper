"""更新向量列类型为 VECTOR(2560)

Revision ID: af98a62d2f74
Revises: fba4565571c5
Create Date: 2026-01-05 16:24:42.766191

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'af98a62d2f74'
down_revision = 'fba4565571c5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建 pgvector 扩展
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')

    # 先删除旧的 embedding 列
    op.drop_column('vector_chunks', 'embedding')

    # 添加新的 VECTOR 类型列
    op.execute('ALTER TABLE vector_chunks ADD COLUMN embedding VECTOR(2560)')

    # 注意：2560 维超过了索引限制（ivfflat 和 hnsw 都限制在 2000 维以内）
    # 暂时不创建索引，后续可以考虑降维或使用其他方案


def downgrade() -> None:
    # 删除 HNSW 向量索引
    op.execute('DROP INDEX IF EXISTS ix_vector_chunks_embedding')

    # 删除 VECTOR 列
    op.drop_column('vector_chunks', 'embedding')

    # 恢复原来的 ARRAY(Float) 列
    op.add_column('vector_chunks', sa.Column('embedding', sa.ARRAY(sa.Float()), nullable=True))