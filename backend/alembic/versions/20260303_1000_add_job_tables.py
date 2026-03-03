"""添加岗位管理功能

Revision ID: add_job_tables
Revises: 
Create Date: 2026-03-03 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_job_tables'
down_revision = 'add_interviewer_persona_tables'
branch_labels = None
depends_on = None


def upgrade():
    # 创建 jobs 表
    op.create_table(
        'jobs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('company', sa.String(length=200), nullable=True),
        sa.Column('job_description', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_jobs_id'), 'jobs', ['id'], unique=False)

    # 在 interviews 表添加 job_id 外键
    op.add_column('interviews', sa.Column('job_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_interviews_job_id',
        'interviews', 'jobs',
        ['job_id'], ['id'],
        ondelete='SET NULL'
    )


def downgrade():
    # 删除 interviews 表的 job_id 外键
    op.drop_constraint('fk_interviews_job_id', 'interviews', type_='foreignkey')
    op.drop_column('interviews', 'job_id')

    # 删除 jobs 表
    op.drop_index(op.f('ix_jobs_id'), table_name='jobs')
    op.drop_table('jobs')
