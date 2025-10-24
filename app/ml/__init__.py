"""
Machine Learning module initialization

This module will contain ML models and utilities for 
confidence scoring and fraud detection.

Status: Placeholder - To be implemented

Current implementation is embedded in:
- app/agents/confidence_scoring.py (ConfidenceScoringAgent)
- app/agents/fraud_detection.py (FraudDetectionAgent)

Future components:
- models.py: ML model classes (ConfidenceScoreModel, FraudDetectionModel)
- features.py: Feature extraction and engineering
- training.py: Training pipelines and utilities
- evaluation.py: Model evaluation metrics
- preprocessing.py: Data preprocessing utilities
- utils.py: Common ML utilities
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
