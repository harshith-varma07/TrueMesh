"""
Machine Learning module for TrueMesh Provider Intelligence

Complete ML implementation for confidence scoring and fraud detection.

Components:
- models.py: Production-ready ML models
  * ConfidenceScoreModel: Random Forest classifier for trust assessment
  * FraudDetectionModel: Isolation Forest for anomaly detection
  * FeatureExtractor: Feature extraction utilities
  * ModelManager: Model versioning and lifecycle management

Features:
- Complete feature extraction from provider data
- Trained models with cross-validation
- Model persistence and versioning
- Detailed prediction with feature importance
- Risk level assessment
"""

from app.ml.models import (
    ConfidenceScoreModel,
    FraudDetectionModel,
    FeatureExtractor,
    ModelManager,
)

__all__ = [
    "ConfidenceScoreModel",
    "FraudDetectionModel",
    "FeatureExtractor",
    "ModelManager",
]
