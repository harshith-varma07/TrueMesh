"""
API endpoints for TrueMesh Provider Intelligence

This module contains all API endpoint routers organized by domain:
- providers: Provider registration and management
- verification: Provider verification workflows
- pitl: Provider-Initiated Trust Loop
- federation: Data federation and synchronization
- admin: Administrative operations
"""

from app.api.endpoints import (
    providers,
    verification,
    pitl,
    federation,
    admin,
)

__all__ = [
    "providers",
    "verification",
    "pitl",
    "federation",
    "admin",
]
