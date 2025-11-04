"""
Entity Resolution API Endpoints - Deduplication and entity matching
"""
from typing import List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime

from app.core.agent_base import AgentTask
from app.agents.entity_resolution import EntityResolutionAgent

router = APIRouter()


class ProviderInput(BaseModel):
    """Provider data for entity resolution"""
    id: str = None
    name: str
    registration_number: str = None
    email: str = None
    phone: str = None
    address_line1: str = None
    city: str = None
    state: str = None
    postal_code: str = None
    provider_type: str = None
    source: str = "manual"


class EntityResolutionRequest(BaseModel):
    """Entity resolution request"""
    providers: List[ProviderInput] = Field(..., description="List of provider records to resolve")
    similarity_threshold: float = Field(default=0.85, ge=0.0, le=1.0, description="Similarity threshold (0-1)")


class CanonicalEntity(BaseModel):
    """Canonical entity result"""
    canonical_id: str
    name: str
    registration_number: str = None
    provider_type: str = None
    email: str = None
    phone: str = None
    address_line1: str = None
    city: str = None
    state: str = None
    postal_code: str = None
    member_count: int
    member_ids: List[str]
    sources: List[str]
    resolved_at: str


class DuplicateGroup(BaseModel):
    """Duplicate group information"""
    canonical_id: str
    members: List[str]
    member_count: int


class EntityResolutionResponse(BaseModel):
    """Entity resolution response"""
    canonical_entities: List[CanonicalEntity]
    duplicate_groups: List[DuplicateGroup]
    entity_count: int
    duplicate_count: int
    resolution_stats: dict


@router.post("/resolve", response_model=EntityResolutionResponse)
async def resolve_entities(request: EntityResolutionRequest):
    """
    Resolve entities using fuzzy matching and deduplication
    
    This endpoint identifies duplicate provider records across different sources
    and creates canonical entities. Uses:
    - Levenshtein distance for string similarity
    - Weighted field matching (name, registration, phone, email, address)
    - Graph-based clustering for relationships
    
    **Process:**
    1. Normalize all provider records
    2. Calculate similarity matrix
    3. Group similar records (above threshold)
    4. Create canonical entities from groups
    5. Build relationship graph
    
    **Returns:**
    - Canonical entities (deduplicated records)
    - Duplicate groups with member lists
    - Resolution statistics
    """
    try:
        # Create agent instance
        agent = EntityResolutionAgent()
        
        # Override similarity threshold if provided
        if request.similarity_threshold:
            agent.similarity_threshold = request.similarity_threshold
        
        # Convert Pydantic models to dicts
        providers_data = [p.model_dump() for p in request.providers]
        
        # Create task
        task = AgentTask(
            id=f"entity-resolution-{datetime.utcnow().timestamp()}",
            task_type="entity_resolution",
            priority=1,
            data={
                "providers": providers_data,
            }
        )
        
        # Process task
        result = await agent.process_task(task)
        
        if result.status.value == "failed":
            raise HTTPException(status_code=500, detail=result.error or "Entity resolution failed")
        
        # Extract results
        canonical_entities = result.result.get("canonical_entities", [])
        duplicate_groups = result.result.get("duplicate_groups", [])
        
        return EntityResolutionResponse(
            canonical_entities=[CanonicalEntity(**e) for e in canonical_entities],
            duplicate_groups=[DuplicateGroup(**g) for g in duplicate_groups],
            entity_count=result.result.get("entity_count", 0),
            duplicate_count=result.result.get("duplicate_count", 0),
            resolution_stats=result.result.get("resolution_stats", {}),
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resolving entities: {str(e)}")


@router.post("/check-duplicates")
async def check_duplicates(providers: List[ProviderInput]):
    """
    Quick duplicate check for provider records
    
    Returns potential duplicates without creating canonical entities.
    Useful for validation before adding new providers.
    """
    try:
        agent = EntityResolutionAgent()
        
        providers_data = [p.model_dump() for p in providers]
        
        # Perform resolution
        resolution_results = await agent.resolve_entities(providers_data)
        
        # Extract only duplicate information
        duplicates = [
            group for group in resolution_results["duplicate_groups"]
            if group["member_count"] > 1
        ]
        
        return {
            "has_duplicates": len(duplicates) > 0,
            "duplicate_count": len(duplicates),
            "duplicates": duplicates,
            "checked_at": datetime.utcnow().isoformat(),
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking duplicates: {str(e)}")


@router.post("/similarity")
async def calculate_similarity(provider_a: ProviderInput, provider_b: ProviderInput):
    """
    Calculate similarity score between two providers
    
    Returns similarity score (0-1) based on weighted field matching:
    - Name: 35%
    - Registration number: 30%
    - Phone: 15%
    - Email: 10%
    - Address: 10%
    """
    try:
        agent = EntityResolutionAgent()
        
        # Normalize providers
        normalized_a = agent._normalize_provider(provider_a.model_dump())
        normalized_b = agent._normalize_provider(provider_b.model_dump())
        
        # Calculate similarity
        similarity = agent._calculate_similarity(normalized_a, normalized_b)
        
        return {
            "similarity_score": round(similarity, 4),
            "is_duplicate": similarity >= agent.similarity_threshold,
            "threshold": agent.similarity_threshold,
            "field_scores": {
                "name": agent._levenshtein_ratio(normalized_a["name"], normalized_b["name"]),
                "registration": agent._levenshtein_ratio(
                    normalized_a["registration_number"], 
                    normalized_b["registration_number"]
                ),
                "phone": agent._levenshtein_ratio(normalized_a["phone"], normalized_b["phone"]),
                "email": agent._levenshtein_ratio(normalized_a["email"], normalized_b["email"]),
                "address": agent._levenshtein_ratio(normalized_a["address"], normalized_b["address"]),
            },
            "calculated_at": datetime.utcnow().isoformat(),
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating similarity: {str(e)}")


@router.get("/stats")
async def get_resolution_stats():
    """
    Get entity resolution statistics
    
    Returns aggregated stats about entity resolution operations
    """
    # In production, would query database for actual stats
    return {
        "total_resolutions": 1543,
        "total_canonical_entities": 12876,
        "total_duplicates_found": 2371,
        "average_duplicates_per_entity": 1.18,
        "deduplication_rate": 0.155,  # 15.5%
        "average_resolution_time_ms": 234.5,
        "stats_as_of": datetime.utcnow().isoformat(),
    }
