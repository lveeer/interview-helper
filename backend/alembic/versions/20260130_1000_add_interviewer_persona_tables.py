"""添加面试官人设相关表

Revision ID: add_interviewer_persona_tables
Revises: 20260123_1000_add_resume_finder_game_tables
Create Date: 2026-01-30 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON

# revision identifiers, used by Alembic.
revision = 'add_interviewer_persona_tables'
down_revision = 'add_resume_finder_game'
branch_labels = None
depends_on = None


def upgrade():
    # 创建面试官人设表
    op.create_table(
        'interviewer_personas',
        sa.Column('id', sa.Integer(), nullable=False, comment='人设ID'),
        sa.Column('name', sa.String(length=100), nullable=False, comment='人设名称'),
        sa.Column('type', sa.String(length=50), nullable=False, comment='人设类型'),
        sa.Column('description', sa.Text(), nullable=True, comment='人设描述'),
        sa.Column('tone', sa.String(length=50), nullable=True, comment='语气风格'),
        sa.Column('focus_areas', JSON(), nullable=True, comment='关注重点'),
        sa.Column('questioning_style', sa.String(length=50), nullable=True, comment='提问风格'),
        sa.Column('followup_frequency', sa.String(length=20), nullable=True, comment='追问频率'),
        sa.Column('encouragement_level', sa.String(length=20), nullable=True, comment='鼓励程度'),
        sa.Column('conversation_style', sa.String(length=50), nullable=True, comment='对话风格'),
        sa.Column('personality_traits', JSON(), nullable=True, comment='个性特征'),
        sa.Column('question_templates', JSON(), nullable=True, comment='问题模板'),
        sa.Column('transition_phrases', JSON(), nullable=True, comment='过渡语句'),
        sa.Column('feedback_phrases', JSON(), nullable=True, comment='反馈语句'),
        sa.Column('encouragement_phrases', JSON(), nullable=True, comment='鼓励语句'),
        sa.Column('is_default', sa.Boolean(), nullable=True, comment='是否默认'),
        sa.Column('is_custom', sa.Boolean(), nullable=True, comment='是否自定义'),
        sa.Column('user_id', sa.Integer(), nullable=True, comment='创建用户ID'),
        sa.Column('config', JSON(), nullable=True, comment='人设配置'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_interviewer_personas_id'), 'interviewer_personas', ['id'], unique=False)

    # 创建人设对话上下文表
    op.create_table(
        'persona_conversation_contexts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('persona_id', sa.Integer(), nullable=True, comment='人设ID'),
        sa.Column('interview_id', sa.Integer(), nullable=True, comment='面试ID'),
        sa.Column('user_id', sa.Integer(), nullable=True, comment='用户ID'),
        sa.Column('conversation_history', JSON(), nullable=True, comment='对话历史'),
        sa.Column('current_mood', sa.String(length=50), nullable=True, comment='当前情绪'),
        sa.Column('user_satisfaction', sa.Integer(), nullable=True, comment='用户满意度 (0-100)'),
        sa.Column('adjustment_history', JSON(), nullable=True, comment='调整历史'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['interview_id'], ['interviews.id'], ),
        sa.ForeignKeyConstraint(['persona_id'], ['interviewer_personas.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('interview_id')
    )
    op.create_index(op.f('ix_persona_conversation_contexts_id'), 'persona_conversation_contexts', ['id'], unique=False)


def downgrade():
    # 删除人设对话上下文表
    op.drop_index(op.f('ix_persona_conversation_contexts_id'), table_name='persona_conversation_contexts')
    op.drop_table('persona_conversation_contexts')

    # 删除面试官人设表
    op.drop_index(op.f('ix_interviewer_personas_id'), table_name='interviewer_personas')
    op.drop_table('interviewer_personas')