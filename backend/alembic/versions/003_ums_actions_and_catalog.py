"""Add ums_service_catalog, action_workflows, and campus_places tables for SRS v3.0

Revision ID: 003_ums_actions_and_catalog
Revises: 002_extended_knowledge_records
Create Date: 2026-11-18 20:55:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '003_ums_actions_and_catalog'
down_revision: Union[str, None] = '002_extended_knowledge_records'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. UMS Service Catalog (234 services)
    op.create_table(
        'ums_service_catalog',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('catalog_id', sa.String(length=50), nullable=False, unique=True),
        sa.Column('module', sa.String(length=100), nullable=False),
        sa.Column('service_label', sa.String(length=255), nullable=False),
        sa.Column('action_type', sa.String(length=50), nullable=False),
        sa.Column('public_chatbot_support', sa.String(length=100), nullable=False),
        sa.Column('execution_boundary', sa.Text(), nullable=False),
        sa.Column('ums_authentication', sa.String(length=100), nullable=False),
        sa.Column('navigation_path', sa.String(length=500), nullable=False),
        sa.Column('deep_link_status', sa.String(length=50), nullable=False, server_default='not_verified'),
        sa.Column('deep_link_url', sa.String(length=500), nullable=False, server_default='https://ums.lpu.in/lpuums/'),
        sa.Column('source_evidence', sa.String(length=255), nullable=False, server_default='User-provided authenticated UMS menu screenshot'),
        sa.Column('verification_status', sa.String(length=100), nullable=False, server_default='menu_label_observed_procedure_not_verified'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('keywords', sa.JSON(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_ums_service_catalog_catalog_id', 'ums_service_catalog', ['catalog_id'])
    op.create_index('ix_ums_service_catalog_module', 'ums_service_catalog', ['module'])
    op.create_index('ix_ums_service_catalog_service_label', 'ums_service_catalog', ['service_label'])
    op.create_index('ix_ums_service_catalog_action_type', 'ums_service_catalog', ['action_type'])
    op.create_index('ix_ums_service_catalog_is_active', 'ums_service_catalog', ['is_active'])

    # 2. Action Workflows (24 core SOP workflows)
    op.create_table(
        'action_workflows',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('action_id', sa.String(length=50), nullable=False, unique=True),
        sa.Column('user_intent', sa.String(length=255), nullable=False),
        sa.Column('action_mode', sa.String(length=50), nullable=False),
        sa.Column('target_system', sa.String(length=100), nullable=False),
        sa.Column('ums_navigation_path', sa.String(length=500), nullable=False),
        sa.Column('chatbot_flow', sa.Text(), nullable=False),
        sa.Column('evidence', sa.Text(), nullable=False),
        sa.Column('execution_guardrail', sa.Text(), nullable=False),
        sa.Column('prerequisites', sa.JSON(), nullable=False),
        sa.Column('steps', sa.JSON(), nullable=False),
        sa.Column('handoff_url', sa.String(length=500), nullable=False, server_default='https://ums.lpu.in/lpuums/'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_action_workflows_action_id', 'action_workflows', ['action_id'])
    op.create_index('ix_action_workflows_user_intent', 'action_workflows', ['user_intent'])
    op.create_index('ix_action_workflows_action_mode', 'action_workflows', ['action_mode'])
    op.create_index('ix_action_workflows_is_active', 'action_workflows', ['is_active'])

    # 3. Campus Places & Wayfinding Directory
    op.create_table(
        'campus_places',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('place_id', sa.String(length=50), nullable=False, unique=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('building', sa.String(length=100), nullable=False),
        sa.Column('floor_room', sa.String(length=100), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('opening_hours', sa.String(length=150), nullable=True),
        sa.Column('accessibility', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('services_available', sa.JSON(), nullable=False),
        sa.Column('official_map_url', sa.String(length=500), nullable=False, server_default='https://www.lpu.in/about_lpu/campus-tour.php'),
        sa.Column('verified_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_campus_places_place_id', 'campus_places', ['place_id'])
    op.create_index('ix_campus_places_name', 'campus_places', ['name'])
    op.create_index('ix_campus_places_category', 'campus_places', ['category'])
    op.create_index('ix_campus_places_building', 'campus_places', ['building'])


def downgrade() -> None:
    op.drop_table('campus_places')
    op.drop_table('action_workflows')
    op.drop_table('ums_service_catalog')

