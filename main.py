import os
import sys
import logging
from pathlib import Path

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import asyncio
import uvicorn

from app.core.config import get_settings
from app.core.database import get_engine
from app.api.main import api_router
from app.agents.orchestrator import OrchestratorAgent
from app.agents.registry import register_all_agents
from app.core.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    settings = get_settings()
    setup_logging()
    
    # Register all agent types
    register_all_agents()
    
    # Initialize database only if DATABASE_URL is properly configured
    # Database will be lazy-loaded when first accessed
    if settings.environment == "production":
        # In production, ensure database is available at startup
        try:
            _ = get_engine()
        except Exception as e:
            logging.warning(f"Database not available at startup: {e}")
    
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
    
    # Mount static files for frontend
    frontend_path = Path(__file__).parent / "frontend"
    if frontend_path.exists():
        # Mount CSS, JS, and other assets at /css, /js, etc.
        css_path = frontend_path / "css"
        js_path = frontend_path / "js"
        
        if css_path.exists():
            app.mount("/css", StaticFiles(directory=str(css_path)), name="css")
        if js_path.exists():
            app.mount("/js", StaticFiles(directory=str(js_path)), name="js")
        
        # Serve index.html at root
        @app.get("/")
        async def read_root():
            """Serve the main frontend page"""
            index_path = frontend_path / "index.html"
            if index_path.exists():
                return FileResponse(str(index_path))
            return {"message": "TrueMesh Provider Intelligence API", "docs": "/docs"}
        
        # Serve other HTML pages
        @app.get("/{page}.html")
        async def read_page(page: str):
            """Serve frontend HTML pages"""
            # List of allowed page names
            allowed_pages = ["dashboard", "providers", "verification", "login", "about", "profile", "register"]
            
            # Validate page parameter to prevent path traversal attacks
            # Check for path traversal characters first
            if ".." in page or "/" in page or "\\" in page:
                raise HTTPException(status_code=404, detail="Invalid page name")
            
            # Ensure page is either alphanumeric or in allowed list
            if not (page.isalnum() or page in allowed_pages):
                raise HTTPException(status_code=404, detail="Page not found")
            
            page_path = frontend_path / f"{page}.html"
            if page_path.exists() and page_path.parent == frontend_path:
                return FileResponse(str(page_path))
            raise HTTPException(status_code=404, detail="Page not found")
    
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