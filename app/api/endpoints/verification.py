"""
Verification API endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

from app.core.agent_base import agent_registry, AgentTask, TaskPriority

router = APIRouter()


class VerificationRequest(BaseModel):
    """Verification request"""
    provider_id: str
    verification_type: str = "full"  # full, quick, compliance


class VerificationResponse(BaseModel):
    """Verification response"""
    provider_id: str
    status: str
    is_verified: bool
    confidence_score: float
    verification_results: Dict[str, Any]
    timestamp: str


@router.post("/", response_model=VerificationResponse)
async def verify_provider_data(request: VerificationRequest):
    """
    Verify provider data against multiple sources
    """
    try:
        # Get data verification agent
        agents = agent_registry.get_agents_by_type("data_verification")
        if not agents:
            verification_agent = agent_registry.create_agent("data_verification")
        else:
            verification_agent = agents[0]
        
        # Create verification task
        task = AgentTask(
            agent_type="data_verification",
            priority=TaskPriority.HIGH,
            data={
                "id": request.provider_id,
                "registration_number": request.provider_id,  # Mock
                "provider_type": "doctor",  # Mock
            }
        )
        
        # Execute verification
        result = await verification_agent.execute_task(task)
        
        if result.status.value == "completed":
            return VerificationResponse(
                provider_id=request.provider_id,
                status="verified",
                is_verified=result.result.get("is_verified", False),
                confidence_score=result.result.get("confidence_score", 0.0),
                verification_results=result.result.get("verification_results", {}),
                timestamp=datetime.utcnow().isoformat()
            )
        else:
            raise HTTPException(status_code=500, detail="Verification failed")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification error: {str(e)}")


@router.get("/{provider_id}/status")
async def get_verification_status(provider_id: str):
    """
    Get current verification status for a provider
    """
    # TODO: Query database for verification records
    return {
        "provider_id": provider_id,
        "verification_status": "verified",
        "last_verified": datetime.utcnow().isoformat(),
        "next_verification_due": "2025-10-24T00:00:00",
        "verification_sources": ["mci_registry", "insurance_registry"],
    }


@router.post("/{provider_id}/fraud-check")
async def check_fraud(provider_id: str):
    """
    Run fraud detection check on provider
    """
    try:
        # Get fraud detection agent
        agents = agent_registry.get_agents_by_type("fraud_detection")
        if not agents:
            fraud_agent = agent_registry.create_agent("fraud_detection")
        else:
            fraud_agent = agents[0]
        
        # Create fraud check task
        task = AgentTask(
            agent_type="fraud_detection",
            priority=TaskPriority.HIGH,
            data={
                "id": provider_id,
                "registration_number": provider_id,
                "name": "Sample Provider",
                "provider_type": "doctor",
            }
        )
        
        # Execute fraud check
        result = await fraud_agent.execute_task(task)
        
        if result.status.value == "completed":
            return {
                "provider_id": provider_id,
                "fraud_score": result.result.get("fraud_score", 0.0),
                "risk_level": result.result.get("risk_level", "low"),
                "is_fraudulent": result.result.get("is_fraudulent", False),
                "fraud_checks": result.result.get("fraud_checks", {}),
                "checked_at": datetime.utcnow().isoformat(),
            }
        else:
            raise HTTPException(status_code=500, detail="Fraud check failed")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fraud check error: {str(e)}")


@router.post("/{provider_id}/confidence-score")
async def calculate_confidence_score(provider_id: str):
    """
    Calculate confidence score for provider
    """
    try:
        # Get confidence scoring agent
        agents = agent_registry.get_agents_by_type("confidence_scoring")
        if not agents:
            scoring_agent = agent_registry.create_agent("confidence_scoring")
        else:
            scoring_agent = agents[0]
        
        # Create scoring task
        task = AgentTask(
            agent_type="confidence_scoring",
            priority=TaskPriority.MEDIUM,
            data={
                "id": provider_id,
                "registration_number": provider_id,
                "name": "Sample Provider",
                "provider_type": "doctor",
                "verification_results": {
                    "mci_registry": {"status": "verified", "confidence": 0.9},
                    "insurance_registry": {"status": "verified", "confidence": 0.85},
                },
            }
        )
        
        # Execute scoring
        result = await scoring_agent.execute_task(task)
        
        if result.status.value == "completed":
            return {
                "provider_id": provider_id,
                "confidence_scores": result.result.get("confidence_scores", {}),
                "overall_score": result.result.get("overall_score", 0.0),
                "calculated_at": datetime.utcnow().isoformat(),
            }
        else:
            raise HTTPException(status_code=500, detail="Confidence scoring failed")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Confidence scoring error: {str(e)}")


@router.post("/{provider_id}/compliance-check")
async def check_compliance(provider_id: str):
    """
    Run compliance check on provider
    """
    try:
        # Get compliance manager agent
        agents = agent_registry.get_agents_by_type("compliance_manager")
        if not agents:
            compliance_agent = agent_registry.create_agent("compliance_manager")
        else:
            compliance_agent = agents[0]
        
        # Create compliance check task
        task = AgentTask(
            agent_type="compliance_manager",
            priority=TaskPriority.MEDIUM,
            data={
                "id": provider_id,
                "registration_number": provider_id,
                "name": "Sample Provider",
                "provider_type": "doctor",
                "city": "Mumbai",
                "state": "Maharashtra",
                "verified_at": datetime.utcnow().isoformat(),
                "confidence_scores": {"overall_score": 0.85, "consistency_score": 0.9},
                "fraud_score": 0.15,
            }
        )
        
        # Execute compliance check
        result = await compliance_agent.execute_task(task)
        
        if result.status.value == "completed":
            return {
                "provider_id": provider_id,
                "compliance_status": result.result.get("compliance_status", ""),
                "is_compliant": result.result.get("is_compliant", False),
                "violations": result.result.get("violations", []),
                "auto_resolved": result.result.get("auto_resolved", 0),
                "checked_at": datetime.utcnow().isoformat(),
            }
        else:
            raise HTTPException(status_code=500, detail="Compliance check failed")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Compliance check error: {str(e)}")
