"""
Model Lifecycle API Endpoints - ML model monitoring and management
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from datetime import datetime

from app.core.agent_base import AgentTask
from app.agents.model_lifecycle import ModelLifecycleAgent

router = APIRouter()


class ModelLifecycleRequest(BaseModel):
    """Model lifecycle management request"""
    action: str = Field(
        ...,
        description="Action: monitor, detect_drift, evaluate_performance, trigger_retrain, version_control, rollback"
    )
    model_name: str = Field(default="all", description="Model name or 'all'")
    parameters: dict = Field(default_factory=dict, description="Additional parameters")


class ModelLifecycleResponse(BaseModel):
    """Model lifecycle response"""
    action: str
    model_name: str
    result: dict
    timestamp: str


@router.post("/manage", response_model=ModelLifecycleResponse)
async def manage_model_lifecycle(request: ModelLifecycleRequest):
    """
    Manage ML model lifecycle
    
    **Actions:**
    - `monitor`: Monitor model performance and health
    - `detect_drift`: Detect data/concept drift
    - `evaluate_performance`: Comprehensive performance evaluation
    - `trigger_retrain`: Trigger model retraining
    - `version_control`: Manage model versions
    - `rollback`: Rollback to previous version
    
    **Model Names:**
    - `confidence_scoring`: Confidence scoring model
    - `fraud_detection`: Fraud detection model
    - `all`: All models
    """
    try:
        # Create agent instance
        agent = ModelLifecycleAgent()
        
        # Create task
        task = AgentTask(
            id=f"model-lifecycle-{datetime.utcnow().timestamp()}",
            task_type="model_lifecycle",
            priority=1,
            data={
                "action": request.action,
                "model_name": request.model_name,
                **request.parameters,
            }
        )
        
        # Process task
        result = await agent.process_task(task)
        
        if result.status.value == "failed":
            raise HTTPException(status_code=500, detail=result.error or "Model lifecycle action failed")
        
        return ModelLifecycleResponse(
            action=request.action,
            model_name=request.model_name,
            result=result.result,
            timestamp=datetime.utcnow().isoformat(),
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error managing model lifecycle: {str(e)}")


@router.get("/monitor")
async def monitor_models(
    model_name: str = Query("all", description="Model to monitor or 'all'"),
):
    """
    Monitor model performance and health
    
    Returns:
    - Model status (healthy, attention_needed, critical)
    - Performance metrics (accuracy, precision, recall, F1)
    - Inference time and error rate
    - Drift detection status
    - Recommendations
    """
    request = ModelLifecycleRequest(
        action="monitor",
        model_name=model_name,
    )
    
    return await manage_model_lifecycle(request)


@router.get("/drift")
async def detect_drift(
    model_name: str = Query("all", description="Model to check for drift"),
):
    """
    Detect data drift and concept drift
    
    Returns:
    - Data drift score and status
    - Concept drift score and status
    - Drifted features list
    - Feature-level drift scores
    - Recommendations (retraining, monitoring)
    """
    request = ModelLifecycleRequest(
        action="detect_drift",
        model_name=model_name,
    )
    
    return await manage_model_lifecycle(request)


@router.get("/performance")
async def evaluate_performance(
    model_name: str = Query("all", description="Model to evaluate"),
):
    """
    Comprehensive performance evaluation
    
    Returns:
    - Current metrics vs baseline
    - Performance delta
    - Trend (improving, stable, declining)
    - Evaluation period and sample size
    """
    request = ModelLifecycleRequest(
        action="evaluate_performance",
        model_name=model_name,
    )
    
    return await manage_model_lifecycle(request)


@router.post("/retrain")
async def trigger_retraining(
    model_name: str,
    reason: str = "performance_degradation",
    training_period: str = "last_90_days",
    notify_email: Optional[str] = None,
):
    """
    Trigger model retraining
    
    Starts a retraining job with specified parameters
    
    **Parameters:**
    - `model_name`: Model to retrain
    - `reason`: Reason for retraining
    - `training_period`: Period for training data
    - `notify_email`: Email for notifications
    
    **Returns:**
    - Training job ID
    - Estimated completion time
    - Training stages and status
    """
    request = ModelLifecycleRequest(
        action="trigger_retrain",
        model_name=model_name,
        parameters={
            "reason": reason,
            "training_period": training_period,
            "notify_email": notify_email,
        }
    )
    
    return await manage_model_lifecycle(request)


@router.get("/versions")
async def list_versions(
    model_name: str = Query(..., description="Model name"),
):
    """
    List model versions
    
    Returns version history with:
    - Version number
    - Status (production, archived)
    - Deployment timestamp
    - Performance metrics
    - Training sample size
    """
    request = ModelLifecycleRequest(
        action="version_control",
        model_name=model_name,
        parameters={"version_action": "list"}
    )
    
    return await manage_model_lifecycle(request)


@router.post("/versions/compare")
async def compare_versions(
    model_name: str,
    version1: str,
    version2: str,
):
    """
    Compare two model versions
    
    Returns side-by-side comparison of:
    - Performance metrics
    - Training parameters
    - Sample sizes
    - Deployment dates
    """
    request = ModelLifecycleRequest(
        action="version_control",
        model_name=model_name,
        parameters={
            "version_action": "compare",
            "version1": version1,
            "version2": version2,
        }
    )
    
    return await manage_model_lifecycle(request)


@router.post("/rollback")
async def rollback_model(
    model_name: str,
    target_version: str,
    reason: str = "performance_issue",
):
    """
    Rollback model to previous version
    
    Initiates rollback process with:
    - Validation checks
    - Gradual traffic diversion (canary)
    - Model swap
    - Verification
    
    **Returns:**
    - Rollback job ID
    - Estimated completion time
    - Rollback stages and status
    - Monitoring plan
    """
    request = ModelLifecycleRequest(
        action="rollback",
        model_name=model_name,
        parameters={
            "target_version": target_version,
            "reason": reason,
        }
    )
    
    return await manage_model_lifecycle(request)


@router.post("/ab-test")
async def start_ab_test(
    model_a: str,
    model_b: str,
    duration_hours: int = 48,
    sample_size: int = 5000,
):
    """
    Start A/B test between two model versions
    
    Compares two models with split traffic
    
    **Parameters:**
    - `model_a`: First model version
    - `model_b`: Second model version
    - `duration_hours`: Test duration
    - `sample_size`: Target sample size
    
    **Returns:**
    - Test ID
    - Traffic split configuration
    - Metrics to compare
    - Status and timeline
    """
    try:
        agent = ModelLifecycleAgent()
        
        ab_test = await agent.run_ab_test(
            model_a,
            model_b,
            {"duration_hours": duration_hours, "sample_size": sample_size}
        )
        
        return ab_test
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting A/B test: {str(e)}")


@router.get("/stats")
async def get_model_stats():
    """
    Get model lifecycle statistics
    
    Returns aggregated stats about all models
    """
    # In production, would query database for actual stats
    return {
        "models_tracked": 2,
        "total_versions": 7,
        "active_deployments": 2,
        "retraining_jobs_total": 12,
        "retraining_jobs_pending": 1,
        "rollbacks_total": 3,
        "ab_tests_total": 5,
        "ab_tests_active": 0,
        "average_model_uptime_days": 42.3,
        "last_updated": datetime.utcnow().isoformat(),
    }
