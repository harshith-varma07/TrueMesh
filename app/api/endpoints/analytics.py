"""
Analytics API Endpoints - Dashboard metrics, reports, and visualizations
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from datetime import datetime

from app.core.agent_base import AgentTask, agent_registry
from app.agents.analytics_insights import AnalyticsInsightsAgent

router = APIRouter()


class AnalyticsRequest(BaseModel):
    """Analytics generation request"""
    analytics_type: str = Field(
        default="overview",
        description="Type of analytics: overview, geospatial, trends, confidence_distribution, anomaly_report"
    )
    filters: dict = Field(default_factory=dict, description="Filters to apply")
    export_format: str = Field(default="json", description="Export format: json, csv, pdf")


class AnalyticsResponse(BaseModel):
    """Analytics response"""
    analytics_type: str
    data: dict
    generated_at: str
    export_format: str


@router.post("/generate", response_model=AnalyticsResponse)
async def generate_analytics(request: AnalyticsRequest):
    """
    Generate analytics based on specified type
    
    **Analytics Types:**
    - `overview`: System overview with summary metrics
    - `geospatial`: Regional distribution and maps
    - `trends`: Historical trends and patterns
    - `confidence_distribution`: Confidence score distribution
    - `anomaly_report`: Fraud and anomaly reports
    
    **Export Formats:**
    - `json`: JSON response (default)
    - `csv`: CSV file
    - `pdf`: PDF report
    """
    try:
        # Create agent instance
        agent = AnalyticsInsightsAgent()
        
        # Create task
        task = AgentTask(
            id=f"analytics-{datetime.utcnow().timestamp()}",
            task_type="analytics",
            priority=1,
            data={
                "analytics_type": request.analytics_type,
                "filters": request.filters,
                "export_format": request.export_format,
            }
        )
        
        # Process task
        result = await agent.process_task(task)
        
        if result.status.value == "failed":
            raise HTTPException(status_code=500, detail=result.error or "Analytics generation failed")
        
        return AnalyticsResponse(
            analytics_type=request.analytics_type,
            data=result.result.get("data", {}),
            generated_at=result.result.get("generated_at", datetime.utcnow().isoformat()),
            export_format=request.export_format,
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating analytics: {str(e)}")


@router.get("/overview")
async def get_overview(
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
):
    """
    Get system overview dashboard metrics
    
    Returns summary metrics including:
    - Total providers and verification stats
    - Confidence metrics
    - Fraud detection metrics
    - Data quality metrics
    - Regional distribution
    - Blockchain metrics
    - Performance metrics
    """
    filters = {}
    if start_date:
        filters["start_date"] = start_date
    if end_date:
        filters["end_date"] = end_date
    
    request = AnalyticsRequest(
        analytics_type="overview",
        filters=filters,
        export_format="json"
    )
    
    return await generate_analytics(request)


@router.get("/geospatial")
async def get_geospatial(
    state: Optional[str] = Query(None, description="Filter by state"),
    metric: Optional[str] = Query("provider_count", description="Metric to visualize"),
):
    """
    Get geospatial analysis with maps and regional data
    
    Returns:
    - Regional provider distribution
    - Heatmap data
    - City clusters with coordinates
    - State-level metrics
    """
    filters = {}
    if state:
        filters["state"] = state
    if metric:
        filters["metric"] = metric
    
    request = AnalyticsRequest(
        analytics_type="geospatial",
        filters=filters,
        export_format="json"
    )
    
    return await generate_analytics(request)


@router.get("/trends")
async def get_trends(
    days: int = Query(30, description="Number of days for trend analysis"),
):
    """
    Get trend analysis and historical patterns
    
    Returns:
    - Time series data (last N days)
    - Data quality index (AQI-style)
    - Growth metrics
    - Seasonal patterns
    """
    request = AnalyticsRequest(
        analytics_type="trends",
        filters={"days": days},
        export_format="json"
    )
    
    return await generate_analytics(request)


@router.get("/confidence-distribution")
async def get_confidence_distribution(
    provider_type: Optional[str] = Query(None, description="Filter by provider type"),
):
    """
    Get confidence score distribution analysis
    
    Returns:
    - Histogram of confidence scores
    - Statistical measures (mean, median, std dev)
    - Distribution by provider type
    - Distribution by region
    """
    filters = {}
    if provider_type:
        filters["provider_type"] = provider_type
    
    request = AnalyticsRequest(
        analytics_type="confidence_distribution",
        filters=filters,
        export_format="json"
    )
    
    return await generate_analytics(request)


@router.get("/anomaly-report")
async def get_anomaly_report(
    risk_level: Optional[str] = Query(None, description="Filter by risk level: critical, high, medium, low"),
):
    """
    Get comprehensive anomaly and fraud detection report
    
    Returns:
    - Anomaly summary by risk level
    - Anomaly types breakdown
    - Recent alerts
    - Resolution statistics
    - Impact analysis
    """
    filters = {}
    if risk_level:
        filters["risk_level"] = risk_level
    
    request = AnalyticsRequest(
        analytics_type="anomaly_report",
        filters=filters,
        export_format="json"
    )
    
    return await generate_analytics(request)


@router.get("/data-quality-index")
async def get_data_quality_index(
    provider_id: Optional[str] = Query(None, description="Calculate for specific provider"),
):
    """
    Calculate AQI-style data quality index
    
    Returns index (0-100) based on:
    - Completeness (30%)
    - Accuracy (25%)
    - Consistency (20%)
    - Timeliness (15%)
    - Uniqueness (10%)
    """
    try:
        agent = AnalyticsInsightsAgent()
        
        # For now, return simulated data quality index
        index = await agent.calculate_data_quality_index({})
        
        return {
            "data_quality_index": index,
            "breakdown": {
                "completeness": 85.0,
                "accuracy": 78.0,
                "consistency": 92.0,
                "timeliness": 67.0,
                "uniqueness": 95.0,
            },
            "grade": "Good" if index >= 80 else "Fair" if index >= 60 else "Poor",
            "calculated_at": datetime.utcnow().isoformat(),
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating data quality index: {str(e)}")


@router.get("/export/{analytics_type}")
async def export_analytics(
    analytics_type: str,
    format: str = Query("json", description="Export format: json, csv, pdf"),
):
    """
    Export analytics in specified format
    
    Supported formats:
    - json: JSON format
    - csv: CSV file
    - pdf: PDF report
    """
    request = AnalyticsRequest(
        analytics_type=analytics_type,
        filters={},
        export_format=format
    )
    
    result = await generate_analytics(request)
    
    return {
        "export_type": format,
        "analytics_type": analytics_type,
        "data": result.data,
        "exported_at": datetime.utcnow().isoformat(),
    }
