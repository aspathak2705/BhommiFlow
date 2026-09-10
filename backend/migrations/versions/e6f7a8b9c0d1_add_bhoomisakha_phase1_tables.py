"""add_bhoomisakha_phase1_tables

Revision ID: e6f7a8b9c0d1
Revises: ce63f24b2bdf
Create Date: 2026-09-11

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'e6f7a8b9c0d1'
down_revision: Union[str, None] = 'ce63f24b2bdf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create projects table
    op.create_table(
        'projects',
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('project_code', sa.String(), nullable=False),
        sa.Column('project_name', sa.String(), nullable=False),
        sa.Column('project_type', sa.String(), nullable=False),
        sa.Column('project_sector', sa.String(), nullable=True),
        sa.Column('project_scale', sa.String(), nullable=False, server_default='Medium'),
        sa.Column('state', sa.String(), nullable=False),
        sa.Column('district', sa.String(), nullable=False),
        sa.Column('taluka', sa.String(), nullable=False),
        sa.Column('village', sa.String(), nullable=False),
        sa.Column('project_start_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('planned_completion_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('land_required_area', sa.Float(), nullable=False),
        sa.Column('land_area_unit', sa.String(), nullable=False, server_default='Hectares'),
        sa.Column('affected_families', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('affected_landholders', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('current_stage', sa.String(), nullable=False, server_default='Notification'),
        sa.Column('project_status', sa.String(), nullable=False, server_default='Draft'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=True),
        sa.Column('data_origin', sa.String(), nullable=False, server_default='synthetic'),
        sa.PrimaryKeyConstraint('project_id'),
        sa.UniqueConstraint('project_code')
    )
    op.create_index(op.f('ix_projects_current_stage'), 'projects', ['current_stage'], unique=False)
    op.create_index(op.f('ix_projects_district'), 'projects', ['district'], unique=False)
    op.create_index(op.f('ix_projects_project_code'), 'projects', ['project_code'], unique=True)
    op.create_index(op.f('ix_projects_project_id'), 'projects', ['project_id'], unique=False)
    op.create_index(op.f('ix_projects_project_name'), 'projects', ['project_name'], unique=False)
    op.create_index(op.f('ix_projects_project_scale'), 'projects', ['project_scale'], unique=False)
    op.create_index(op.f('ix_projects_project_sector'), 'projects', ['project_sector'], unique=False)
    op.create_index(op.f('ix_projects_project_status'), 'projects', ['project_status'], unique=False)
    op.create_index(op.f('ix_projects_project_type'), 'projects', ['project_type'], unique=False)
    op.create_index(op.f('ix_projects_state'), 'projects', ['state'], unique=False)
    op.create_index(op.f('ix_projects_taluka'), 'projects', ['taluka'], unique=False)

    # 2. Create project_parcels table
    op.create_table(
        'project_parcels',
        sa.Column('parcel_id', sa.String(), nullable=False),
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('survey_number', sa.String(), nullable=False),
        sa.Column('subdivision_number', sa.String(), nullable=True),
        sa.Column('state', sa.String(), nullable=False),
        sa.Column('district', sa.String(), nullable=False),
        sa.Column('taluka', sa.String(), nullable=False),
        sa.Column('village', sa.String(), nullable=False),
        sa.Column('land_type', sa.String(), nullable=False, server_default='Agricultural'),
        sa.Column('area', sa.Float(), nullable=False),
        sa.Column('area_unit', sa.String(), nullable=False, server_default='Hectares'),
        sa.Column('parcel_status', sa.String(), nullable=False, server_default='Identified'),
        sa.Column('geometry', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=True),
        sa.Column('data_origin', sa.String(), nullable=False, server_default='synthetic'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.project_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('parcel_id')
    )
    op.create_index(op.f('ix_project_parcels_district'), 'project_parcels', ['district'], unique=False)
    op.create_index(op.f('ix_project_parcels_parcel_id'), 'project_parcels', ['parcel_id'], unique=False)
    op.create_index(op.f('ix_project_parcels_parcel_status'), 'project_parcels', ['parcel_status'], unique=False)
    op.create_index(op.f('ix_project_parcels_project_id'), 'project_parcels', ['project_id'], unique=False)
    op.create_index(op.f('ix_project_parcels_state'), 'project_parcels', ['state'], unique=False)
    op.create_index(op.f('ix_project_parcels_survey_number'), 'project_parcels', ['survey_number'], unique=False)
    op.create_index(op.f('ix_project_parcels_taluka'), 'project_parcels', ['taluka'], unique=False)

    # 3. Create project_timeline_events table
    op.create_table(
        'project_timeline_events',
        sa.Column('event_id', sa.String(), nullable=False),
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('parcel_id', sa.String(), nullable=True),
        sa.Column('event_type', sa.String(), nullable=False),
        sa.Column('event_date', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=True),
        sa.Column('stage', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('actor_type', sa.String(), nullable=False, server_default='System'),
        sa.Column('actor_id', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=False, server_default='COMPLETED'),
        sa.Column('metadata_json', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=True),
        sa.Column('data_origin', sa.String(), nullable=False, server_default='synthetic'),
        sa.ForeignKeyConstraint(['actor_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['parcel_id'], ['project_parcels.parcel_id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.project_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('event_id')
    )
    op.create_index(op.f('ix_project_timeline_events_event_date'), 'project_timeline_events', ['event_date'], unique=False)
    op.create_index(op.f('ix_project_timeline_events_event_id'), 'project_timeline_events', ['event_id'], unique=False)
    op.create_index(op.f('ix_project_timeline_events_event_type'), 'project_timeline_events', ['event_type'], unique=False)
    op.create_index(op.f('ix_project_timeline_events_parcel_id'), 'project_timeline_events', ['parcel_id'], unique=False)
    op.create_index(op.f('ix_project_timeline_events_project_id'), 'project_timeline_events', ['project_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_project_timeline_events_project_id'), table_name='project_timeline_events')
    op.drop_index(op.f('ix_project_timeline_events_parcel_id'), table_name='project_timeline_events')
    op.drop_index(op.f('ix_project_timeline_events_event_type'), table_name='project_timeline_events')
    op.drop_index(op.f('ix_project_timeline_events_event_id'), table_name='project_timeline_events')
    op.drop_index(op.f('ix_project_timeline_events_event_date'), table_name='project_timeline_events')
    op.drop_table('project_timeline_events')

    op.drop_index(op.f('ix_project_parcels_taluka'), table_name='project_parcels')
    op.drop_index(op.f('ix_project_parcels_survey_number'), table_name='project_parcels')
    op.drop_index(op.f('ix_project_parcels_state'), table_name='project_parcels')
    op.drop_index(op.f('ix_project_parcels_project_id'), table_name='project_parcels')
    op.drop_index(op.f('ix_project_parcels_parcel_status'), table_name='project_parcels')
    op.drop_index(op.f('ix_project_parcels_parcel_id'), table_name='project_parcels')
    op.drop_index(op.f('ix_project_parcels_district'), table_name='project_parcels')
    op.drop_table('project_parcels')

    op.drop_index(op.f('ix_projects_taluka'), table_name='projects')
    op.drop_index(op.f('ix_projects_state'), table_name='projects')
    op.drop_index(op.f('ix_projects_project_type'), table_name='projects')
    op.drop_index(op.f('ix_projects_project_status'), table_name='projects')
    op.drop_index(op.f('ix_projects_project_sector'), table_name='projects')
    op.drop_index(op.f('ix_projects_project_scale'), table_name='projects')
    op.drop_index(op.f('ix_projects_project_name'), table_name='projects')
    op.drop_index(op.f('ix_projects_project_id'), table_name='projects')
    op.drop_index(op.f('ix_projects_project_code'), table_name='projects')
    op.drop_index(op.f('ix_projects_district'), table_name='projects')
    op.drop_index(op.f('ix_projects_current_stage'), table_name='projects')
    op.drop_table('projects')
