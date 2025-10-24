"""
Fraud Detection Agent - Detects duplicate, fake, or inconsistent provider entries
"""
import os
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import hashlib

from app.core.agent_base import BaseAgent, AgentTask, AgentResult, AgentStatus
from app.core.logging import get_logger


class FraudDetectionAgent(BaseAgent):
    """
    Fraud Detection Agent - Detects fraudulent provider entries
    
    Responsibilities:
    - Detect duplicate provider entries
    - Identify fake or synthetic data
    - Find data inconsistencies
    - Calculate fraud risk scores
    - Flag suspicious patterns
    """
    
    def __init__(self, agent_id: Optional[str] = None):
        super().__init__(agent_id)
        self.model = None
        self.scaler = None
        self.model_version = "1.0.0"
        self.known_providers_hash = set()  # For duplicate detection
        self._load_or_create_model()
        
    def get_agent_type(self) -> str:
        return "fraud_detection"
    
    def _load_or_create_model(self):
        """Load existing model or create new one"""
        model_dir = self.settings.model_storage_path
        model_path = os.path.join(model_dir, "fraud_detection_model.pkl")
        scaler_path = os.path.join(model_dir, "fraud_detection_scaler.pkl")
        
        try:
            if os.path.exists(model_path) and os.path.exists(scaler_path):
                self.model = joblib.load(model_path)
                self.scaler = joblib.load(scaler_path)
                self.logger.info("Loaded existing fraud detection model")
            else:
                # Create new Isolation Forest model for anomaly detection
                self.model = IsolationForest(
                    n_estimators=100,
                    contamination=0.1,
                    random_state=42
                )
                self.scaler = StandardScaler()
                
                # Train with dummy data for initialization
                self._train_initial_model()
                
                # Save model
                os.makedirs(model_dir, exist_ok=True)
                joblib.dump(self.model, model_path)
                joblib.dump(self.scaler, scaler_path)
                
                self.logger.info("Created new fraud detection model")
                
        except Exception as e:
            self.logger.error(f"Failed to load/create fraud model: {str(e)}")
            # Create fallback model
            self.model = IsolationForest(n_estimators=50, random_state=42)
            self.scaler = StandardScaler()
            self._train_initial_model()
    
    def _train_initial_model(self):
        """Train model with initial dummy data"""
        # Generate synthetic normal behavior data
        np.random.seed(42)
        n_samples = 1000
        
        # Features: data_completeness, pattern_consistency, registration_format,
        # contact_validity, location_validity, verification_diversity
        # Normal data: high completeness, consistent patterns
        X_normal = np.random.uniform(0.6, 1.0, (int(n_samples * 0.9), 6))
        
        # Anomalous data: low completeness, inconsistent patterns
        X_anomaly = np.random.uniform(0.0, 0.4, (int(n_samples * 0.1), 6))
        
        X = np.vstack([X_normal, X_anomaly])
        
        # Fit scaler and model
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled)
        
        self.logger.info("Trained initial fraud detection model")
    
    async def process_task(self, task: AgentTask) -> AgentResult:
        """Process fraud detection task"""
        start_time = datetime.utcnow()
        
        try:
            provider_data = task.data
            
            # Perform multiple fraud checks
            fraud_checks = await self.detect_fraud(provider_data)
            
            # Calculate overall fraud score and risk level
            fraud_score = fraud_checks["fraud_score"]
            risk_level = self._determine_risk_level(fraud_score)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return AgentResult(
                task_id=task.id,
                agent_id=self.agent_id,
                status=AgentStatus.COMPLETED,
                result={
                    "fraud_score": fraud_score,
                    "risk_level": risk_level,
                    "fraud_checks": fraud_checks,
                    "is_fraudulent": fraud_score > self.settings.fraud_threshold,
                    "detected_at": datetime.utcnow().isoformat(),
                },
                execution_time=execution_time,
                metadata={
                    "model_version": self.model_version,
                    "risk_level": risk_level,
                }
            )
            
        except Exception as e:
            self.logger.error(f"Fraud detection failed: {str(e)}", task_id=task.id)
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return AgentResult(
                task_id=task.id,
                agent_id=self.agent_id,
                status=AgentStatus.FAILED,
                error=str(e),
                execution_time=execution_time
            )
    
    async def detect_fraud(self, provider_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive fraud detection"""
        checks = {}
        
        # 1. Duplicate detection
        checks["duplicate_check"] = self._check_duplicate(provider_data)
        
        # 2. Data inconsistency check
        checks["inconsistency_check"] = self._check_inconsistencies(provider_data)
        
        # 3. Fake data patterns
        checks["fake_pattern_check"] = self._check_fake_patterns(provider_data)
        
        # 4. ML-based anomaly detection
        checks["anomaly_check"] = self._check_anomaly(provider_data)
        
        # 5. Registration number validation
        checks["registration_validity"] = self._validate_registration_number(provider_data)
        
        # Calculate overall fraud score
        fraud_score = self._calculate_fraud_score(checks)
        
        return {
            "fraud_score": fraud_score,
            "checks": checks,
            "detection_method": "multi_check",
        }
    
    def _check_duplicate(self, provider_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check for duplicate provider entries"""
        # Create hash from key identifying fields
        identifier = f"{provider_data.get('registration_number', '')}{provider_data.get('name', '')}{provider_data.get('phone', '')}"
        provider_hash = hashlib.sha256(identifier.encode()).hexdigest()
        
        is_duplicate = provider_hash in self.known_providers_hash
        
        if not is_duplicate:
            self.known_providers_hash.add(provider_hash)
        
        return {
            "is_duplicate": is_duplicate,
            "confidence": 1.0 if is_duplicate else 0.0,
            "reason": "Exact match found in system" if is_duplicate else "No duplicate found",
        }
    
    def _check_inconsistencies(self, provider_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check for data inconsistencies"""
        inconsistencies = []
        
        # Check name consistency
        name = provider_data.get("name", "")
        if name and len(name) < 3:
            inconsistencies.append("Name too short")
        
        # Check registration number format
        reg_num = provider_data.get("registration_number", "")
        if reg_num and not reg_num.isalnum():
            inconsistencies.append("Invalid registration number format")
        
        # Check phone number format (Indian format)
        phone = provider_data.get("phone", "")
        if phone and (len(phone) < 10 or not phone.replace("+", "").replace("-", "").isdigit()):
            inconsistencies.append("Invalid phone number format")
        
        # Check email format
        email = provider_data.get("email", "")
        if email and "@" not in email:
            inconsistencies.append("Invalid email format")
        
        # Check verification results consistency
        verification_results = provider_data.get("verification_results", {})
        verified_sources = sum(
            1 for v in verification_results.values()
            if v and v.get("status") == "verified"
        )
        
        if verified_sources == 0 and len(verification_results) > 0:
            inconsistencies.append("No sources verified")
        
        inconsistency_score = len(inconsistencies) / 5.0  # Normalize to 0-1
        
        return {
            "has_inconsistencies": len(inconsistencies) > 0,
            "inconsistencies": inconsistencies,
            "score": min(inconsistency_score, 1.0),
        }
    
    def _check_fake_patterns(self, provider_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check for patterns typical of fake data"""
        fake_indicators = []
        
        # Sequential or pattern-based registration numbers
        reg_num = provider_data.get("registration_number", "")
        if reg_num and (reg_num == "123456" or reg_num == "ABCDEF"):
            fake_indicators.append("Sequential registration number")
        
        # Generic or placeholder names
        name = provider_data.get("name", "").lower()
        if any(keyword in name for keyword in ["test", "demo", "fake", "sample"]):
            fake_indicators.append("Generic/placeholder name")
        
        # Missing critical information
        required_fields = ["registration_number", "name", "provider_type"]
        missing_fields = [f for f in required_fields if not provider_data.get(f)]
        if len(missing_fields) > 1:
            fake_indicators.append(f"Missing critical fields: {', '.join(missing_fields)}")
        
        # All fields too perfect (uncommon in real data)
        all_fields = ["registration_number", "name", "email", "phone", "address_line1", "city", "state"]
        filled_fields = sum(1 for f in all_fields if provider_data.get(f))
        if filled_fields == len(all_fields):
            # This is actually good, not a fake indicator
            pass
        
        fake_score = len(fake_indicators) / 3.0  # Normalize to 0-1
        
        return {
            "has_fake_patterns": len(fake_indicators) > 0,
            "indicators": fake_indicators,
            "score": min(fake_score, 1.0),
        }
    
    def _check_anomaly(self, provider_data: Dict[str, Any]) -> Dict[str, Any]:
        """ML-based anomaly detection"""
        try:
            # Extract features for anomaly detection
            features = self._extract_anomaly_features(provider_data)
            
            # Scale and predict
            features_scaled = self.scaler.transform(features.reshape(1, -1))
            prediction = self.model.predict(features_scaled)[0]
            anomaly_score = self.model.score_samples(features_scaled)[0]
            
            # prediction: 1 = normal, -1 = anomaly
            is_anomaly = prediction == -1
            
            # Convert anomaly score to 0-1 range (higher = more anomalous)
            normalized_score = 1.0 if is_anomaly else 0.0
            
            return {
                "is_anomaly": is_anomaly,
                "score": normalized_score,
                "anomaly_score": float(anomaly_score),
            }
            
        except Exception as e:
            self.logger.error(f"Anomaly detection failed: {str(e)}")
            return {
                "is_anomaly": False,
                "score": 0.0,
                "error": str(e),
            }
    
    def _extract_anomaly_features(self, provider_data: Dict[str, Any]) -> np.ndarray:
        """Extract features for anomaly detection"""
        # Feature 1: Data completeness
        all_fields = ["registration_number", "name", "email", "phone", "city", "state"]
        completeness = sum(1 for f in all_fields if provider_data.get(f)) / len(all_fields)
        
        # Feature 2: Pattern consistency (based on field lengths)
        name_len = len(provider_data.get("name", "")) / 100.0
        reg_len = len(provider_data.get("registration_number", "")) / 20.0
        
        # Feature 3: Registration format validity
        reg_num = provider_data.get("registration_number", "")
        reg_validity = 1.0 if reg_num and reg_num.isalnum() else 0.0
        
        # Feature 4: Contact validity
        email = provider_data.get("email", "")
        phone = provider_data.get("phone", "")
        contact_validity = (("@" in email) + (len(phone) >= 10)) / 2.0
        
        # Feature 5: Location validity
        location_validity = 1.0 if provider_data.get("city") and provider_data.get("state") else 0.0
        
        # Feature 6: Verification diversity
        verification_results = provider_data.get("verification_results", {})
        verification_diversity = len([
            v for v in verification_results.values()
            if v and v.get("status") == "verified"
        ]) / 3.0
        
        features = np.array([
            completeness,
            min(name_len, 1.0),
            min(reg_len, 1.0),
            reg_validity,
            contact_validity,
            location_validity,
        ])
        
        return features
    
    def _validate_registration_number(self, provider_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate registration number format and structure"""
        reg_num = provider_data.get("registration_number", "")
        provider_type = provider_data.get("provider_type", "")
        
        is_valid = True
        issues = []
        
        if not reg_num:
            is_valid = False
            issues.append("Registration number missing")
        elif len(reg_num) < 6:
            is_valid = False
            issues.append("Registration number too short")
        elif not reg_num.isalnum():
            is_valid = False
            issues.append("Registration number contains invalid characters")
        
        validity_score = 0.0 if not is_valid else 1.0
        
        return {
            "is_valid": is_valid,
            "issues": issues,
            "score": validity_score,
        }
    
    def _calculate_fraud_score(self, checks: Dict[str, Any]) -> float:
        """Calculate overall fraud score from all checks"""
        # Weight different checks
        weights = {
            "duplicate_check": 0.30,
            "inconsistency_check": 0.20,
            "fake_pattern_check": 0.25,
            "anomaly_check": 0.15,
            "registration_validity": 0.10,
        }
        
        total_score = 0.0
        
        # Duplicate check
        if checks.get("duplicate_check", {}).get("is_duplicate"):
            total_score += weights["duplicate_check"]
        
        # Inconsistency check
        total_score += checks.get("inconsistency_check", {}).get("score", 0.0) * weights["inconsistency_check"]
        
        # Fake pattern check
        total_score += checks.get("fake_pattern_check", {}).get("score", 0.0) * weights["fake_pattern_check"]
        
        # Anomaly check
        total_score += checks.get("anomaly_check", {}).get("score", 0.0) * weights["anomaly_check"]
        
        # Registration validity (inverse - higher invalidity = higher fraud score)
        reg_validity = checks.get("registration_validity", {}).get("score", 1.0)
        total_score += (1.0 - reg_validity) * weights["registration_validity"]
        
        return min(total_score, 1.0)
    
    def _determine_risk_level(self, fraud_score: float) -> str:
        """Determine risk level from fraud score"""
        if fraud_score >= 0.8:
            return "critical"
        elif fraud_score >= 0.6:
            return "high"
        elif fraud_score >= 0.4:
            return "medium"
        else:
            return "low"
