"""Initial schema - Create all tables

Revision ID: 001_initial
Revises: 
Create Date: 2024-10-24 10:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON
import uuid

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all tables"""
    
    # Providers table
    op.create_table(
        'providers',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('registration_number', sa.String(100), nullable=False, unique=True, index=True),
        sa.Column('name', sa.String(255), nullable=False, index=True),
        sa.Column('provider_type', sa.String(50), nullable=False),
        sa.Column('specialization', sa.String(100)),
        sa.Column('email', sa.String(255), index=True),
        sa.Column('phone', sa.String(20)),
        sa.Column('address_line1', sa.String(255)),
        sa.Column('address_line2', sa.String(255)),
        sa.Column('city', sa.String(100), index=True),
        sa.Column('state', sa.String(100), index=True),
        sa.Column('postal_code', sa.String(20)),
        sa.Column('country', sa.String(100), default='India'),
        sa.Column('status', sa.String(20), default='pending', index=True),
        sa.Column('verified_at', sa.DateTime()),
        sa.Column('verification_expires_at', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now(), index=True),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', sa.String(100)),
        sa.Column('updated_by', sa.String(100)),
        sa.Column('additional_data', JSON, default={}),
        sa.CheckConstraint("status IN ('pending', 'verified', 'rejected', 'suspended', 'under_review')", name='check_provider_status')
    )
    op.create_index('idx_provider_location', 'providers', ['state', 'city'])
    op.create_index('idx_provider_type_status', 'providers', ['provider_type', 'status'])
    
    # Provider verifications table
    op.create_table(
        'provider_verifications',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('provider_id', UUID(as_uuid=True), sa.ForeignKey('providers.id'), nullable=False, index=True),
        sa.Column('source_type', sa.String(50), nullable=False, index=True),
        sa.Column('source_url', sa.String(500)),
        sa.Column('verification_data', JSON, default={}),
        sa.Column('is_verified', sa.Boolean, nullable=False, default=False),
        sa.Column('confidence_score', sa.Float, default=0.0),
        sa.Column('verification_notes', sa.Text()),
        sa.Column('verified_at', sa.DateTime(), default=sa.func.now(), index=True),
        sa.Column('verified_by', sa.String(100)),
        sa.Column('expires_at', sa.DateTime()),
        sa.CheckConstraint('confidence_score >= 0.0 AND confidence_score <= 1.0', name='check_confidence_range')
    )
    op.create_index('idx_verification_source_date', 'provider_verifications', ['source_type', 'verified_at'])
    
    # Confidence scores table
    op.create_table(
        'confidence_scores',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('provider_id', UUID(as_uuid=True), sa.ForeignKey('providers.id'), nullable=False, index=True),
        sa.Column('overall_score', sa.Float, nullable=False, index=True),
        sa.Column('verification_score', sa.Float, default=0.0),
        sa.Column('consistency_score', sa.Float, default=0.0),
        sa.Column('historical_score', sa.Float, default=0.0),
        sa.Column('external_score', sa.Float, default=0.0),
        sa.Column('model_version', sa.String(50), nullable=False),
        sa.Column('features_used', JSON, default={}),
        sa.Column('model_confidence', sa.Float, default=0.0),
        sa.Column('calculated_at', sa.DateTime(), default=sa.func.now(), index=True),
        sa.Column('calculated_by', sa.String(100)),
        sa.Column('expires_at', sa.DateTime()),
        sa.CheckConstraint('overall_score >= 0.0 AND overall_score <= 1.0', name='check_overall_score_range'),
        sa.CheckConstraint('verification_score >= 0.0 AND verification_score <= 1.0', name='check_verification_score_range')
    )
    op.create_index('idx_score_overall_date', 'confidence_scores', ['overall_score', 'calculated_at'])
    
    # Fraud alerts table
    op.create_table(
        'fraud_alerts',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('provider_id', UUID(as_uuid=True), sa.ForeignKey('providers.id'), nullable=False, index=True),
        sa.Column('alert_type', sa.String(50), nullable=False, index=True),
        sa.Column('risk_level', sa.String(20), nullable=False, index=True),
        sa.Column('fraud_score', sa.Float, nullable=False),
        sa.Column('detection_model', sa.String(50)),
        sa.Column('detection_features', JSON, default={}),
        sa.Column('detection_reason', sa.Text()),
        sa.Column('is_resolved', sa.Boolean, default=False, index=True),
        sa.Column('resolution_notes', sa.Text()),
        sa.Column('resolved_at', sa.DateTime()),
        sa.Column('resolved_by', sa.String(100)),
        sa.Column('detected_at', sa.DateTime(), default=sa.func.now(), index=True),
        sa.Column('detected_by', sa.String(100)),
        sa.CheckConstraint('fraud_score >= 0.0 AND fraud_score <= 1.0', name='check_fraud_score_range'),
        sa.CheckConstraint("risk_level IN ('low', 'medium', 'high', 'critical')", name='check_risk_level')
    )
    op.create_index('idx_fraud_risk_date', 'fraud_alerts', ['risk_level', 'detected_at'])
    op.create_index('idx_fraud_resolved', 'fraud_alerts', ['is_resolved', 'detected_at'])
    
    # Provenance records table
    op.create_table(
        'provenance_records',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('provider_id', UUID(as_uuid=True), sa.ForeignKey('providers.id'), nullable=False, index=True),
        sa.Column('block_hash', sa.String(64), unique=True, nullable=False, index=True),
        sa.Column('previous_hash', sa.String(64), nullable=False, index=True),
        sa.Column('merkle_root', sa.String(64), nullable=False),
        sa.Column('nonce', sa.Integer, default=0),
        sa.Column('difficulty', sa.Integer, default=1),
        sa.Column('transaction_type', sa.String(50), nullable=False, index=True),
        sa.Column('transaction_data', JSON, nullable=False),
        sa.Column('data_hash', sa.String(64), nullable=False),
        sa.Column('timestamp', sa.DateTime(), default=sa.func.now(), index=True),
        sa.Column('created_by', sa.String(100)),
        sa.Column('node_id', sa.String(100)),
        sa.Column('is_valid', sa.Boolean, default=True, index=True),
        sa.Column('validation_notes', sa.Text())
    )
    op.create_index('idx_provenance_hash_time', 'provenance_records', ['block_hash', 'timestamp'])
    op.create_index('idx_provenance_chain', 'provenance_records', ['previous_hash', 'timestamp'])
    
    # Compliance records table
    op.create_table(
        'compliance_records',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('provider_id', UUID(as_uuid=True), sa.ForeignKey('providers.id'), nullable=False, index=True),
        sa.Column('policy_name', sa.String(100), nullable=False, index=True),
        sa.Column('policy_version', sa.String(20)),
        sa.Column('compliance_status', sa.String(20), nullable=False, index=True),
        sa.Column('check_results', JSON, default={}),
        sa.Column('violations', JSON, default=[]),
        sa.Column('recommendations', JSON, default=[]),
        sa.Column('auto_resolved', sa.Boolean, default=False),
        sa.Column('resolution_actions', JSON, default=[]),
        sa.Column('resolution_notes', sa.Text()),
        sa.Column('checked_at', sa.DateTime(), default=sa.func.now(), index=True),
        sa.Column('checked_by', sa.String(100)),
        sa.Column('resolved_at', sa.DateTime()),
        sa.Column('next_check_at', sa.DateTime()),
        sa.CheckConstraint("compliance_status IN ('compliant', 'non_compliant', 'pending_review', 'exception_granted')", name='check_compliance_status')
    )
    op.create_index('idx_compliance_policy_status', 'compliance_records', ['policy_name', 'compliance_status'])
    op.create_index('idx_compliance_next_check', 'compliance_records', ['next_check_at'])
    
    # Federation nodes table
    op.create_table(
        'federation_nodes',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('node_id', sa.String(100), unique=True, nullable=False, index=True),
        sa.Column('node_name', sa.String(255), nullable=False),
        sa.Column('endpoint_url', sa.String(500), nullable=False),
        sa.Column('public_key', sa.Text(), nullable=False),
        sa.Column('is_active', sa.Boolean, default=True, index=True),
        sa.Column('is_trusted', sa.Boolean, default=False, index=True),
        sa.Column('trust_score', sa.Float, default=0.0),
        sa.Column('registered_at', sa.DateTime(), default=sa.func.now(), index=True),
        sa.Column('last_seen_at', sa.DateTime()),
        sa.Column('last_sync_at', sa.DateTime()),
        sa.Column('sync_config', JSON, default={}),
        sa.CheckConstraint('trust_score >= 0.0 AND trust_score <= 1.0', name='check_trust_score_range')
    )
    op.create_index('idx_node_status', 'federation_nodes', ['is_active', 'is_trusted'])
    
    # Audit logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('event_type', sa.String(50), nullable=False, index=True),
        sa.Column('event_category', sa.String(50), nullable=False, index=True),
        sa.Column('event_data', JSON, default={}),
        sa.Column('user_id', sa.String(100), index=True),
        sa.Column('agent_id', sa.String(100), index=True),
        sa.Column('session_id', sa.String(100)),
        sa.Column('ip_address', sa.String(45)),
        sa.Column('resource_type', sa.String(50)),
        sa.Column('resource_id', sa.String(100)),
        sa.Column('timestamp', sa.DateTime(), default=sa.func.now(), index=True),
        sa.Column('severity', sa.String(20), default='info')
    )
    op.create_index('idx_audit_type_time', 'audit_logs', ['event_type', 'timestamp'])
    op.create_index('idx_audit_user_time', 'audit_logs', ['user_id', 'timestamp'])
    op.create_index('idx_audit_resource', 'audit_logs', ['resource_type', 'resource_id'])


def downgrade() -> None:
    """Drop all tables"""
    op.drop_table('audit_logs')
    op.drop_table('federation_nodes')
    op.drop_table('compliance_records')
    op.drop_table('provenance_records')
    op.drop_table('fraud_alerts')
    op.drop_table('confidence_scores')
    op.drop_table('provider_verifications')
    op.drop_table('providers')
