"""添加召回测试功能相关表

Revision ID: 2cf9e8f992d6
Revises: f4a2251a6dd5
Create Date: 2026-01-22 14:30:47.584343

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2cf9e8f992d6'
down_revision = 'f4a2251a6dd5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'recall_test_cases',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('query', sa.Text(), nullable=False),
        sa.Column('expected_chunk_ids', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_recall_test_cases_id'), 'recall_test_cases', ['id'], unique=False)

    op.create_table(
        'recall_test_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('test_case_id', sa.Integer(), nullable=False),
        sa.Column('retrieved_chunk_ids', sa.Text(), nullable=False),
        sa.Column('retrieved_scores', sa.Text(), nullable=False),
        sa.Column('recall', sa.Integer(), nullable=True),
        sa.Column('precision', sa.Integer(), nullable=True),
        sa.Column('f1_score', sa.Integer(), nullable=True),
        sa.Column('mrr', sa.Integer(), nullable=True),
        sa.Column('use_query_expansion', sa.Integer(), nullable=True),
        sa.Column('use_hybrid_search', sa.Integer(), nullable=True),
        sa.Column('use_reranking', sa.Integer(), nullable=True),
        sa.Column('top_k', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['test_case_id'], ['recall_test_cases.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_recall_test_results_id'), 'recall_test_results', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_recall_test_results_id'), table_name='recall_test_results')
    op.drop_table('recall_test_results')
    op.drop_index(op.f('ix_recall_test_cases_id'), table_name='recall_test_cases')
    op.drop_table('recall_test_cases')