"""
Machine Learning module for TrueMesh Provider Intelligence

Complete ML implementation for:
1. Confidence Scoring - Trust and confidence assessment
2. Fraud Detection - Anomaly and fraud detection
3. Feature Engineering - Feature extraction and preprocessing
4. Model Management - Model versioning and lifecycle
"""

import os
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score
import joblib
from pathlib import Path
import json


class ConfidenceScoreModel:
    """
    Confidence scoring model for provider trust assessment
    
    Uses Random Forest Classifier to predict confidence levels
    based on verification data, historical patterns, and external validations.
    """
    
    def __init__(self, model_path: Optional[str] = None):
        self.model: Optional[RandomForestClassifier] = None
        self.scaler: Optional[StandardScaler] = None
        self.version = "1.0.0"
        self.feature_names = [
            "verification_count",
            "avg_verification_confidence",
            "data_consistency_score",
            "historical_pattern_score",
            "external_validation_count",
            "source_diversity_score",
            "time_since_registration_days",
            "update_frequency_score",
            "compliance_score",
            "fraud_risk_score"
        ]
        
        if model_path:
            self.load(model_path)
        else:
            self._initialize_model()
    
    def _initialize_model(self):
        """Initialize model with optimized parameters"""
        self.model = RandomForestClassifier(
            n_estimators=150,
            max_depth=12,
            min_samples_split=5,
            min_samples_leaf=2,
            max_features='sqrt',
            random_state=42,
            n_jobs=-1
        )
        self.scaler = StandardScaler()
    
    def extract_features(self, provider_data: Dict[str, Any]) -> np.ndarray:
        """
        Extract features from provider data
        
        Args:
            provider_data: Provider information and verification results
            
        Returns:
            Feature array
        """
        features = []
        
        # Verification count
        verification_results = provider_data.get("verification_results", {})
        features.append(len(verification_results))
        
        # Average verification confidence
        confidences = [
            v.get("confidence", 0.0) 
            for v in verification_results.values()
        ]
        features.append(np.mean(confidences) if confidences else 0.0)
        
        # Data consistency score
        features.append(provider_data.get("data_consistency_score", 0.5))
        
        # Historical pattern score
        features.append(provider_data.get("historical_score", 0.5))
        
        # External validation count
        external_validations = provider_data.get("external_validations", [])
        features.append(len(external_validations))
        
        # Source diversity (unique verification sources)
        unique_sources = len(set(v.get("source", "") for v in verification_results.values()))
        features.append(unique_sources / max(len(verification_results), 1))
        
        # Time since registration
        from datetime import datetime
        created_at = provider_data.get("created_at", datetime.utcnow().isoformat())
        try:
            created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            days_since = (datetime.utcnow() - created_date).days
            features.append(min(days_since, 365) / 365.0)  # Normalize to [0, 1]
        except:
            features.append(0.0)
        
        # Update frequency score
        features.append(provider_data.get("update_frequency_score", 0.5))
        
        # Compliance score
        features.append(provider_data.get("compliance_score", 0.5))
        
        # Fraud risk score (inverted - lower fraud = higher confidence)
        fraud_score = provider_data.get("fraud_score", 0.0)
        features.append(1.0 - fraud_score)
        
        return np.array(features).reshape(1, -1)
    
    def train(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """
        Train the confidence scoring model
        
        Args:
            X: Feature matrix (n_samples, n_features)
            y: Labels (0 = low confidence, 1 = high confidence)
            
        Returns:
            Training metrics
        """
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled, y)
        
        # Evaluate with cross-validation
        cv_scores = cross_val_score(self.model, X_scaled, y, cv=5)
        
        return {
            "accuracy": self.model.score(X_scaled, y),
            "cv_accuracy_mean": cv_scores.mean(),
            "cv_accuracy_std": cv_scores.std()
        }
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict confidence scores
        
        Args:
            X: Feature matrix
            
        Returns:
            Confidence probabilities (0 to 1)
        """
        if self.model is None or self.scaler is None:
            raise ValueError("Model not trained or loaded")
        
        X_scaled = self.scaler.transform(X)
        # Get probability of high confidence class
        probabilities = self.model.predict_proba(X_scaled)
        return probabilities[:, 1]  # Probability of class 1 (high confidence)
    
    def predict_with_breakdown(self, provider_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict confidence score with feature importance breakdown
        
        Args:
            provider_data: Provider information
            
        Returns:
            Prediction result with breakdown
        """
        features = self.extract_features(provider_data)
        confidence = self.predict(features)[0]
        
        # Get feature importances
        feature_importance = dict(zip(
            self.feature_names,
            self.model.feature_importances_
        ))
        
        return {
            "overall_score": float(confidence),
            "feature_values": dict(zip(self.feature_names, features[0])),
            "feature_importance": feature_importance,
            "model_version": self.version
        }
    
    def save(self, path: str):
        """Save model and scaler to disk"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        model_data = {
            "model": self.model,
            "scaler": self.scaler,
            "version": self.version,
            "feature_names": self.feature_names
        }
        
        joblib.dump(model_data, path)
    
    def load(self, path: str):
        """Load model and scaler from disk"""
        model_data = joblib.load(path)
        
        self.model = model_data["model"]
        self.scaler = model_data["scaler"]
        self.version = model_data.get("version", "1.0.0")
        self.feature_names = model_data.get("feature_names", self.feature_names)


class FraudDetectionModel:
    """
    Fraud detection model using Isolation Forest
    
    Detects anomalies and potential fraud in provider data
    using unsupervised learning.
    """
    
    def __init__(self, model_path: Optional[str] = None):
        self.model: Optional[IsolationForest] = None
        self.scaler: Optional[StandardScaler] = None
        self.version = "1.0.0"
        self.feature_names = [
            "claim_frequency",
            "avg_claim_amount",
            "claim_amount_std",
            "approval_rate",
            "duplicate_claims_ratio",
            "verification_inconsistency_score",
            "location_anomaly_score",
            "billing_pattern_score",
            "time_pattern_score",
            "relationship_network_score"
        ]
        self.threshold = -0.5  # Anomaly score threshold
        
        if model_path:
            self.load(model_path)
        else:
            self._initialize_model()
    
    def _initialize_model(self):
        """Initialize model with optimized parameters"""
        self.model = IsolationForest(
            n_estimators=150,
            max_samples='auto',
            contamination=0.1,  # Expected 10% anomaly rate
            max_features=1.0,
            random_state=42,
            n_jobs=-1
        )
        self.scaler = StandardScaler()
    
    def extract_features(self, provider_data: Dict[str, Any]) -> np.ndarray:
        """
        Extract fraud detection features from provider data
        
        Args:
            provider_data: Provider information and activity data
            
        Returns:
            Feature array
        """
        features = []
        
        # Claim frequency (claims per month)
        total_claims = provider_data.get("total_claims", 0)
        months_active = max(provider_data.get("months_active", 1), 1)
        features.append(total_claims / months_active)
        
        # Average claim amount
        features.append(provider_data.get("avg_claim_amount", 0.0))
        
        # Claim amount standard deviation
        features.append(provider_data.get("claim_amount_std", 0.0))
        
        # Approval rate
        approved = provider_data.get("approved_claims", 0)
        features.append(approved / max(total_claims, 1))
        
        # Duplicate claims ratio
        features.append(provider_data.get("duplicate_claims_ratio", 0.0))
        
        # Verification inconsistency score
        features.append(provider_data.get("verification_inconsistency", 0.0))
        
        # Location anomaly score
        features.append(provider_data.get("location_anomaly", 0.0))
        
        # Billing pattern score
        features.append(provider_data.get("billing_pattern_score", 0.5))
        
        # Time pattern score (unusual activity times)
        features.append(provider_data.get("time_pattern_score", 0.5))
        
        # Relationship network score
        features.append(provider_data.get("network_score", 0.5))
        
        return np.array(features).reshape(1, -1)
    
    def train(self, X: np.ndarray) -> Dict[str, Any]:
        """
        Train the fraud detection model
        
        Args:
            X: Feature matrix (n_samples, n_features)
            
        Returns:
            Training metrics
        """
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled)
        
        # Get anomaly scores
        scores = self.model.score_samples(X_scaled)
        predictions = self.model.predict(X_scaled)
        
        anomaly_count = np.sum(predictions == -1)
        
        return {
            "samples_trained": len(X),
            "anomalies_detected": int(anomaly_count),
            "anomaly_rate": float(anomaly_count / len(X)),
            "score_mean": float(scores.mean()),
            "score_std": float(scores.std())
        }
    
    def predict(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predict fraud probability and anomaly scores
        
        Args:
            X: Feature matrix
            
        Returns:
            Tuple of (predictions, scores)
            predictions: -1 for anomaly, 1 for normal
            scores: anomaly scores (lower = more anomalous)
        """
        if self.model is None or self.scaler is None:
            raise ValueError("Model not trained or loaded")
        
        X_scaled = self.scaler.transform(X)
        predictions = self.model.predict(X_scaled)
        scores = self.model.score_samples(X_scaled)
        
        return predictions, scores
    
    def predict_with_risk_level(self, provider_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict fraud risk with detailed breakdown
        
        Args:
            provider_data: Provider information
            
        Returns:
            Prediction result with risk assessment
        """
        features = self.extract_features(provider_data)
        predictions, scores = self.predict(features)
        
        is_anomaly = predictions[0] == -1
        anomaly_score = scores[0]
        
        # Convert anomaly score to fraud probability (0 to 1)
        # Normalize using sigmoid-like function
        fraud_score = 1.0 / (1.0 + np.exp(anomaly_score * 2))
        
        # Determine risk level
        if fraud_score >= 0.8:
            risk_level = "critical"
        elif fraud_score >= 0.6:
            risk_level = "high"
        elif fraud_score >= 0.4:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return {
            "is_fraudulent": bool(is_anomaly),
            "fraud_score": float(fraud_score),
            "anomaly_score": float(anomaly_score),
            "risk_level": risk_level,
            "feature_values": dict(zip(self.feature_names, features[0])),
            "model_version": self.version
        }
    
    def save(self, path: str):
        """Save model and scaler to disk"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        model_data = {
            "model": self.model,
            "scaler": self.scaler,
            "version": self.version,
            "feature_names": self.feature_names,
            "threshold": self.threshold
        }
        
        joblib.dump(model_data, path)
    
    def load(self, path: str):
        """Load model and scaler from disk"""
        model_data = joblib.load(path)
        
        self.model = model_data["model"]
        self.scaler = model_data["scaler"]
        self.version = model_data.get("version", "1.0.0")
        self.feature_names = model_data.get("feature_names", self.feature_names)
        self.threshold = model_data.get("threshold", -0.5)


class FeatureExtractor:
    """
    Feature extraction utilities for ML models
    
    Provides standardized feature extraction and preprocessing
    for confidence scoring and fraud detection.
    """
    
    @staticmethod
    def extract_confidence_features(provider_data: Dict[str, Any]) -> np.ndarray:
        """
        Extract features for confidence scoring
        
        Args:
            provider_data: Provider information
            
        Returns:
            Feature array
        """
        model = ConfidenceScoreModel()
        return model.extract_features(provider_data)
    
    @staticmethod
    def extract_fraud_features(provider_data: Dict[str, Any]) -> np.ndarray:
        """
        Extract features for fraud detection
        
        Args:
            provider_data: Provider information
            
        Returns:
            Feature array
        """
        model = FraudDetectionModel()
        return model.extract_features(provider_data)
    
    @staticmethod
    def normalize_features(features: np.ndarray) -> np.ndarray:
        """Normalize features using standard scaling"""
        scaler = StandardScaler()
        return scaler.fit_transform(features)


class ModelManager:
    """
    Model lifecycle management
    
    Handles model versioning, registry, and deployment.
    """
    
    def __init__(self, storage_path: str):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.models: Dict[str, Any] = {}
        self.registry_file = self.storage_path / "model_registry.json"
        self._load_registry()
    
    def _load_registry(self):
        """Load model registry from disk"""
        if self.registry_file.exists():
            with open(self.registry_file, 'r') as f:
                self.models = json.load(f)
        else:
            self.models = {}
    
    def _save_registry(self):
        """Save model registry to disk"""
        with open(self.registry_file, 'w') as f:
            json.dump(self.models, f, indent=2)
    
    def register_model(
        self,
        name: str,
        model: Any,
        version: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Register a model in the registry
        
        Args:
            name: Model name
            model: Model object
            version: Model version
            metadata: Additional metadata
        """
        from datetime import datetime
        
        model_key = f"{name}_v{version}"
        model_path = self.storage_path / f"{model_key}.pkl"
        
        # Save model
        if hasattr(model, 'save'):
            model.save(str(model_path))
        else:
            joblib.dump(model, str(model_path))
        
        # Update registry
        self.models[model_key] = {
            "name": name,
            "version": version,
            "path": str(model_path),
            "registered_at": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        
        self._save_registry()
    
    def get_model(self, name: str, version: Optional[str] = None) -> Any:
        """
        Get a model from the registry
        
        Args:
            name: Model name
            version: Model version (latest if not specified)
            
        Returns:
            Model object
        """
        if version:
            model_key = f"{name}_v{version}"
        else:
            # Get latest version
            matching_keys = [k for k in self.models.keys() if k.startswith(name)]
            if not matching_keys:
                raise ValueError(f"Model {name} not found")
            model_key = sorted(matching_keys)[-1]
        
        if model_key not in self.models:
            raise ValueError(f"Model {model_key} not found")
        
        model_info = self.models[model_key]
        model_path = model_info["path"]
        
        # Load based on model name
        if "confidence" in name.lower():
            model = ConfidenceScoreModel(model_path)
        elif "fraud" in name.lower():
            model = FraudDetectionModel(model_path)
        else:
            model = joblib.load(model_path)
        
        return model
    
    def list_models(self) -> List[Dict[str, Any]]:
        """
        List all registered models
        
        Returns:
            List of model information
        """
        return list(self.models.values())
    
    def delete_model(self, name: str, version: str):
        """Delete a model from the registry"""
        model_key = f"{name}_v{version}"
        
        if model_key in self.models:
            model_info = self.models[model_key]
            model_path = Path(model_info["path"])
            
            # Delete file
            if model_path.exists():
                model_path.unlink()
            
            # Remove from registry
            del self.models[model_key]
            self._save_registry()
