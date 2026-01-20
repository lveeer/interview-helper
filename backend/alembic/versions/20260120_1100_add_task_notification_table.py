"""添加任务通知历史记录表

Revision ID: 20260120_1100
Revises: acf05fb5e2aa
Create Date: 2026-01-20 11:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260120_1100'
down_revision = 'acf05fb5e2aa'
branch_labels = None
depends_on = None


def upgrade():
    # 创建任务类型枚举
    task_type_enum = postgresql.ENUM(
        'INTERVIEW_GENERATION',
        'RESUME_UPLOAD',
        'RESUME_PARSE',
        'RESUME_OPTIMIZE',
        'KNOWLEDGE_UPLOAD',
        'EVALUATION_GENERATE',
        'JOB_MATCH',
        name='tasktype',
        create_type=True
    )
    
    # 创建通知状态枚举
    notification_status_enum = postgresql.ENUM(
        'PENDING',
        'SENT',
        'READ',
        'FAILED',
        name='notificationstatus',
        create_type=True
    )
    
    # 创建任务通知表
    op.create_table(
        'task_notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.String(length=255), nullable=False),
        sa.Column('task_type', task_type_enum, nullable=False),
        sa.Column('task_title', sa.String(length=255), nullable=False),
        sa.Column('status', notification_status_enum, nullable=True),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('notification_type', sa.String(length=50), nullable=True),
        sa.Column('result', sa.Text(), nullable=True),
        sa.Column('error', sa.Text(), nullable=True),
        sa.Column('progress', sa.Integer(), nullable=True),
        sa.Column('redirect_url', sa.String(length=500), nullable=True),
        sa.Column('redirect_params', sa.Text(), nullable=True),
        sa.Column('extra_data', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建索引
    op.create_index(op.f('ix_task_notifications_id'), 'task_notifications', ['id'], unique=False)
    op.create_index(op.f('ix_task_notifications_task_id'), 'task_notifications', ['task_id'], unique=False)
    op.create_index(op.f('ix_task_notifications_user_id'), 'task_notifications', ['user_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_task_notifications_user_id'), table_name='task_notifications')
    op.drop_index(op.f('ix_task_notifications_task_id'), table_name='task_notifications')
    op.drop_index(op.f('ix_task_notifications_id'), table_name='task_notifications')
    op.drop_table('task_notifications')
    
    # 删除枚举类型
    op.execute('DROP TYPE IF EXISTS tasktype')
    op.execute('DROP TYPE IF EXISTS notificationstatus')