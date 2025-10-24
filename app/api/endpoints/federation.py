"""
Federation API endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime

from app.core.agent_base import agent_registry

router = APIRouter()


class SyncRequest(BaseModel):
    """Federation sync request"""
    provider_data: Dict[str, Any]
    operation: str = "update"


@router.post("/sync")
async def sync_to_federation(request: SyncRequest):
    """
    Sync provider data to federation network
    """
    try:
        # Get federated publisher agent
        agents = agent_registry.get_agents_by_type("federated_publisher")
        if not agents:
            publisher_agent = agent_registry.create_agent("federated_publisher")
        else:
            publisher_agent = agents[0]
        
        # Publish to federation
        result = await publisher_agent.publish_to_federation(
            request.provider_data,
            request.operation
        )
        
        return {
            "status": "synced",
            "operation": request.operation,
            "publish_results": result,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Federation sync error: {str(e)}")


@router.get("/status")
async def get_federation_status():
    """
    Get federation network status
    """
    try:
        # Get federated publisher agent
        agents = agent_registry.get_agents_by_type("federated_publisher")
        if not agents:
            return {
                "status": "not_initialized",
                "message": "Federation not initialized"
            }
        
        publisher_agent = agents[0]
        
        # Get federation status
        status = publisher_agent.get_federation_status()
        
        return status
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status error: {str(e)}")


@router.post("/health-check")
async def check_federation_health():
    """
    Check health of all federation nodes
    """
    try:
        # Get federated publisher agent
        agents = agent_registry.get_agents_by_type("federated_publisher")
        if not agents:
            return {
                "healthy_nodes": 0,
                "total_nodes": 0,
                "message": "Federation not initialized"
            }
        
        publisher_agent = agents[0]
        
        # Check health
        health = await publisher_agent.health_check_federation()
        
        return health
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check error: {str(e)}")


@router.get("/updates")
async def get_federation_updates(since: str = None):
    """
    Get updates from federation network
    """
    try:
        # Get federated publisher agent
        agents = agent_registry.get_agents_by_type("federated_publisher")
        if not agents:
            return {
                "synced_updates": [],
                "message": "Federation not initialized"
            }
        
        publisher_agent = agents[0]
        
        # Sync from federation
        result = await publisher_agent.sync_from_federation()
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync error: {str(e)}")
