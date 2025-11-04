"""
Data Ingestion API Endpoints - Multi-source data collection
"""
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from datetime import datetime

from app.core.agent_base import AgentTask
from app.agents.data_ingestion import DataIngestionAgent

router = APIRouter()


class IngestionRequest(BaseModel):
    """Data ingestion request"""
    source_type: str = Field(
        default="all",
        description="Source type: all, health_facilities, doctors, accreditation, business_entities"
    )
    filters: dict = Field(default_factory=dict, description="Filters to apply (state, city, etc.)")


class IngestionResponse(BaseModel):
    """Data ingestion response"""
    ingested_count: int
    by_source: dict
    ingestion_stats: dict
    ingested_at: str


class GeocodeRequest(BaseModel):
    """Geocoding request"""
    address: str = Field(..., description="Address to geocode")


@router.post("/ingest", response_model=IngestionResponse)
async def ingest_data(request: IngestionRequest):
    """
    Ingest data from multiple sources
    
    **Supported Sources:**
    - `health_facilities`: Hospital and clinic data (NHM/data.gov.in)
    - `doctors`: Doctor registration data (National Medical Commission)
    - `accreditation`: Facility accreditation (NABH/QCI)
    - `business_entities`: Corporate entity verification (MCA)
    - `all`: Ingest from all sources
    
    **Filters:**
    - `state`: Filter by state
    - `city`: Filter by city
    - `specialization`: Filter doctors by specialization
    
    **Process:**
    1. Pull raw data from specified sources
    2. Normalize to standard format
    3. Add timestamps for audit trail
    4. Store raw + normalized data
    
    **Returns:**
    - Count of ingested records by source
    - Normalized data ready for entity resolution
    - Ingestion statistics
    """
    try:
        # Create agent instance
        agent = DataIngestionAgent()
        
        # Create task
        task = AgentTask(
            id=f"ingestion-{datetime.utcnow().timestamp()}",
            task_type="data_ingestion",
            priority=1,
            data={
                "source_type": request.source_type,
                "filters": request.filters,
            }
        )
        
        # Process task
        result = await agent.process_task(task)
        
        if result.status.value == "failed":
            raise HTTPException(status_code=500, detail=result.error or "Data ingestion failed")
        
        return IngestionResponse(
            ingested_count=result.result.get("ingested_count", 0),
            by_source=result.result.get("by_source", {}),
            ingestion_stats=result.result.get("ingestion_stats", {}),
            ingested_at=result.result.get("ingested_at", datetime.utcnow().isoformat()),
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ingesting data: {str(e)}")


@router.get("/sources")
async def list_sources():
    """
    List available data sources
    
    Returns information about all configured data sources
    """
    return {
        "sources": [
            {
                "id": "health_facilities",
                "name": "Health Facility Directory",
                "provider": "NHM / data.gov.in",
                "description": "Hospital and clinic listings",
                "status": "active",
                "last_updated": "2025-11-01T10:00:00Z",
            },
            {
                "id": "doctors",
                "name": "Doctor Registry",
                "provider": "National Medical Commission",
                "description": "Registered medical practitioners",
                "status": "active",
                "last_updated": "2025-11-02T14:30:00Z",
            },
            {
                "id": "accreditation",
                "name": "Facility Accreditation",
                "provider": "NABH / Quality Council of India",
                "description": "Healthcare facility accreditation status",
                "status": "active",
                "last_updated": "2025-10-28T09:15:00Z",
            },
            {
                "id": "business_entities",
                "name": "Business Entity Registry",
                "provider": "Ministry of Corporate Affairs",
                "description": "Corporate entity verification",
                "status": "active",
                "last_updated": "2025-11-03T16:45:00Z",
            },
        ],
        "total_sources": 4,
    }


@router.get("/health-facilities")
async def get_health_facilities(
    state: Optional[str] = Query(None, description="Filter by state"),
    city: Optional[str] = Query(None, description="Filter by city"),
):
    """
    Get health facility data from NHM directory
    
    Returns hospital and clinic listings from public health facility directory
    """
    filters = {}
    if state:
        filters["state"] = state
    if city:
        filters["city"] = city
    
    request = IngestionRequest(
        source_type="health_facilities",
        filters=filters
    )
    
    return await ingest_data(request)


@router.get("/doctors")
async def get_doctors(
    state: Optional[str] = Query(None, description="Filter by state"),
    specialization: Optional[str] = Query(None, description="Filter by specialization"),
):
    """
    Get doctor data from National Medical Commission
    
    Returns registered doctor information from NMC public lookup
    """
    filters = {}
    if state:
        filters["state"] = state
    if specialization:
        filters["specialization"] = specialization
    
    request = IngestionRequest(
        source_type="doctors",
        filters=filters
    )
    
    return await ingest_data(request)


@router.get("/accreditation")
async def get_accreditation(
    state: Optional[str] = Query(None, description="Filter by state"),
):
    """
    Get accreditation data from NABH
    
    Returns facility accreditation status from NABH/QCI public portals
    """
    filters = {}
    if state:
        filters["state"] = state
    
    request = IngestionRequest(
        source_type="accreditation",
        filters=filters
    )
    
    return await ingest_data(request)


@router.get("/business-entities")
async def get_business_entities(
    state: Optional[str] = Query(None, description="Filter by state"),
):
    """
    Get business entity data from MCA
    
    Returns corporate entity information from Ministry of Corporate Affairs
    """
    filters = {}
    if state:
        filters["state"] = state
    
    request = IngestionRequest(
        source_type="business_entities",
        filters=filters
    )
    
    return await ingest_data(request)


@router.post("/geocode")
async def geocode_address(request: GeocodeRequest):
    """
    Geocode an address to lat/long coordinates
    
    Uses OpenStreetMap Nominatim API for address geocoding
    
    **Returns:**
    - Latitude and longitude
    - Formatted address
    """
    try:
        agent = DataIngestionAgent()
        
        coordinates = await agent.geocode_address(request.address)
        
        if coordinates:
            return {
                "address": request.address,
                "latitude": coordinates["latitude"],
                "longitude": coordinates["longitude"],
                "geocoded": True,
                "geocoded_at": datetime.utcnow().isoformat(),
            }
        else:
            return {
                "address": request.address,
                "geocoded": False,
                "error": "Could not geocode address",
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error geocoding address: {str(e)}")


@router.get("/stats")
async def get_ingestion_stats():
    """
    Get data ingestion statistics
    
    Returns aggregated stats about data ingestion operations
    """
    # In production, would query database for actual stats
    return {
        "total_ingestions": 3456,
        "total_records_ingested": 15247,
        "by_source": {
            "health_facilities": 4532,
            "doctors": 8765,
            "accreditation": 987,
            "business_entities": 963,
        },
        "last_ingestion": datetime.utcnow().isoformat(),
        "average_ingestion_time_s": 12.4,
        "success_rate": 0.987,
    }
