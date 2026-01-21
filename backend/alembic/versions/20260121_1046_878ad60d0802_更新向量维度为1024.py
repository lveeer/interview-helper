"""更新向量维度为1024

Revision ID: 878ad60d0802
Revises: 20260120_1100
Create Date: 2026-01-21 10:46:23.579563

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '878ad60d0802'
down_revision = '20260120_1100'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 更新 vector_chunks 表的 embedding 列维度从 2560 改为 1024
    op.execute('ALTER TABLE vector_chunks ALTER COLUMN embedding TYPE vector(1024)')


def downgrade() -> None:
    # 回滚:将维度改回 2560
    op.execute('ALTER TABLE vector_chunks ALTER COLUMN embedding TYPE vector(2560)')