"""
Confidence Scoring Agent - ML-based trust and confidence scoring
"""
import os
import pickle
from typing import Dict, Any, Optional, List
from datetime import datetime
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib

from app.core.agent_base import BaseAgent, AgentTask, AgentResult, AgentStatus
from app.core.logging import get_logger


class ConfidenceScoringAgent(BaseAgent):
    """
    Confidence Scoring Agent - ML-based confidence and trust scoring
    
    Responsibilities:
    - Calculate trust scores using ML models
    - Evaluate data consistency
    - Assess historical patterns
    - Score external validation results
    - Update confidence scores in database
    """
    
    def __init__(self, agent_id: Optional[str] = None):
        super().__init__(agent_id)
        self.model = None
        self.scaler = None
        self.model_version = "1.0.0"
        self._load_or_create_model()
        
    def get_agent_type(self) -> str:
        return "confidence_scoring"
    
    def _load_or_create_model(self):
        """Load existing model or create new one"""
        model_dir = self.settings.model_storage_path
        model_path = os.path.join(model_dir, "confidence_model.pkl")
        scaler_path = os.path.join(model_dir, "confidence_scaler.pkl")
        
        try:
            if os.path.exists(model_path) and os.path.exists(scaler_path):
                self.model = joblib.load(model_path)
                self.scaler = joblib.load(scaler_path)
                self.logger.info("Loaded existing confidence scoring model")
            else:
                # Create new model
                self.model = RandomForestClassifier(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42
                )
                self.scaler = StandardScaler()
                
                # Train with dummy data for initialization
                self._train_initial_model()
                
                # Save model
                os.makedirs(model_dir, exist_ok=True)
                joblib.dump(self.model, model_path)
                joblib.dump(self.scaler, scaler_path)
                
                self.logger.info("Created new confidence scoring model")
                
        except Exception as e:
            self.logger.error(f"Failed to load/create model: {str(e)}")
            # Create fallback model
            self.model = RandomForestClassifier(n_estimators=50, random_state=42)
            self.scaler = StandardScaler()
            self._train_initial_model()
    
    def _train_initial_model(self):
        """Train model with initial dummy data"""
        # Generate synthetic training data
        np.random.seed(42)
        n_samples = 1000
        
        # Features: verification_count, avg_confidence, data_consistency, 
        # historical_score, external_validations, source_diversity
        X = np.random.rand(n_samples, 6)
        
        # Labels: 1 for high confidence (score > 0.7), 0 for low confidence
        y = (X[:, 1] > 0.5).astype(int)  # Based on avg_confidence
        
        # Fit scaler and model
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        
        self.logger.info("Trained initial confidence scoring model")
    
    async def process_task(self, task: AgentTask) -> AgentResult:
        """Process confidence scoring task"""
        start_time = datetime.utcnow()
        
        try:
            provider_data = task.data
            
            # Extract features from provider data
            features = self._extract_features(provider_data)
            
            # Calculate confidence scores
            scores = self._calculate_confidence_scores(features, provider_data)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return AgentResult(
                task_id=task.id,
                agent_id=self.agent_id,
                status=AgentStatus.COMPLETED,
                result={
                    "confidence_scores": scores,
                    "overall_score": scores["overall_score"],
                    "model_version": self.model_version,
                    "calculated_at": datetime.utcnow().isoformat(),
                },
                execution_time=execution_time,
                metadata={
                    "model_version": self.model_version,
                    "features_count": len(features),
                }
            )
            
        except Exception as e:
            self.logger.error(f"Confidence scoring failed: {str(e)}", task_id=task.id)
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return AgentResult(
                task_id=task.id,
                agent_id=self.agent_id,
                status=AgentStatus.FAILED,
                error=str(e),
                execution_time=execution_time
            )
    
    def _extract_features(self, provider_data: Dict[str, Any]) -> np.ndarray:
        """Extract features from provider data for ML model"""
        # Feature 1: Verification count
        verification_results = provider_data.get("verification_results", {})
        verification_count = sum(
            1 for v in verification_results.values()
            if v and v.get("status") == "verified"
        )
        
        # Feature 2: Average verification confidence
        confidences = [
            v.get("confidence", 0.0)
            for v in verification_results.values()
            if v and "confidence" in v
        ]
        avg_confidence = np.mean(confidences) if confidences else 0.0
        
        # Feature 3: Data consistency (0-1 scale)
        data_consistency = self._calculate_data_consistency(provider_data)
        
        # Feature 4: Historical score (from previous records, defaulting to 0.5)
        historical_score = provider_data.get("historical_score", 0.5)
        
        # Feature 5: External validations count
        external_validations = len([
            v for v in verification_results.values()
            if v and v.get("status") == "verified"
        ])
        
        # Feature 6: Source diversity (unique sources verified)
        source_diversity = len([
            k for k, v in verification_results.items()
            if v and v.get("status") == "verified"
        ]) / max(len(verification_results), 1)
        
        features = np.array([
            verification_count / 10.0,  # Normalize to 0-1
            avg_confidence,
            data_consistency,
            historical_score,
            external_validations / 5.0,  # Normalize to 0-1
            source_diversity,
        ])
        
        return features
    
    def _calculate_data_consistency(self, provider_data: Dict[str, Any]) -> float:
        """Calculate data consistency score"""
        # Check if key fields are present and non-empty
        required_fields = ["registration_number", "name", "provider_type"]
        optional_fields = ["email", "phone", "city", "state"]
        
        required_score = sum(
            1 for field in required_fields
            if provider_data.get(field)
        ) / len(required_fields)
        
        optional_score = sum(
            1 for field in optional_fields
            if provider_data.get(field)
        ) / len(optional_fields)
        
        # Weighted average (required fields are more important)
        consistency_score = (required_score * 0.7) + (optional_score * 0.3)
        
        return consistency_score
    
    def _calculate_confidence_scores(self, features: np.ndarray, provider_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate comprehensive confidence scores"""
        # Scale features
        features_scaled = self.scaler.transform(features.reshape(1, -1))
        
        # Get ML model prediction probability
        model_confidence = self.model.predict_proba(features_scaled)[0][1]
        
        # Calculate component scores
        verification_score = features[1]  # avg_confidence
        consistency_score = features[2]  # data_consistency
        historical_score = features[3]   # historical_score
        external_score = features[4]     # external_validations (normalized)
        
        # Calculate overall score as weighted average
        overall_score = (
            model_confidence * 0.30 +
            verification_score * 0.25 +
            consistency_score * 0.20 +
            historical_score * 0.15 +
            external_score * 0.10
        )
        
        # Ensure score is between 0 and 1
        overall_score = max(0.0, min(1.0, overall_score))
        
        return {
            "overall_score": round(overall_score, 3),
            "verification_score": round(verification_score, 3),
            "consistency_score": round(consistency_score, 3),
            "historical_score": round(historical_score, 3),
            "external_score": round(external_score, 3),
            "model_confidence": round(model_confidence, 3),
        }
    
    def retrain_model(self, training_data: List[Dict[str, Any]]):
        """Retrain the model with new data"""
        try:
            if len(training_data) < 10:
                self.logger.warning("Insufficient training data for retraining")
                return
            
            # Extract features and labels
            X = []
            y = []
            
            for data in training_data:
                features = self._extract_features(data)
                X.append(features)
                
                # Label based on verified status and confidence
                label = 1 if data.get("is_verified", False) and data.get("confidence_score", 0) > 0.7 else 0
                y.append(label)
            
            X = np.array(X)
            y = np.array(y)
            
            # Retrain scaler and model
            X_scaled = self.scaler.fit_transform(X)
            self.model.fit(X_scaled, y)
            
            # Save updated model
            model_dir = self.settings.model_storage_path
            os.makedirs(model_dir, exist_ok=True)
            joblib.dump(self.model, os.path.join(model_dir, "confidence_model.pkl"))
            joblib.dump(self.scaler, os.path.join(model_dir, "confidence_scaler.pkl"))
            
            self.logger.info(f"Model retrained with {len(training_data)} samples")
            
        except Exception as e:
            self.logger.error(f"Model retraining failed: {str(e)}")
