"""添加简历找茬游戏相关表

Revision ID: add_resume_finder_game
Revises: 2cf9e8f992d6
Create Date: 2026-01-23 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_resume_finder_game'
down_revision = '2cf9e8f992d6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建游戏会话表
    op.create_table(
        'resume_finder_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('difficulty', sa.String(length=20), nullable=False),
        sa.Column('buggy_resume', sa.JSON(), nullable=False),
        sa.Column('errors', sa.JSON(), nullable=False),
        sa.Column('status', sa.String(length=20), server_default='in_progress', nullable=False),
        sa.Column('score', sa.Integer(), server_default='0', nullable=False),
        sa.Column('found_errors', sa.Integer(), server_default='0', nullable=False),
        sa.Column('hints_used', sa.Integer(), server_default='0', nullable=False),
        sa.Column('time_limit', sa.Integer(), nullable=False),
        sa.Column('time_used', sa.Integer(), server_default='0', nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_resume_finder_sessions_id'), 'resume_finder_sessions', ['id'], unique=False)
    op.create_index(op.f('ix_resume_finder_sessions_user_id'), 'resume_finder_sessions', ['user_id'], unique=False)
    op.create_index(op.f('ix_resume_finder_sessions_status'), 'resume_finder_sessions', ['status'], unique=False)
    op.create_index(op.f('ix_resume_finder_sessions_created_at'), 'resume_finder_sessions', ['created_at'], unique=False)

    # 创建用户积分表
    op.create_table(
        'user_points',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('total_score', sa.Integer(), server_default='0', nullable=False),
        sa.Column('daily_score', sa.Integer(), server_default='0', nullable=False),
        sa.Column('weekly_score', sa.Integer(), server_default='0', nullable=False),
        sa.Column('monthly_score', sa.Integer(), server_default='0', nullable=False),
        sa.Column('total_games', sa.Integer(), server_default='0', nullable=False),
        sa.Column('total_found', sa.Integer(), server_default='0', nullable=False),
        sa.Column('best_score', sa.Integer(), server_default='0', nullable=False),
        sa.Column('best_time', sa.Integer(), server_default='0', nullable=False),
        sa.Column('current_streak', sa.Integer(), server_default='0', nullable=False),
        sa.Column('max_streak', sa.Integer(), server_default='0', nullable=False),
        sa.Column('last_played_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_user_points_id'), 'user_points', ['id'], unique=False)

    # 创建用户成就表
    op.create_table(
        'user_achievements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('achievement_id', sa.String(length=50), nullable=False),
        sa.Column('earned_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'achievement_id')
    )
    op.create_index(op.f('ix_user_achievements_id'), 'user_achievements', ['id'], unique=False)
    op.create_index(op.f('ix_user_achievements_user_id'), 'user_achievements', ['user_id'], unique=False)

    # 创建排行榜快照表
    op.create_table(
        'leaderboard_snapshots',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('period', sa.String(length=20), nullable=False),
        sa.Column('snapshot_date', sa.Date(), nullable=False),
        sa.Column('rankings', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('period', 'snapshot_date')
    )
    op.create_index(op.f('ix_leaderboard_snapshots_id'), 'leaderboard_snapshots', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_leaderboard_snapshots_id'), table_name='leaderboard_snapshots')
    op.drop_table('leaderboard_snapshots')

    op.drop_index(op.f('ix_user_achievements_user_id'), table_name='user_achievements')
    op.drop_index(op.f('ix_user_achievements_id'), table_name='user_achievements')
    op.drop_table('user_achievements')

    op.drop_index(op.f('ix_user_points_id'), table_name='user_points')
    op.drop_table('user_points')

    op.drop_index(op.f('ix_resume_finder_sessions_created_at'), table_name='resume_finder_sessions')
    op.drop_index(op.f('ix_resume_finder_sessions_status'), table_name='resume_finder_sessions')
    op.drop_index(op.f('ix_resume_finder_sessions_user_id'), table_name='resume_finder_sessions')
    op.drop_index(op.f('ix_resume_finder_sessions_id'), table_name='resume_finder_sessions')
    op.drop_table('resume_finder_sessions')