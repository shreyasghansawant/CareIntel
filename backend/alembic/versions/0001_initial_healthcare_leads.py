"""create healthcare_leads table

Revision ID: 0001_initial_healthcare_leads
Revises: 
Create Date: 2026-10-30 01:25:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '0001_initial_healthcare_leads'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        'healthcare_leads',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('business_type', sa.String(length=100), nullable=True, server_default='Clinic'),
        sa.Column('address', sa.String(length=500), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=True, server_default='Global'),
        sa.Column('postal_code', sa.String(length=50), nullable=True),
        sa.Column('phone', sa.String(length=100), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('website', sa.String(length=500), nullable=True),
        sa.Column('normalized_website', sa.String(length=500), nullable=True),
        sa.Column('services', sa.JSON(), nullable=True),
        sa.Column('source_url', sa.String(length=1000), nullable=False),
        sa.Column('source_type', sa.String(length=50), nullable=False, server_default='WEBSITE'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='NEW'),
        sa.Column('raw_data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_healthcare_leads_id'), 'healthcare_leads', ['id'], unique=False)
    op.create_index(op.f('ix_healthcare_leads_name'), 'healthcare_leads', ['name'], unique=False)
    op.create_index(op.f('ix_healthcare_leads_city'), 'healthcare_leads', ['city'], unique=False)
    op.create_index(op.f('ix_healthcare_leads_country'), 'healthcare_leads', ['country'], unique=False)
    op.create_index(op.f('ix_healthcare_leads_email'), 'healthcare_leads', ['email'], unique=False)
    op.create_index(op.f('ix_healthcare_leads_normalized_website'), 'healthcare_leads', ['normalized_website'], unique=False)
    op.create_index(op.f('ix_healthcare_leads_status'), 'healthcare_leads', ['status'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_healthcare_leads_status'), table_name='healthcare_leads')
    op.drop_index(op.f('ix_healthcare_leads_normalized_website'), table_name='healthcare_leads')
    op.drop_index(op.f('ix_healthcare_leads_email'), table_name='healthcare_leads')
    op.drop_index(op.f('ix_healthcare_leads_country'), table_name='healthcare_leads')
    op.drop_index(op.f('ix_healthcare_leads_city'), table_name='healthcare_leads')
    op.drop_index(op.f('ix_healthcare_leads_name'), table_name='healthcare_leads')
    op.drop_index(op.f('ix_healthcare_leads_id'), table_name='healthcare_leads')
    op.drop_table('healthcare_leads')
