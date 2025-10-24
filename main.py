import os
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import uvicorn

from app.core.config import get_settings
from app.core.database import create_database_engine, get_database_url
from app.api.main import api_router
from app.agents.orchestrator import OrchestratorAgent
from app.core.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    settings = get_settings()
    setup_logging()
    
    # Initialize database
    engine = create_database_engine()
    
    # Initialize and start orchestrator
    orchestrator = OrchestratorAgent()
    
    # Start background tasks
    orchestrator_task = asyncio.create_task(orchestrator.start())
    
    app.state.orchestrator = orchestrator
    app.state.orchestrator_task = orchestrator_task
    
    yield
    
    # Shutdown
    orchestrator_task.cancel()
    try:
        await orchestrator_task
    except asyncio.CancelledError:
        pass


def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    settings = get_settings()
    
    app = FastAPI(
        title="TrueMesh Provider Intelligence",
        description="Automated healthcare provider data validation and provenance platform",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.environment != "production" else None,
        redoc_url="/redoc" if settings.environment != "production" else None,
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routes
    app.include_router(api_router, prefix="/api/v1")
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {"status": "healthy", "service": "TrueMesh Provider Intelligence"}
    
    return app


# Create the application instance
app = create_app()

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.environment == "development",
        log_level="info"
    )