"""添加简历专业技能原始内容字段

Revision ID: acf05fb5e2aa
Revises: f05a0073050f
Create Date: 2026-01-20 10:29:59.529839

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'acf05fb5e2aa'
down_revision = 'f05a0073050f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('resumes', sa.Column('skills_raw', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('resumes', 'skills_raw')