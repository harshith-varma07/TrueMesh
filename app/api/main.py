"""
API Router Configuration
"""
from fastapi import APIRouter
from app.api.endpoints import providers, verification, admin, pitl, federation

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(providers.router, prefix="/providers", tags=["providers"])
api_router.include_router(verification.router, prefix="/verification", tags=["verification"])
api_router.include_router(pitl.router, prefix="/pitl", tags=["pitl"])
api_router.include_router(federation.router, prefix="/federation", tags=["federation"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
