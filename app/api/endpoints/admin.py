"""
Admin API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.core.agent_base import agent_registry

router = APIRouter()


class ExceptionRequest(BaseModel):
    """Compliance exception request"""
    provider_id: str
    policy_type: str
    reason: str
    duration_days: int = 30


@router.get("/agents/status")
async def get_agents_status():
    """
    Get status of all agents in the system
    """
    try:
        status = agent_registry.get_agent_status_summary()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving agent status: {str(e)}")


@router.get("/orchestrator/status")
async def get_orchestrator_status():
    """
    Get orchestrator agent status
    """
    try:
        agents = agent_registry.get_agents_by_type("orchestrator")
        if not agents:
            return {"status": "not_initialized"}
        
        orchestrator = agents[0]
        return orchestrator.get_workflow_status()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving orchestrator status: {str(e)}")


@router.get("/provenance/chain-info")
async def get_blockchain_info():
    """
    Get provenance blockchain information
    """
    try:
        agents = agent_registry.get_agents_by_type("provenance_ledger")
        if not agents:
            provenance_agent = agent_registry.create_agent("provenance_ledger")
        else:
            provenance_agent = agents[0]
        
        chain_info = provenance_agent.get_chain_info()
        return chain_info
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving chain info: {str(e)}")


@router.post("/provenance/verify")
async def verify_provenance_record(block_hash: str, data_hash: str):
    """
    Verify a provenance record
    """
    try:
        agents = agent_registry.get_agents_by_type("provenance_ledger")
        if not agents:
            raise HTTPException(status_code=404, detail="Provenance agent not found")
        
        provenance_agent = agents[0]
        
        is_valid = provenance_agent.verify_record(block_hash, data_hash)
        
        return {
            "block_hash": block_hash,
            "data_hash": data_hash,
            "is_valid": is_valid,
            "verified_at": datetime.utcnow().isoformat(),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification error: {str(e)}")


@router.post("/compliance/exception")
async def grant_compliance_exception(request: ExceptionRequest):
    """
    Grant a compliance exception for a provider
    """
    try:
        agents = agent_registry.get_agents_by_type("compliance_manager")
        if not agents:
            compliance_agent = agent_registry.create_agent("compliance_manager")
        else:
            compliance_agent = agents[0]
        
        exception = compliance_agent.grant_exception(
            provider_id=request.provider_id,
            policy_type=request.policy_type,
            reason=request.reason,
            duration_days=request.duration_days
        )
        
        return exception
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error granting exception: {str(e)}")


@router.get("/compliance/exceptions")
async def list_compliance_exceptions(provider_id: Optional[str] = None):
    """
    List active compliance exceptions
    """
    try:
        agents = agent_registry.get_agents_by_type("compliance_manager")
        if not agents:
            return {"exceptions": [], "count": 0}
        
        compliance_agent = agents[0]
        
        exceptions = compliance_agent.get_active_exceptions(provider_id)
        
        return {
            "exceptions": exceptions,
            "count": len(exceptions),
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing exceptions: {str(e)}")


@router.get("/stats/overview")
async def get_system_overview():
    """
    Get system statistics overview
    """
    try:
        agent_status = agent_registry.get_agent_status_summary()
        
        # Get provenance chain info
        provenance_agents = agent_registry.get_agents_by_type("provenance_ledger")
        chain_info = {}
        if provenance_agents:
            chain_info = provenance_agents[0].get_chain_info()
        
        # Get federation status
        federation_agents = agent_registry.get_agents_by_type("federated_publisher")
        federation_status = {}
        if federation_agents:
            federation_status = federation_agents[0].get_federation_status()
        
        return {
            "agents": agent_status,
            "provenance_chain": chain_info,
            "federation": federation_status,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving overview: {str(e)}")


@router.get("/health")
async def admin_health_check():
    """
    Admin health check endpoint
    """
    return {
        "status": "healthy",
        "service": "TrueMesh Admin API",
        "timestamp": datetime.utcnow().isoformat(),
    }
