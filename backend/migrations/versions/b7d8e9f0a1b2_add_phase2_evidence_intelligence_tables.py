"""add_phase2_evidence_intelligence_tables

Revision ID: b7d8e9f0a1b2
Revises: e6f7a8b9c0d1
Create Date: 2026-09-11

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'b7d8e9f0a1b2'
down_revision: Union[str, None] = 'e6f7a8b9c0d1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Enable postgis extension if not enabled
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis;")

    # 2. Create bhoomi_documents table
    op.create_table(
        'bhoomi_documents',
        sa.Column('document_id', sa.String(), nullable=False),
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('parcel_id', sa.String(), nullable=True),
        sa.Column('document_type', sa.String(), nullable=False),
        sa.Column('source_type', sa.String(), nullable=False, server_default='synthetic'),
        sa.Column('file_name', sa.String(), nullable=False),
        sa.Column('storage_reference', sa.String(), nullable=False),
        sa.Column('mime_type', sa.String(), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('sha256_hash', sa.String(), nullable=False),
        sa.Column('page_count', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('document_number', sa.String(), nullable=True),
        sa.Column('registration_number', sa.String(), nullable=True),
        sa.Column('survey_number', sa.String(), nullable=True),
        sa.Column('subdivision_number', sa.String(), nullable=True),
        sa.Column('issuer', sa.String(), nullable=True),
        sa.Column('issue_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('registration_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('transaction_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('document_status', sa.String(), nullable=False, server_default='ACTIVE'),
        sa.Column('extraction_status', sa.String(), nullable=False, server_default='Pending'),
        sa.Column('uploaded_by', sa.String(), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=True),
        sa.Column('data_origin', sa.String(), nullable=False, server_default='synthetic'),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['parcel_id'], ['project_parcels.parcel_id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.project_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('document_id')
    )
    op.create_index(op.f('ix_bhoomi_documents_document_id'), 'bhoomi_documents', ['document_id'], unique=False)
    op.create_index(op.f('ix_bhoomi_documents_document_type'), 'bhoomi_documents', ['document_type'], unique=False)
    op.create_index(op.f('ix_bhoomi_documents_extraction_status'), 'bhoomi_documents', ['extraction_status'], unique=False)
    op.create_index(op.f('ix_bhoomi_documents_parcel_id'), 'bhoomi_documents', ['parcel_id'], unique=False)
    op.create_index(op.f('ix_bhoomi_documents_project_id'), 'bhoomi_documents', ['project_id'], unique=False)
    op.create_index(op.f('ix_bhoomi_documents_sha256_hash'), 'bhoomi_documents', ['sha256_hash'], unique=False)

    # 3. Create document_extractions table
    op.create_table(
        'document_extractions',
        sa.Column('extraction_id', sa.String(), nullable=False),
        sa.Column('document_id', sa.String(), nullable=False),
        sa.Column('extraction_version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('raw_text', sa.Text(), nullable=True),
        sa.Column('structured_data_json', sa.Text(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('status', sa.String(), nullable=False, server_default='Completed'),
        sa.Column('extractor_type', sa.String(), nullable=False, server_default='TextExtractor'),
        sa.Column('extractor_version', sa.String(), nullable=False, server_default='1.0.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['bhoomi_documents.document_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('extraction_id')
    )
    op.create_index(op.f('ix_document_extractions_document_id'), 'document_extractions', ['document_id'], unique=False)
    op.create_index(op.f('ix_document_extractions_extraction_id'), 'document_extractions', ['extraction_id'], unique=False)

    # 4. Create evidence_records table
    op.create_table(
        'evidence_records',
        sa.Column('evidence_id', sa.String(), nullable=False),
        sa.Column('document_id', sa.String(), nullable=False),
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('parcel_id', sa.String(), nullable=True),
        sa.Column('evidence_type', sa.String(), nullable=False),
        sa.Column('field_name', sa.String(), nullable=False),
        sa.Column('raw_value', sa.Text(), nullable=False),
        sa.Column('normalized_value', sa.Text(), nullable=True),
        sa.Column('source_page', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('verification_status', sa.String(), nullable=False, server_default='Unverified'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=True),
        sa.Column('data_origin', sa.String(), nullable=False, server_default='synthetic'),
        sa.ForeignKeyConstraint(['document_id'], ['bhoomi_documents.document_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parcel_id'], ['project_parcels.parcel_id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.project_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('evidence_id')
    )
    op.create_index(op.f('ix_evidence_records_document_id'), 'evidence_records', ['document_id'], unique=False)
    op.create_index(op.f('ix_evidence_records_evidence_id'), 'evidence_records', ['evidence_id'], unique=False)
    op.create_index(op.f('ix_evidence_records_evidence_type'), 'evidence_records', ['evidence_type'], unique=False)
    op.create_index(op.f('ix_evidence_records_field_name'), 'evidence_records', ['field_name'], unique=False)
    op.create_index(op.f('ix_evidence_records_parcel_id'), 'evidence_records', ['parcel_id'], unique=False)
    op.create_index(op.f('ix_evidence_records_project_id'), 'evidence_records', ['project_id'], unique=False)

    # 5. Create cross_record_comparisons table
    op.create_table(
        'cross_record_comparisons',
        sa.Column('comparison_id', sa.String(), nullable=False),
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('document_a_id', sa.String(), nullable=False),
        sa.Column('document_b_id', sa.String(), nullable=False),
        sa.Column('comparison_type', sa.String(), nullable=False, server_default='Document Comparison'),
        sa.Column('field_name', sa.String(), nullable=False),
        sa.Column('value_a', sa.Text(), nullable=True),
        sa.Column('value_b', sa.Text(), nullable=True),
        sa.Column('difference_type', sa.String(), nullable=False),
        sa.Column('severity', sa.String(), nullable=False, server_default='Low'),
        sa.Column('review_required', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=True),
        sa.ForeignKeyConstraint(['document_a_id'], ['bhoomi_documents.document_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['document_b_id'], ['bhoomi_documents.document_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.project_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('comparison_id')
    )
    op.create_index(op.f('ix_cross_record_comparisons_comparison_id'), 'cross_record_comparisons', ['comparison_id'], unique=False)
    op.create_index(op.f('ix_cross_record_comparisons_document_a_id'), 'cross_record_comparisons', ['document_a_id'], unique=False)
    op.create_index(op.f('ix_cross_record_comparisons_document_b_id'), 'cross_record_comparisons', ['document_b_id'], unique=False)
    op.create_index(op.f('ix_cross_record_comparisons_project_id'), 'cross_record_comparisons', ['project_id'], unique=False)

    # 6. Create conflict_signals table
    op.create_table(
        'conflict_signals',
        sa.Column('conflict_id', sa.String(), nullable=False),
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('comparison_id', sa.String(), nullable=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('severity', sa.String(), nullable=False, server_default='Medium'),
        sa.Column('status', sa.String(), nullable=False, server_default='Open'),
        sa.Column('review_required', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=True),
        sa.Column('data_origin', sa.String(), nullable=False, server_default='synthetic'),
        sa.ForeignKeyConstraint(['comparison_id'], ['cross_record_comparisons.comparison_id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.project_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('conflict_id')
    )
    op.create_index(op.f('ix_conflict_signals_conflict_id'), 'conflict_signals', ['conflict_id'], unique=False)
    op.create_index(op.f('ix_conflict_signals_project_id'), 'conflict_signals', ['project_id'], unique=False)
    op.create_index(op.f('ix_conflict_signals_severity'), 'conflict_signals', ['severity'], unique=False)


def downgrade() -> None:
    op.drop_table('conflict_signals')
    op.drop_table('cross_record_comparisons')
    op.drop_table('evidence_records')
    op.drop_table('document_extractions')
    op.drop_table('bhoomi_documents')
