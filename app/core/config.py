"""
Core configuration module for TrueMesh Provider Intelligence
"""
from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        protected_namespaces=('settings_',)  # Allow 'model_' prefix in field names
    )
    
    # Application
    app_name: str = "TrueMesh Provider Intelligence"
    environment: str = Field(default="development", alias="ENV")
    debug: bool = Field(default=True, alias="DEBUG")
    port: int = Field(default=8000, alias="PORT")
    
    # Security
    secret_key: str = Field(..., alias="SECRET_KEY")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:8000", "http://localhost:8080", "http://127.0.0.1:8000"]
    
    # Database
    database_url: str = Field(..., alias="DATABASE_URL")
    database_echo: bool = Field(default=False, alias="DATABASE_ECHO")
    
    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    
    # External APIs
    mci_registry_url: str = Field(default="https://api.mciindia.org", alias="MCI_REGISTRY_URL")
    insurance_registry_url: str = Field(default="https://api.irdai.gov.in", alias="INSURANCE_REGISTRY_URL")
    
    # ML Models
    model_storage_path: str = Field(default="./data/models", alias="MODEL_STORAGE_PATH")
    confidence_threshold: float = Field(default=0.7, alias="CONFIDENCE_THRESHOLD")
    fraud_threshold: float = Field(default=0.8, alias="FRAUD_THRESHOLD")
    
    # Blockchain/Provenance
    blockchain_network: str = Field(default="local", alias="BLOCKCHAIN_NETWORK")
    genesis_hash: str = Field(default="0000000000000000000000000000000000000000000000000000000000000000")
    
    # Agent Configuration
    max_concurrent_agents: int = Field(default=10, alias="MAX_CONCURRENT_AGENTS")
    agent_timeout_seconds: int = Field(default=300, alias="AGENT_TIMEOUT_SECONDS")
    
    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_format: str = Field(default="json", alias="LOG_FORMAT")
    
    # Federation
    federation_nodes: List[str] = Field(default=[], alias="FEDERATION_NODES")
    node_id: str = Field(default="node-1", alias="NODE_ID")
    
    @field_validator('federation_nodes', mode='before')
    @classmethod
    def parse_federation_nodes(cls, v):
        """Parse federation_nodes from environment variable"""
        if v is None or v == '':
            return []
        if isinstance(v, str):
            # Split by comma and strip whitespace
            return [node.strip() for node in v.split(',') if node.strip()]
        return v
    
    # Encryption
    encryption_key: str = Field(..., alias="ENCRYPTION_KEY")
    
    # Rate Limiting
    rate_limit_requests: int = Field(default=100, alias="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=3600, alias="RATE_LIMIT_WINDOW")  # seconds


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get application settings (singleton pattern)"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings