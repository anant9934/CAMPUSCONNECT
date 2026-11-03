"""Add typed knowledge architecture v4.0 metadata columns

Revision ID: 004_typed_knowledge_architecture_v4
Revises: 003_ums_actions_and_catalog
Create Date: 2026-11-18 21:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '004_typed_knowledge_architecture_v4'
down_revision: Union[str, None] = '003_ums_actions_and_catalog'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('knowledge_records', schema=None) as batch_op:
        batch_op.add_column(sa.Column('institution', sa.String(length=100), server_default='Lovely Professional University', nullable=False))
        batch_op.add_column(sa.Column('campus', sa.String(length=100), server_default='Phagwara, Punjab', nullable=False))
        batch_op.add_column(sa.Column('source_id', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('source_title', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('source_type', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('source_section', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('effective_from', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('effective_to', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('review_due_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('last_verified_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('verification_status', sa.String(length=50), server_default='verified', nullable=False))
        batch_op.add_column(sa.Column('verified_by', sa.String(length=100), server_default='system', nullable=False))
        batch_op.add_column(sa.Column('confidentiality', sa.String(length=50), server_default='public', nullable=False))
        batch_op.add_column(sa.Column('language', sa.String(length=10), server_default='en', nullable=False))
        batch_op.add_column(sa.Column('tags', sa.JSON(), server_default='[]', nullable=False))
        batch_op.add_column(sa.Column('is_active', sa.Boolean(), server_default='1', nullable=False))

        batch_op.create_index('ix_knowledge_records_verification_status', ['verification_status'])
        batch_op.create_index('ix_knowledge_records_confidentiality', ['confidentiality'])
        batch_op.create_index('ix_knowledge_records_is_active', ['is_active'])


def downgrade() -> None:
    with op.batch_alter_table('knowledge_records', schema=None) as batch_op:
        batch_op.drop_index('ix_knowledge_records_is_active')
        batch_op.drop_index('ix_knowledge_records_confidentiality')
        batch_op.drop_index('ix_knowledge_records_verification_status')
        batch_op.drop_column('is_active')
        batch_op.drop_column('tags')
        batch_op.drop_column('language')
        batch_op.drop_column('confidentiality')
        batch_op.drop_column('verified_by')
        batch_op.drop_column('verification_status')
        batch_op.drop_column('last_verified_at')
        batch_op.drop_column('review_due_at')
        batch_op.drop_column('effective_to')
        batch_op.drop_column('effective_from')
        batch_op.drop_column('source_section')
        batch_op.drop_column('source_type')
        batch_op.drop_column('source_title')
        batch_op.drop_column('source_id')
        batch_op.drop_column('campus')
        batch_op.drop_column('institution')

