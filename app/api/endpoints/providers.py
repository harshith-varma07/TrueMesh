"""
Provider API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

from app.core.agent_base import agent_registry, TaskPriority
from app.agents.orchestrator import WorkflowType

router = APIRouter()


# Request/Response Models
class ProviderCreate(BaseModel):
    """Provider creation request"""
    registration_number: str = Field(..., min_length=6)
    name: str = Field(..., min_length=3)
    provider_type: str = Field(..., description="doctor, hospital, clinic, pharmacy")
    specialization: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: str = "India"


class ProviderUpdate(BaseModel):
    """Provider update request"""
    name: Optional[str] = None
    specialization: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None


class ProviderResponse(BaseModel):
    """Provider response"""
    id: str
    registration_number: str
    name: str
    provider_type: str
    status: str
    created_at: str
    updated_at: str


class WorkflowResponse(BaseModel):
    """Workflow execution response"""
    workflow_id: str
    workflow_type: str
    status: str
    message: str


@router.post("/", response_model=WorkflowResponse)
async def create_provider(provider: ProviderCreate):
    """
    Create a new healthcare provider and initiate verification workflow
    """
    try:
        # Get orchestrator agent
        agents = agent_registry.get_agents_by_type("orchestrator")
        if not agents:
            orchestrator = agent_registry.create_agent("orchestrator")
        else:
            orchestrator = agents[0]
        
        # Prepare provider data
        provider_data = provider.dict()
        provider_data["id"] = str(uuid.uuid4())
        provider_data["created_at"] = datetime.utcnow().isoformat()
        provider_data["updated_at"] = datetime.utcnow().isoformat()
        provider_data["status"] = "pending"
        
        # Submit to orchestrator workflow
        task_id = await orchestrator.submit_task(
            workflow_type=WorkflowType.PROVIDER_REGISTRATION.value,
            provider_data=provider_data,
            priority=TaskPriority.HIGH
        )
        
        return WorkflowResponse(
            workflow_id=task_id,
            workflow_type=WorkflowType.PROVIDER_REGISTRATION.value,
            status="submitted",
            message="Provider registration workflow initiated"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create provider: {str(e)}")


@router.get("/{provider_id}", response_model=ProviderResponse)
async def get_provider(provider_id: str):
    """
    Get provider details by ID
    
    Note: In production, this would query the database.
    For now, returns a mock response.
    """
    # TODO: Implement database query
    return ProviderResponse(
        id=provider_id,
        registration_number="REG123456",
        name="Dr. Sample Provider",
        provider_type="doctor",
        status="verified",
        created_at=datetime.utcnow().isoformat(),
        updated_at=datetime.utcnow().isoformat()
    )


@router.put("/{provider_id}", response_model=WorkflowResponse)
async def update_provider(provider_id: str, updates: ProviderUpdate):
    """
    Update provider information and trigger re-verification
    """
    try:
        # Get orchestrator agent
        agents = agent_registry.get_agents_by_type("orchestrator")
        if not agents:
            orchestrator = agent_registry.create_agent("orchestrator")
        else:
            orchestrator = agents[0]
        
        # Prepare update data
        provider_data = {
            "id": provider_id,
            **updates.dict(exclude_unset=True),
            "updated_at": datetime.utcnow().isoformat(),
        }
        
        # Submit to orchestrator workflow
        task_id = await orchestrator.submit_task(
            workflow_type=WorkflowType.PROVIDER_UPDATE.value,
            provider_data=provider_data,
            priority=TaskPriority.MEDIUM
        )
        
        return WorkflowResponse(
            workflow_id=task_id,
            workflow_type=WorkflowType.PROVIDER_UPDATE.value,
            status="submitted",
            message="Provider update workflow initiated"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update provider: {str(e)}")


@router.get("/")
async def list_providers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    provider_type: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
):
    """
    List providers with optional filters
    
    Note: In production, this would query the database.
    For now, returns mock data.
    """
    # TODO: Implement database query with filters
    mock_providers = [
        ProviderResponse(
            id=str(uuid.uuid4()),
            registration_number=f"REG{i:06d}",
            name=f"Provider {i}",
            provider_type="doctor",
            status="verified",
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat()
        )
        for i in range(1, min(limit, 10) + 1)
    ]
    
    return {
        "total": len(mock_providers),
        "skip": skip,
        "limit": limit,
        "providers": mock_providers
    }


@router.delete("/{provider_id}")
async def delete_provider(provider_id: str):
    """
    Delete a provider (soft delete)
    
    Note: In production, this would update the database.
    """
    # TODO: Implement database update
    return {
        "provider_id": provider_id,
        "status": "deleted",
        "message": "Provider has been deleted"
    }


@router.get("/{provider_id}/history")
async def get_provider_history(provider_id: str):
    """
    Get complete provenance history for a provider
    """
    try:
        # Get provenance ledger agent
        agents = agent_registry.get_agents_by_type("provenance_ledger")
        if not agents:
            provenance_agent = agent_registry.create_agent("provenance_ledger")
        else:
            provenance_agent = agents[0]
        
        # Get provider history from blockchain
        history = provenance_agent.get_provider_history(provider_id)
        
        return {
            "provider_id": provider_id,
            "history_count": len(history),
            "history": history,
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve history: {str(e)}")


@router.post("/{provider_id}/verify", response_model=WorkflowResponse)
async def verify_provider(provider_id: str):
    """
    Trigger provider verification workflow
    """
    try:
        # Get orchestrator agent
        agents = agent_registry.get_agents_by_type("orchestrator")
        if not agents:
            orchestrator = agent_registry.create_agent("orchestrator")
        else:
            orchestrator = agents[0]
        
        # Submit verification workflow
        task_id = await orchestrator.submit_task(
            workflow_type=WorkflowType.PROVIDER_VERIFICATION.value,
            provider_data={"id": provider_id},
            priority=TaskPriority.HIGH
        )
        
        return WorkflowResponse(
            workflow_id=task_id,
            workflow_type=WorkflowType.PROVIDER_VERIFICATION.value,
            status="submitted",
            message="Provider verification workflow initiated"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to verify provider: {str(e)}")


@router.get("/{provider_id}/scores")
async def get_provider_scores(provider_id: str):
    """
    Get confidence and fraud scores for a provider
    
    Note: In production, this would query the database.
    """
    # TODO: Implement database query
    return {
        "provider_id": provider_id,
        "confidence_scores": {
            "overall_score": 0.85,
            "verification_score": 0.9,
            "consistency_score": 0.8,
            "historical_score": 0.85,
            "external_score": 0.85,
        },
        "fraud_score": 0.15,
        "risk_level": "low",
        "last_updated": datetime.utcnow().isoformat(),
    }
