"""添加简历优化功能相关表

Revision ID: d0703335a5a0
Revises: 20260106_1510
Create Date: 2026-01-07 10:32:02.356110

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd0703335a5a0'
down_revision = '20260106_1510'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 为 resumes 表添加版本控制和分析结果字段
    op.add_column('resumes', sa.Column('current_version', sa.String(20), nullable=True, server_default='v1.0'))
    op.add_column('resumes', sa.Column('analysis_result', sa.Text(), nullable=True))

    # 创建 resume_optimizations 表
    op.create_table(
        'resume_optimizations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('resume_id', sa.Integer(), nullable=False),
        sa.Column('priority', sa.String(20), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('before', sa.Text(), nullable=True),
        sa.Column('after', sa.Text(), nullable=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('is_applied', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['resume_id'], ['resumes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_resume_optimizations_id'), 'resume_optimizations', ['id'], unique=False)

    # 创建 resume_optimization_history 表
    op.create_table(
        'resume_optimization_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('resume_id', sa.Integer(), nullable=False),
        sa.Column('version', sa.String(20), nullable=False),
        sa.Column('version_before', sa.String(20), nullable=True),
        sa.Column('version_after', sa.String(20), nullable=True),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(20), nullable=True, server_default='success'),
        sa.Column('changes', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['resume_id'], ['resumes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_resume_optimization_history_id'), 'resume_optimization_history', ['id'], unique=False)


def downgrade() -> None:
    # 删除 resume_optimization_history 表
    op.drop_index(op.f('ix_resume_optimization_history_id'), table_name='resume_optimization_history')
    op.drop_table('resume_optimization_history')

    # 删除 resume_optimizations 表
    op.drop_index(op.f('ix_resume_optimizations_id'), table_name='resume_optimizations')
    op.drop_table('resume_optimizations')

    # 从 resumes 表删除版本控制和分析结果字段
    op.drop_column('resumes', 'analysis_result')
    op.drop_column('resumes', 'current_version')