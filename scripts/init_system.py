#!/usr/bin/env python
"""
Complete initialization script for TrueMesh Provider Intelligence
Runs all initialization steps in order
"""
import os
import sys
import subprocess
from pathlib import Path

from app.core.logging import setup_logging, get_logger

setup_logging()
logger = get_logger("init_system")


def run_script(script_name: str, description: str) -> bool:
    """Run a Python script"""
    try:
        logger.info(f"Running {description}...")
        script_path = Path(__file__).parent / script_name
        
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logger.info(f"✓ {description} completed")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            logger.error(f"✗ {description} failed")
            if result.stderr:
                print(result.stderr, file=sys.stderr)
            return False
            
    except Exception as e:
        logger.error(f"Failed to run {description}: {str(e)}")
        return False


def main():
    """Run all initialization steps"""
    logger.info("=" * 60)
    logger.info("TrueMesh Provider Intelligence - System Initialization")
    logger.info("=" * 60)
    
    steps = [
        ("init_db.py", "Database Initialization"),
        ("init_models.py", "ML Models Initialization"),
    ]
    
    for script, description in steps:
        if not run_script(script, description):
            logger.error(f"Initialization failed at step: {description}")
            return False
    
    logger.info("=" * 60)
    logger.info("✓ System initialization completed successfully!")
    logger.info("=" * 60)
    logger.info("")
    logger.info("Next steps:")
    logger.info("  1. Review your .env file configuration")
    logger.info("  2. Start the application: python main.py")
    logger.info("  3. Access the API at: http://localhost:8000/docs")
    logger.info("")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
