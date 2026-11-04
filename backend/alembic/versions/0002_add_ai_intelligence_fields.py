"""add ai intelligence fields

Revision ID: 0002_add_ai_intelligence_fields
Revises: 0001_initial_healthcare_leads
Create Date: 2026-10-30 04:15:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '0002_add_ai_intelligence_fields'
down_revision: Union[str, None] = '0001_initial_healthcare_leads'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column('healthcare_leads', sa.Column('ai_analysis', sa.JSON(), nullable=True))
    op.add_column('healthcare_leads', sa.Column('ai_opportunities', sa.JSON(), nullable=True))
    op.add_column('healthcare_leads', sa.Column('ai_score', sa.Integer(), nullable=True))
    op.add_column('healthcare_leads', sa.Column('ai_score_category', sa.String(length=50), nullable=True))
    op.add_column('healthcare_leads', sa.Column('ai_score_reason', sa.Text(), nullable=True))
    op.add_column('healthcare_leads', sa.Column('ai_outreach_subject', sa.String(length=255), nullable=True))
    op.add_column('healthcare_leads', sa.Column('ai_outreach_body', sa.Text(), nullable=True))
    op.add_column('healthcare_leads', sa.Column('ai_analyzed_at', sa.DateTime(timezone=True), nullable=True))

def downgrade() -> None:
    op.drop_column('healthcare_leads', 'ai_analyzed_at')
    op.drop_column('healthcare_leads', 'ai_outreach_body')
    op.drop_column('healthcare_leads', 'ai_outreach_subject')
    op.drop_column('healthcare_leads', 'ai_score_reason')
    op.drop_column('healthcare_leads', 'ai_score_category')
    op.drop_column('healthcare_leads', 'ai_score')
    op.drop_column('healthcare_leads', 'ai_opportunities')
    op.drop_column('healthcare_leads', 'ai_analysis')

