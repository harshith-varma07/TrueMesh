"""
Core utilities and base classes for TrueMesh Provider Intelligence

This module contains fundamental components:
- config: Application configuration and settings
- database: Database connection and session management
- logging: Structured logging utilities
- agent_base: Base classes for agent framework
"""

from app.core.config import get_settings, Settings
from app.core.database import (
    Base,
    engine,
    async_engine,
    get_db,
    get_async_db,
    create_database_engine,
    create_async_database_engine,
)
from app.core.logging import get_logger, setup_logging
from app.core.agent_base import (
    BaseAgent,
    AgentTask,
    AgentResult,
    AgentStatus,
    TaskPriority,
    agent_registry,
)

__all__ = [
    # Configuration
    "get_settings",
    "Settings",
    # Database
    "Base",
    "engine",
    "async_engine",
    "get_db",
    "get_async_db",
    "create_database_engine",
    "create_async_database_engine",
    # Logging
    "get_logger",
    "setup_logging",
    # Agent Framework
    "BaseAgent",
    "AgentTask",
    "AgentResult",
    "AgentStatus",
    "TaskPriority",
    "agent_registry",
]
