"""Add knowledge_records table for 12 multi-type institutional datasets

Revision ID: 002_extended_knowledge_records
Revises: 001_initial_schema
Create Date: 2026-11-18 18:40:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '002_extended_knowledge_records'
down_revision: Union[str, None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'knowledge_records',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('record_id', sa.String(length=50), nullable=False, unique=True),
        sa.Column('record_type', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('category_id', sa.String(length=36), sa.ForeignKey('categories.id', ondelete='SET NULL'), nullable=True),
        sa.Column('category_name', sa.String(length=100), nullable=True),
        sa.Column('original_source_url', sa.String(length=500), nullable=False),
        sa.Column('source_document', sa.String(length=255), nullable=True),
        sa.Column('source_page', sa.String(length=50), nullable=True),
        sa.Column('clause_reference', sa.String(length=100), nullable=True),
        sa.Column('publication_date', sa.DateTime(), nullable=True),
        sa.Column('last_verified_date', sa.DateTime(), nullable=False),
        sa.Column('effective_date', sa.DateTime(), nullable=True),
        sa.Column('review_expiry_date', sa.DateTime(), nullable=True),
        sa.Column('approval_status', sa.String(length=30), nullable=False, server_default='approved'),
        sa.Column('is_approved', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('is_sensitive', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('requires_admin_review', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('content_hash', sa.String(length=64), nullable=False),
        sa.Column('searchable_variants', sa.JSON(), nullable=False),
        sa.Column('type_metadata', sa.JSON(), nullable=False),
        sa.Column('audit_trail', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_knowledge_records_record_id', 'knowledge_records', ['record_id'])
    op.create_index('ix_knowledge_records_record_type', 'knowledge_records', ['record_type'])
    op.create_index('ix_knowledge_records_title', 'knowledge_records', ['title'])
    op.create_index('ix_knowledge_records_category_id', 'knowledge_records', ['category_id'])
    op.create_index('ix_knowledge_records_approval_status', 'knowledge_records', ['approval_status'])
    op.create_index('ix_knowledge_records_is_approved', 'knowledge_records', ['is_approved'])
    op.create_index('ix_knowledge_records_is_sensitive', 'knowledge_records', ['is_sensitive'])
    op.create_index('ix_knowledge_records_content_hash', 'knowledge_records', ['content_hash'])
    op.create_index('ix_knowledge_records_review_expiry_date', 'knowledge_records', ['review_expiry_date'])


def downgrade() -> None:
    op.drop_table('knowledge_records')

