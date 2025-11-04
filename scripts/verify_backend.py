#!/usr/bin/env python
"""
Quick verification script to test all backend components
"""
import sys
from pathlib import Path

def test_imports():
    """Test that all modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        # Core imports
        from app.core.config import get_settings
        from app.core.database import Base, engine
        from app.core.logging import setup_logging, get_logger
        from app.security.security import SecurityManager
        print("✓ Core modules")
        
        # Model imports
        from app.models import (
            Provider, ProviderVerification, ConfidenceScore,
            FraudAlert, ProvenanceRecord, ComplianceRecord,
            FederationNode, AuditLog
        )
        print("✓ Database models")
        
        # Blockchain imports
        from app.blockchain import Block, Blockchain, Transaction, MerkleTree
        print("✓ Blockchain components")
        
        # ML imports
        from app.ml import (
            ConfidenceScoreModel, FraudDetectionModel,
            FeatureExtractor, ModelManager
        )
        print("✓ ML models")
        
        # Agent imports
        from app.agents.orchestrator import OrchestratorAgent
        from app.agents.data_verification import DataVerificationAgent
        from app.agents.confidence_scoring import ConfidenceScoringAgent
        from app.agents.fraud_detection import FraudDetectionAgent
        from app.agents.provenance_ledger import ProvenanceLedgerAgent
        from app.agents.federated_publisher import FederatedPublisherAgent
        from app.agents.pitl import PITLAgent
        from app.agents.compliance_manager import ComplianceManagerAgent
        from app.agents.registry import agent_registry
        print("✓ All agents")
        
        # API imports
        from app.api.main import api_router
        from app.api.endpoints import providers, verification, admin, pitl, federation
        print("✓ API endpoints")
        
        # Main app
        from main import create_app
        print("✓ Main application")
        
        print("\n✅ All imports successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Import failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_blockchain():
    """Test blockchain functionality"""
    print("\n🔍 Testing blockchain...")
    
    try:
        from app.blockchain import Blockchain, Transaction
        from datetime import datetime
        
        # Create blockchain
        chain = Blockchain(genesis_hash="0" * 64, difficulty=1)
        print("✓ Blockchain initialized")
        
        # Add transaction
        tx = Transaction(
            transaction_id="test-1",
            transaction_type="test",
            provider_id="test-provider",
            data={"test": "data"},
            timestamp=datetime.utcnow().isoformat(),
            created_by="system"
        )
        chain.add_transaction(tx)
        print("✓ Transaction added")
        
        # Mine block
        block = chain.mine_pending_transactions()
        print(f"✓ Block mined: {block.hash[:16]}...")
        
        # Verify chain
        is_valid = chain.verify_chain()
        print(f"✓ Chain valid: {is_valid}")
        
        if not is_valid:
            print("❌ Blockchain validation failed!")
            return False
        
        print("\n✅ Blockchain tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Blockchain test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_ml_models():
    """Test ML model initialization"""
    print("\n🔍 Testing ML models...")
    
    try:
        from app.ml import ConfidenceScoreModel, FraudDetectionModel
        import numpy as np
        
        # Test confidence model
        confidence_model = ConfidenceScoreModel()
        print("✓ Confidence model initialized")
        
        # Test fraud model
        fraud_model = FraudDetectionModel()
        print("✓ Fraud detection model initialized")
        
        # Test feature extraction
        test_provider = {
            "verification_results": {
                "mci": {"confidence": 0.9},
                "insurance": {"confidence": 0.85}
            },
            "data_consistency_score": 0.8,
            "historical_score": 0.75,
            "external_validations": ["source1"],
            "created_at": "2024-01-01T00:00:00",
            "update_frequency_score": 0.6,
            "compliance_score": 0.7,
            "fraud_score": 0.2
        }
        
        features = confidence_model.extract_features(test_provider)
        print(f"✓ Features extracted: shape {features.shape}")
        
        print("\n✅ ML model tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ ML model test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_security():
    """Test security utilities"""
    print("\n🔍 Testing security...")
    
    try:
        from app.security.security import (
            hash_password, verify_password,
            create_access_token, mask_email, mask_phone
        )
        
        # Test password hashing
        password = "TestPassword123!"
        hashed = hash_password(password)
        is_valid = verify_password(password, hashed)
        print(f"✓ Password hashing: {is_valid}")
        
        # Test JWT
        token = create_access_token({"sub": "test-user"})
        print(f"✓ JWT token created: {token[:20]}...")
        
        # Test PII masking
        email = "test.user@example.com"
        masked_email = mask_email(email)
        print(f"✓ Email masking: {email} -> {masked_email}")
        
        phone = "+91-9876543210"
        masked_phone = mask_phone(phone)
        print(f"✓ Phone masking: {phone} -> {masked_phone}")
        
        print("\n✅ Security tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Security test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("🚀 TrueMesh Backend Verification")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Blockchain", test_blockchain()))
    results.append(("ML Models", test_ml_models()))
    results.append(("Security", test_security()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name:.<40} {status}")
    
    all_passed = all(r[1] for r in results)
    
    print("=" * 60)
    if all_passed:
        print("✅ All tests passed! Backend is ready.")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
