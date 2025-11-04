"""
API Router Configuration
"""
from fastapi import APIRouter
from app.api.endpoints import (
    providers,
    verification,
    admin,
    pitl,
    federation,
    analytics,
    entity_resolution,
    data_ingestion,
    model_lifecycle,
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(providers.router, prefix="/providers", tags=["providers"])
api_router.include_router(verification.router, prefix="/verification", tags=["verification"])
api_router.include_router(pitl.router, prefix="/pitl", tags=["pitl"])
api_router.include_router(federation.router, prefix="/federation", tags=["federation"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(entity_resolution.router, prefix="/entity-resolution", tags=["entity-resolution"])
api_router.include_router(data_ingestion.router, prefix="/data-ingestion", tags=["data-ingestion"])
api_router.include_router(model_lifecycle.router, prefix="/model-lifecycle", tags=["model-lifecycle"])
