"""
Database models for TrueMesh Provider Intelligence
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
import json

from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, Text, Float, 
    ForeignKey, JSON, Index, UniqueConstraint, CheckConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.core.database import Base


class ProviderStatus(str, Enum):
    """Provider verification status"""
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    SUSPENDED = "suspended"
    UNDER_REVIEW = "under_review"


class DataSourceType(str, Enum):
    """Data source types"""
    MCI_REGISTRY = "mci_registry"
    INSURANCE_REGISTRY = "insurance_registry"
    PROVIDER_SELF_REPORTED = "provider_self_reported"
    TPA_VERIFICATION = "tpa_verification"
    GOVERNMENT_DATABASE = "government_database"
    THIRD_PARTY_VERIFICATION = "third_party_verification"


class FraudRiskLevel(str, Enum):
    """Fraud risk levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ComplianceStatus(str, Enum):
    """Compliance status"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PENDING_REVIEW = "pending_review"
    EXCEPTION_GRANTED = "exception_granted"


class Provider(Base):
    """Healthcare provider model"""
    __tablename__ = "providers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic Information
    registration_number = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    provider_type = Column(String(50), nullable=False)  # doctor, hospital, clinic, pharmacy
    specialization = Column(String(100))
    
    # Contact Information
    email = Column(String(255), index=True)
    phone = Column(String(20))
    address_line1 = Column(String(255))
    address_line2 = Column(String(255))
    city = Column(String(100), index=True)
    state = Column(String(100), index=True)
    postal_code = Column(String(20))
    country = Column(String(100), default="India")
    
    # Verification Status
    status = Column(String(20), default=ProviderStatus.PENDING.value, index=True)
    verified_at = Column(DateTime)
    verification_expires_at = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(100))
    updated_by = Column(String(100))
    
    # Additional data as JSON
    additional_data = Column(JSON, default={})
    
    # Relationships
    verifications = relationship("ProviderVerification", back_populates="provider", cascade="all, delete-orphan")
    scores = relationship("ConfidenceScore", back_populates="provider", cascade="all, delete-orphan")
    fraud_alerts = relationship("FraudAlert", back_populates="provider", cascade="all, delete-orphan")
    provenance_records = relationship("ProvenanceRecord", back_populates="provider", cascade="all, delete-orphan")
    compliance_records = relationship("ComplianceRecord", back_populates="provider", cascade="all, delete-orphan")
    
    # Indexes and constraints
    __table_args__ = (
        Index("idx_provider_location", "state", "city"),
        Index("idx_provider_type_status", "provider_type", "status"),
        CheckConstraint("status IN ('pending', 'verified', 'rejected', 'suspended', 'under_review')", name="check_provider_status"),
    )


class ProviderVerification(Base):
    """Provider data verification records"""
    __tablename__ = "provider_verifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider_id = Column(UUID(as_uuid=True), ForeignKey("providers.id"), nullable=False, index=True)
    
    # Verification details
    source_type = Column(String(50), nullable=False, index=True)
    source_url = Column(String(500))
    verification_data = Column(JSON, default={})
    
    # Results
    is_verified = Column(Boolean, nullable=False, default=False)
    confidence_score = Column(Float, default=0.0)
    verification_notes = Column(Text)
    
    # Metadata
    verified_at = Column(DateTime, default=datetime.utcnow, index=True)
    verified_by = Column(String(100))  # Agent ID
    expires_at = Column(DateTime)
    
    # Relationships
    provider = relationship("Provider", back_populates="verifications")
    
    __table_args__ = (
        Index("idx_verification_source_date", "source_type", "verified_at"),
        CheckConstraint("confidence_score >= 0.0 AND confidence_score <= 1.0", name="check_confidence_range"),
    )


class ConfidenceScore(Base):
    """Provider confidence scoring records"""
    __tablename__ = "confidence_scores"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider_id = Column(UUID(as_uuid=True), ForeignKey("providers.id"), nullable=False, index=True)
    
    # Scores
    overall_score = Column(Float, nullable=False, index=True)
    verification_score = Column(Float, default=0.0)
    consistency_score = Column(Float, default=0.0)
    historical_score = Column(Float, default=0.0)
    external_score = Column(Float, default=0.0)
    
    # Model information
    model_version = Column(String(50), nullable=False)
    features_used = Column(JSON, default={})
    model_confidence = Column(Float, default=0.0)
    
    # Metadata
    calculated_at = Column(DateTime, default=datetime.utcnow, index=True)
    calculated_by = Column(String(100))  # Agent ID
    expires_at = Column(DateTime)
    
    # Relationships
    provider = relationship("Provider", back_populates="scores")
    
    __table_args__ = (
        Index("idx_score_overall_date", "overall_score", "calculated_at"),
        CheckConstraint("overall_score >= 0.0 AND overall_score <= 1.0", name="check_overall_score_range"),
        CheckConstraint("verification_score >= 0.0 AND verification_score <= 1.0", name="check_verification_score_range"),
    )


class FraudAlert(Base):
    """Fraud detection alerts"""
    __tablename__ = "fraud_alerts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider_id = Column(UUID(as_uuid=True), ForeignKey("providers.id"), nullable=False, index=True)
    
    # Alert details
    alert_type = Column(String(50), nullable=False, index=True)
    risk_level = Column(String(20), nullable=False, index=True)
    fraud_score = Column(Float, nullable=False)
    
    # Detection information
    detection_model = Column(String(50))
    detection_features = Column(JSON, default={})
    detection_reason = Column(Text)
    
    # Status
    is_resolved = Column(Boolean, default=False, index=True)
    resolution_notes = Column(Text)
    resolved_at = Column(DateTime)
    resolved_by = Column(String(100))
    
    # Metadata
    detected_at = Column(DateTime, default=datetime.utcnow, index=True)
    detected_by = Column(String(100))  # Agent ID
    
    # Relationships
    provider = relationship("Provider", back_populates="fraud_alerts")
    
    __table_args__ = (
        Index("idx_fraud_risk_date", "risk_level", "detected_at"),
        Index("idx_fraud_resolved", "is_resolved", "detected_at"),
        CheckConstraint("fraud_score >= 0.0 AND fraud_score <= 1.0", name="check_fraud_score_range"),
        CheckConstraint("risk_level IN ('low', 'medium', 'high', 'critical')", name="check_risk_level"),
    )


class ProvenanceRecord(Base):
    """Provenance/blockchain ledger records"""
    __tablename__ = "provenance_records"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider_id = Column(UUID(as_uuid=True), ForeignKey("providers.id"), nullable=False, index=True)
    
    # Blockchain data
    block_hash = Column(String(64), unique=True, nullable=False, index=True)
    previous_hash = Column(String(64), nullable=False, index=True)
    merkle_root = Column(String(64), nullable=False)
    nonce = Column(Integer, default=0)
    difficulty = Column(Integer, default=1)
    
    # Transaction data
    transaction_type = Column(String(50), nullable=False, index=True)
    transaction_data = Column(JSON, nullable=False)
    data_hash = Column(String(64), nullable=False)
    
    # Metadata
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    created_by = Column(String(100))  # Agent ID or user ID
    node_id = Column(String(100))
    
    # Validation
    is_valid = Column(Boolean, default=True, index=True)
    validation_notes = Column(Text)
    
    # Relationships
    provider = relationship("Provider", back_populates="provenance_records")
    
    __table_args__ = (
        Index("idx_provenance_hash_time", "block_hash", "timestamp"),
        Index("idx_provenance_chain", "previous_hash", "timestamp"),
    )


class ComplianceRecord(Base):
    """Compliance and policy records"""
    __tablename__ = "compliance_records"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider_id = Column(UUID(as_uuid=True), ForeignKey("providers.id"), nullable=False, index=True)
    
    # Compliance details
    policy_name = Column(String(100), nullable=False, index=True)
    policy_version = Column(String(20))
    compliance_status = Column(String(20), nullable=False, index=True)
    
    # Check results
    check_results = Column(JSON, default={})
    violations = Column(JSON, default=[])
    recommendations = Column(JSON, default=[])
    
    # Resolution
    auto_resolved = Column(Boolean, default=False)
    resolution_actions = Column(JSON, default=[])
    resolution_notes = Column(Text)
    
    # Metadata
    checked_at = Column(DateTime, default=datetime.utcnow, index=True)
    checked_by = Column(String(100))  # Agent ID
    resolved_at = Column(DateTime)
    next_check_at = Column(DateTime)
    
    # Relationships
    provider = relationship("Provider", back_populates="compliance_records")
    
    __table_args__ = (
        Index("idx_compliance_policy_status", "policy_name", "compliance_status"),
        Index("idx_compliance_next_check", "next_check_at"),
        CheckConstraint("compliance_status IN ('compliant', 'non_compliant', 'pending_review', 'exception_granted')", name="check_compliance_status"),
    )


class FederationNode(Base):
    """Federation network nodes"""
    __tablename__ = "federation_nodes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Node information
    node_id = Column(String(100), unique=True, nullable=False, index=True)
    node_name = Column(String(255), nullable=False)
    endpoint_url = Column(String(500), nullable=False)
    public_key = Column(Text, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    is_trusted = Column(Boolean, default=False, index=True)
    trust_score = Column(Float, default=0.0)
    
    # Metadata
    registered_at = Column(DateTime, default=datetime.utcnow, index=True)
    last_seen_at = Column(DateTime)
    last_sync_at = Column(DateTime)
    
    # Configuration
    sync_config = Column(JSON, default={})
    
    __table_args__ = (
        Index("idx_node_status", "is_active", "is_trusted"),
        CheckConstraint("trust_score >= 0.0 AND trust_score <= 1.0", name="check_trust_score_range"),
    )


class AuditLog(Base):
    """System audit log"""
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Event details
    event_type = Column(String(50), nullable=False, index=True)
    event_category = Column(String(50), nullable=False, index=True)
    event_data = Column(JSON, default={})
    
    # Context
    user_id = Column(String(100), index=True)
    agent_id = Column(String(100), index=True)
    session_id = Column(String(100))
    ip_address = Column(String(45))
    
    # Resources affected
    resource_type = Column(String(50))
    resource_id = Column(String(100))
    
    # Metadata
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    severity = Column(String(20), default="info")
    
    __table_args__ = (
        Index("idx_audit_type_time", "event_type", "timestamp"),
        Index("idx_audit_user_time", "user_id", "timestamp"),
        Index("idx_audit_resource", "resource_type", "resource_id"),
    )
