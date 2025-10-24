#!/usr/bin/env python
"""
Initialize ML models for TrueMesh Provider Intelligence
"""
import os
import sys
from pathlib import Path

from app.core.config import get_settings
from app.agents.confidence_scoring import ConfidenceScoringAgent
from app.agents.fraud_detection import FraudDetectionAgent
from app.core.logging import setup_logging, get_logger

setup_logging()
logger = get_logger("init_models")


def init_models():
    """Initialize ML models"""
    try:
        settings = get_settings()
        
        # Create model storage directory
        model_dir = Path(settings.model_storage_path)
        model_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Initializing ML models in {model_dir}")
        
        # Initialize Confidence Scoring Agent (triggers model creation)
        logger.info("Initializing Confidence Scoring Model...")
        confidence_agent = ConfidenceScoringAgent()
        logger.info("✓ Confidence Scoring Model initialized")
        
        # Initialize Fraud Detection Agent (triggers model creation)
        logger.info("Initializing Fraud Detection Model...")
        fraud_agent = FraudDetectionAgent()
        logger.info("✓ Fraud Detection Model initialized")
        
        logger.info("✓ All ML models initialized successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize models: {str(e)}")
        return False


if __name__ == "__main__":
    success = init_models()
    sys.exit(0 if success else 1)
