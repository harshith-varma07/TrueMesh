"""
PITL (Provider-Initiated Trust Loop) API endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime

from app.core.agent_base import agent_registry, AgentTask, TaskPriority

router = APIRouter()


class UpdateRequest(BaseModel):
    """Provider update request"""
    provider_id: str
    updates: Dict[str, Any]


class ChallengeRequest(BaseModel):
    """Provider challenge request"""
    provider_id: str
    challenge_data: Dict[str, Any]
    challenge_reason: str = Field(..., min_length=10)


class ChallengeResponse(BaseModel):
    """Challenge response"""
    challenge_id: str
    status: str
    message: str


@router.post("/update")
async def submit_provider_update(request: UpdateRequest):
    """
    Submit provider-initiated update request
    """
    try:
        # Get PITL agent
        agents = agent_registry.get_agents_by_type("pitl")
        if not agents:
            pitl_agent = agent_registry.create_agent("pitl")
        else:
            pitl_agent = agents[0]
        
        # Create PITL task
        task = AgentTask(
            agent_type="pitl",
            priority=TaskPriority.HIGH,
            data={
                "id": request.provider_id,
                "pitl_operation": "update_request",
                "updates": request.updates,
            }
        )
        
        # Execute PITL operation
        result = await pitl_agent.execute_task(task)
        
        if result.status.value == "completed":
            return {
                "provider_id": request.provider_id,
                "status": result.result.get("status", "pending"),
                "message": "Update request processed",
                "updated_fields": result.result.get("updated_fields", []),
                "timestamp": datetime.utcnow().isoformat(),
            }
        else:
            raise HTTPException(status_code=500, detail="Update request failed")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Update error: {str(e)}")


@router.post("/challenge", response_model=ChallengeResponse)
async def submit_challenge(request: ChallengeRequest):
    """
    Submit provider challenge to existing data
    """
    try:
        # Get PITL agent
        agents = agent_registry.get_agents_by_type("pitl")
        if not agents:
            pitl_agent = agent_registry.create_agent("pitl")
        else:
            pitl_agent = agents[0]
        
        # Create challenge task
        task = AgentTask(
            agent_type="pitl",
            priority=TaskPriority.HIGH,
            data={
                "id": request.provider_id,
                "pitl_operation": "challenge",
                "challenge_data": request.challenge_data,
                "challenge_reason": request.challenge_reason,
            }
        )
        
        # Execute challenge
        result = await pitl_agent.execute_task(task)
        
        if result.status.value == "completed":
            return ChallengeResponse(
                challenge_id=result.result.get("challenge_id", ""),
                status=result.result.get("status", "pending"),
                message=result.result.get("next_steps", "Challenge submitted for review")
            )
        else:
            raise HTTPException(status_code=500, detail="Challenge submission failed")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Challenge error: {str(e)}")


@router.get("/challenges/{challenge_id}")
async def get_challenge_status(challenge_id: str):
    """
    Get status of a challenge
    """
    try:
        # Get PITL agent
        agents = agent_registry.get_agents_by_type("pitl")
        if not agents:
            raise HTTPException(status_code=404, detail="PITL agent not found")
        
        pitl_agent = agents[0]
        
        # Get challenge status
        challenge = pitl_agent.get_challenge_status(challenge_id)
        
        if challenge:
            return challenge
        else:
            raise HTTPException(status_code=404, detail="Challenge not found")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving challenge: {str(e)}")


@router.get("/challenges")
async def list_pending_challenges():
    """
    List all pending challenges
    """
    try:
        # Get PITL agent
        agents = agent_registry.get_agents_by_type("pitl")
        if not agents:
            return {"pending_count": 0, "challenges": []}
        
        pitl_agent = agents[0]
        
        # Get pending challenges
        result = pitl_agent.get_pending_challenges()
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing challenges: {str(e)}")


@router.post("/challenges/{challenge_id}/resolve")
async def resolve_challenge(challenge_id: str, resolution: str = "approve"):
    """
    Resolve a challenge (admin endpoint)
    """
    try:
        # Get PITL agent
        agents = agent_registry.get_agents_by_type("pitl")
        if not agents:
            raise HTTPException(status_code=404, detail="PITL agent not found")
        
        pitl_agent = agents[0]
        
        # Create resolution task
        task = AgentTask(
            agent_type="pitl",
            priority=TaskPriority.HIGH,
            data={
                "pitl_operation": "verify_challenge",
                "challenge_id": challenge_id,
                "resolution": resolution,
            }
        )
        
        # Execute resolution
        result = await pitl_agent.execute_task(task)
        
        if result.status.value == "completed":
            return result.result
        else:
            raise HTTPException(status_code=500, detail="Challenge resolution failed")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resolution error: {str(e)}")
