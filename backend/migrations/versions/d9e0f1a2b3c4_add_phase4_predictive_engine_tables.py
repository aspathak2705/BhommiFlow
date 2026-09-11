"""add_phase4_predictive_engine_tables

Revision ID: d9e0f1a2b3c4
Revises: c8e9f0a1b2c3
Create Date: 2026-09-11

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'd9e0f1a2b3c4'
down_revision: Union[str, None] = 'c8e9f0a1b2c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'project_predictions',
        sa.Column('prediction_id', sa.String(), nullable=False),
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('model_version', sa.String(), nullable=False, server_default='delay-model-v1'),
        sa.Column('feature_schema_version', sa.String(), nullable=False, server_default='v1'),
        sa.Column('predicted_probability', sa.Float(), nullable=False),
        sa.Column('risk_level', sa.String(), nullable=False, server_default='Low'),
        sa.Column('horizon_days', sa.Integer(), nullable=False, server_default='180'),
        sa.Column('top_features_json', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=True),
        sa.Column('data_origin', sa.String(), nullable=False, server_default='synthetic'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.project_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('prediction_id')
    )
    op.create_index(op.f('ix_project_predictions_prediction_id'), 'project_predictions', ['prediction_id'], unique=False)
    op.create_index(op.f('ix_project_predictions_project_id'), 'project_predictions', ['project_id'], unique=False)
    op.create_index(op.f('ix_project_predictions_risk_level'), 'project_predictions', ['risk_level'], unique=False)


def downgrade() -> None:
    op.drop_table('project_predictions')
