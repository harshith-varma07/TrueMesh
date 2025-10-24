"""
TrueMesh Provider Intelligence - Main Application Package

A fully automated Python-based healthcare provider data validation 
and provenance platform for Indian payers and TPAs.
"""

__version__ = "1.0.0"
__author__ = "TrueMesh Team"
__description__ = "Provider Intelligence and Trust Loop System"

# Import key components for easier access
from app.core.config import get_settings
from app.core.database import Base, get_db, get_async_db
from app.core.logging import get_logger, setup_logging

__all__ = [
    "__version__",
    "get_settings",
    "Base",
    "get_db",
    "get_async_db",
    "get_logger",
    "setup_logging",
]
