"""
Logging configuration for TrueMesh Provider Intelligence
"""
import logging
import sys
from typing import Any, Dict
import structlog
from rich.logging import RichHandler
from rich.console import Console

from app.core.config import get_settings


def setup_logging() -> None:
    """Setup structured logging with Rich console output"""
    settings = get_settings()
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if settings.log_format == "json" else structlog.dev.ConsoleRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard logging
    handlers = []
    
    if settings.environment == "development":
        # Rich handler for development
        console = Console()
        rich_handler = RichHandler(
            console=console,
            rich_tracebacks=True,
            tracebacks_show_locals=True
        )
        rich_handler.setFormatter(
            logging.Formatter("%(message)s")
        )
        handlers.append(rich_handler)
    else:
        # Standard handler for production
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        handlers.append(handler)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        handlers=handlers,
        force=True
    )
    
    # Configure specific loggers
    logging.getLogger("uvicorn.access").disabled = True
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a configured structlog logger"""
    return structlog.get_logger(name)