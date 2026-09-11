"""add_phase3_intelligence_graph_tables

Revision ID: c8e9f0a1b2c3
Revises: b7d8e9f0a1b2
Create Date: 2026-09-11

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'c8e9f0a1b2c3'
down_revision: Union[str, None] = 'b7d8e9f0a1b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create process_dependencies table
    op.create_table(
        'process_dependencies',
        sa.Column('dependency_id', sa.String(), nullable=False),
        sa.Column('project_id', sa.String(), nullable=True),
        sa.Column('source_process', sa.String(), nullable=False),
        sa.Column('target_process', sa.String(), nullable=False),
        sa.Column('dependency_type', sa.String(), nullable=False, server_default='DEPENDS_ON'),
        sa.Column('active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('rule_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.project_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('dependency_id')
    )
    op.create_index(op.f('ix_process_dependencies_dependency_id'), 'process_dependencies', ['dependency_id'], unique=False)
    op.create_index(op.f('ix_process_dependencies_project_id'), 'process_dependencies', ['project_id'], unique=False)
    op.create_index(op.f('ix_process_dependencies_source_process'), 'process_dependencies', ['source_process'], unique=False)
    op.create_index(op.f('ix_process_dependencies_target_process'), 'process_dependencies', ['target_process'], unique=False)

    # 2. Create bottleneck_signals table
    op.create_table(
        'bottleneck_signals',
        sa.Column('bottleneck_id', sa.String(), nullable=False),
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('primary_bottleneck', sa.String(), nullable=False),
        sa.Column('secondary_bottleneck', sa.String(), nullable=True),
        sa.Column('severity', sa.String(), nullable=False, server_default='Medium'),
        sa.Column('age_days', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('supporting_signals_json', sa.Text(), nullable=True),
        sa.Column('rule_id', sa.String(), nullable=True),
        sa.Column('generated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=True),
        sa.Column('data_origin', sa.String(), nullable=False, server_default='synthetic'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.project_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('bottleneck_id')
    )
    op.create_index(op.f('ix_bottleneck_signals_bottleneck_id'), 'bottleneck_signals', ['bottleneck_id'], unique=False)
    op.create_index(op.f('ix_bottleneck_signals_project_id'), 'bottleneck_signals', ['project_id'], unique=False)
    op.create_index(op.f('ix_bottleneck_signals_severity'), 'bottleneck_signals', ['severity'], unique=False)

    # 3. Create delay_propagations table
    op.create_table(
        'delay_propagations',
        sa.Column('propagation_id', sa.String(), nullable=False),
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('root_blocker', sa.String(), nullable=False),
        sa.Column('dependency_chain_json', sa.Text(), nullable=False),
        sa.Column('affected_processes_json', sa.Text(), nullable=False),
        sa.Column('propagation_depth', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('critical_path_affected', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('generated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=True),
        sa.Column('data_origin', sa.String(), nullable=False, server_default='synthetic'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.project_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('propagation_id')
    )
    op.create_index(op.f('ix_delay_propagations_project_id'), 'delay_propagations', ['project_id'], unique=False)
    op.create_index(op.f('ix_delay_propagations_propagation_id'), 'delay_propagations', ['propagation_id'], unique=False)


def downgrade() -> None:
    op.drop_table('delay_propagations')
    op.drop_table('bottleneck_signals')
    op.drop_table('process_dependencies')
