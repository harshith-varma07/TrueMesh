"""
Data Ingestion Agent - Pulls data from multiple public and partner sources
"""
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import httpx
import json

from app.core.agent_base import BaseAgent, AgentTask, AgentResult, AgentStatus
from app.core.logging import get_logger


class DataIngestionAgent(BaseAgent):
    """
    Data Ingestion Agent - Multi-source data collection
    
    Responsibilities:
    - Pull data from National Health Mission (NHM) facilities
    - Fetch doctor data from National Medical Commission (NMC)
    - Retrieve accreditation data from NABH
    - Get business entity data from MCA
    - Normalize and timestamp all incoming data
    - Store raw and normalized data for processing
    
    Data Sources (MVP - using public/free-tier APIs):
    - data.gov.in Health Facility Directory
    - NMC public lookup (simulated)
    - NABH accreditation search (simulated)
    - MCA corporate data (simulated)
    - OpenStreetMap Nominatim for geocoding
    """
    
    def __init__(self, agent_id: Optional[str] = None):
        super().__init__(agent_id)
        self.http_client = None
        self.data_sources = {
            "nhm_facilities": "https://api.data.gov.in/resource/health-facilities",
            "nmc_doctors": "https://www.nmc.org.in/api/doctors",  # Simulated
            "nabh_accreditation": "https://www.nabh.co/api/search",  # Simulated
            "mca_entities": "https://www.mca.gov.in/api/companies",  # Simulated
            "osm_geocoding": "https://nominatim.openstreetmap.org/search",
        }
        
    async def _get_http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client"""
        if self.http_client is None:
            self.http_client = httpx.AsyncClient(
                timeout=30.0,
                headers={"User-Agent": "TrueMesh-Provider-Intelligence/1.0"}
            )
        return self.http_client
    
    def get_agent_type(self) -> str:
        return "data_ingestion"
    
    async def process_task(self, task: AgentTask) -> AgentResult:
        """Process data ingestion task"""
        start_time = datetime.utcnow()
        
        try:
            params = task.data
            source_type = params.get("source_type", "all")
            filters = params.get("filters", {})
            
            # Ingest data from specified sources
            ingestion_results = await self.ingest_data(source_type, filters)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return AgentResult(
                task_id=task.id,
                agent_id=self.agent_id,
                status=AgentStatus.COMPLETED,
                result={
                    "ingested_count": ingestion_results["total_count"],
                    "by_source": ingestion_results["by_source"],
                    "normalized_data": ingestion_results["normalized_data"],
                    "raw_data_stored": ingestion_results["raw_stored"],
                    "ingestion_stats": ingestion_results["stats"],
                },
                execution_time=execution_time,
                metadata={
                    "source_type": source_type,
                    "ingested_at": datetime.utcnow().isoformat(),
                }
            )
            
        except Exception as e:
            self.logger.error(f"Data ingestion failed: {str(e)}", task_id=task.id)
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return AgentResult(
                task_id=task.id,
                agent_id=self.agent_id,
                status=AgentStatus.FAILED,
                result={},
                error=str(e),
                execution_time=execution_time
            )
    
    async def ingest_data(self, source_type: str, filters: Dict) -> Dict[str, Any]:
        """
        Ingest data from specified sources
        """
        results = {
            "total_count": 0,
            "by_source": {},
            "normalized_data": [],
            "raw_stored": True,
            "stats": {},
        }
        
        # Determine which sources to query
        sources_to_query = []
        if source_type == "all":
            sources_to_query = ["health_facilities", "doctors", "accreditation", "business_entities"]
        else:
            sources_to_query = [source_type]
        
        # Ingest from each source
        for source in sources_to_query:
            try:
                if source == "health_facilities":
                    data = await self._ingest_health_facilities(filters)
                elif source == "doctors":
                    data = await self._ingest_doctors(filters)
                elif source == "accreditation":
                    data = await self._ingest_accreditation(filters)
                elif source == "business_entities":
                    data = await self._ingest_business_entities(filters)
                else:
                    continue
                
                # Normalize and store
                normalized = [self._normalize_record(record, source) for record in data]
                
                results["by_source"][source] = len(normalized)
                results["normalized_data"].extend(normalized)
                results["total_count"] += len(normalized)
                
            except Exception as e:
                self.logger.warning(f"Failed to ingest from {source}: {str(e)}")
                results["by_source"][source] = 0
        
        # Add statistics
        results["stats"] = {
            "sources_queried": len(sources_to_query),
            "sources_succeeded": len([v for v in results["by_source"].values() if v > 0]),
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        return results
    
    async def _ingest_health_facilities(self, filters: Dict) -> List[Dict]:
        """
        Ingest health facility data from NHM / data.gov.in
        For MVP, using simulated data
        """
        # Simulated health facility data (in production, would call real API)
        simulated_facilities = [
            {
                "facility_id": "FAC001",
                "name": "Apollo Hospital",
                "type": "hospital",
                "address": "123 Main Road, Greams Lane",
                "city": "Chennai",
                "state": "Tamil Nadu",
                "postal_code": "600006",
                "phone": "+914412345678",
                "email": "info@apollohospitals.com",
                "beds": 500,
                "specialties": ["Cardiology", "Neurology", "Oncology"],
            },
            {
                "facility_id": "FAC002",
                "name": "Fortis Hospital",
                "type": "hospital",
                "address": "Mulund Goregaon Link Road",
                "city": "Mumbai",
                "state": "Maharashtra",
                "postal_code": "400078",
                "phone": "+912212345678",
                "email": "contact@fortishealthcare.com",
                "beds": 300,
                "specialties": ["Orthopedics", "Cardiology"],
            },
            {
                "facility_id": "FAC003",
                "name": "Medanta Hospital",
                "type": "hospital",
                "address": "Sector 38, Golf Course Road",
                "city": "Gurugram",
                "state": "Haryana",
                "postal_code": "122001",
                "phone": "+911244567890",
                "email": "info@medanta.org",
                "beds": 1500,
                "specialties": ["Cardiac Surgery", "Neurosurgery", "Oncology"],
            },
        ]
        
        # Apply filters
        filtered = simulated_facilities
        if "state" in filters:
            filtered = [f for f in filtered if f.get("state") == filters["state"]]
        if "city" in filters:
            filtered = [f for f in filtered if f.get("city") == filters["city"]]
        
        # In production, would make actual API call:
        # client = await self._get_http_client()
        # response = await client.get(self.data_sources["nhm_facilities"], params=filters)
        # return response.json()["data"]
        
        return filtered
    
    async def _ingest_doctors(self, filters: Dict) -> List[Dict]:
        """
        Ingest doctor data from National Medical Commission
        For MVP, using simulated data
        """
        simulated_doctors = [
            {
                "doctor_id": "DOC001",
                "registration_number": "MH12345",
                "name": "Dr. Rajesh Kumar",
                "specialization": "Cardiology",
                "qualification": "MD, DM",
                "registration_date": "2010-05-15",
                "city": "Mumbai",
                "state": "Maharashtra",
                "email": "dr.rajesh@example.com",
                "phone": "+919876543210",
            },
            {
                "doctor_id": "DOC002",
                "registration_number": "TN67890",
                "name": "Dr. Priya Sharma",
                "specialization": "Neurology",
                "qualification": "MBBS, MD",
                "registration_date": "2015-08-22",
                "city": "Chennai",
                "state": "Tamil Nadu",
                "email": "dr.priya@example.com",
                "phone": "+919876543211",
            },
            {
                "doctor_id": "DOC003",
                "registration_number": "DL11223",
                "name": "Dr. Amit Patel",
                "specialization": "Orthopedics",
                "qualification": "MS Ortho",
                "registration_date": "2012-03-10",
                "city": "Delhi",
                "state": "Delhi",
                "email": "dr.amit@example.com",
                "phone": "+919876543212",
            },
        ]
        
        filtered = simulated_doctors
        if "state" in filters:
            filtered = [d for d in filtered if d.get("state") == filters["state"]]
        if "specialization" in filters:
            filtered = [d for d in filtered if d.get("specialization") == filters["specialization"]]
        
        return filtered
    
    async def _ingest_accreditation(self, filters: Dict) -> List[Dict]:
        """
        Ingest accreditation data from NABH
        For MVP, using simulated data
        """
        simulated_accreditation = [
            {
                "accreditation_id": "ACC001",
                "facility_name": "Apollo Hospital Chennai",
                "accreditation_type": "NABH",
                "status": "Accredited",
                "valid_from": "2022-01-01",
                "valid_until": "2025-12-31",
                "certification_number": "NABH-2022-001",
                "city": "Chennai",
                "state": "Tamil Nadu",
            },
            {
                "accreditation_id": "ACC002",
                "facility_name": "Fortis Hospital Mumbai",
                "accreditation_type": "NABH",
                "status": "Accredited",
                "valid_from": "2021-06-15",
                "valid_until": "2024-06-14",
                "certification_number": "NABH-2021-045",
                "city": "Mumbai",
                "state": "Maharashtra",
            },
        ]
        
        filtered = simulated_accreditation
        if "state" in filters:
            filtered = [a for a in filtered if a.get("state") == filters["state"]]
        
        return filtered
    
    async def _ingest_business_entities(self, filters: Dict) -> List[Dict]:
        """
        Ingest business entity data from MCA
        For MVP, using simulated data
        """
        simulated_entities = [
            {
                "entity_id": "ENT001",
                "company_name": "Apollo Hospitals Enterprise Limited",
                "cin": "L85110TN1979PLC008035",
                "registration_date": "1979-09-15",
                "status": "Active",
                "category": "Company limited by Shares",
                "subcategory": "Indian Non-Government Company",
                "registered_address": "19, Bishop Gardens, Raja Annamalaipuram",
                "city": "Chennai",
                "state": "Tamil Nadu",
            },
            {
                "entity_id": "ENT002",
                "company_name": "Fortis Healthcare Limited",
                "cin": "L85110DL1996PLC276758",
                "registration_date": "1996-11-26",
                "status": "Active",
                "category": "Company limited by Shares",
                "subcategory": "Indian Non-Government Company",
                "registered_address": "Fortis Hospital, Sector 62",
                "city": "Noida",
                "state": "Uttar Pradesh",
            },
        ]
        
        filtered = simulated_entities
        if "state" in filters:
            filtered = [e for e in filtered if e.get("state") == filters["state"]]
        
        return filtered
    
    def _normalize_record(self, record: Dict, source: str) -> Dict[str, Any]:
        """
        Normalize incoming data record to standard format
        """
        normalized = {
            "source": source,
            "ingested_at": datetime.utcnow().isoformat(),
            "raw_data": record,
        }
        
        # Map source-specific fields to standard schema
        if source == "health_facilities":
            normalized.update({
                "provider_type": "hospital",
                "name": record.get("name"),
                "registration_number": record.get("facility_id"),
                "address_line1": record.get("address"),
                "city": record.get("city"),
                "state": record.get("state"),
                "postal_code": record.get("postal_code"),
                "phone": record.get("phone"),
                "email": record.get("email"),
                "metadata": {
                    "beds": record.get("beds"),
                    "specialties": record.get("specialties"),
                }
            })
        elif source == "doctors":
            normalized.update({
                "provider_type": "doctor",
                "name": record.get("name"),
                "registration_number": record.get("registration_number"),
                "city": record.get("city"),
                "state": record.get("state"),
                "email": record.get("email"),
                "phone": record.get("phone"),
                "metadata": {
                    "specialization": record.get("specialization"),
                    "qualification": record.get("qualification"),
                    "registration_date": record.get("registration_date"),
                }
            })
        elif source == "accreditation":
            normalized.update({
                "provider_type": "accreditation",
                "name": record.get("facility_name"),
                "city": record.get("city"),
                "state": record.get("state"),
                "metadata": {
                    "accreditation_type": record.get("accreditation_type"),
                    "status": record.get("status"),
                    "valid_from": record.get("valid_from"),
                    "valid_until": record.get("valid_until"),
                    "certification_number": record.get("certification_number"),
                }
            })
        elif source == "business_entities":
            normalized.update({
                "provider_type": "business",
                "name": record.get("company_name"),
                "registration_number": record.get("cin"),
                "address_line1": record.get("registered_address"),
                "city": record.get("city"),
                "state": record.get("state"),
                "metadata": {
                    "status": record.get("status"),
                    "category": record.get("category"),
                    "registration_date": record.get("registration_date"),
                }
            })
        
        return normalized
    
    async def geocode_address(self, address: str) -> Optional[Dict[str, float]]:
        """
        Geocode address using OpenStreetMap Nominatim
        """
        try:
            client = await self._get_http_client()
            response = await client.get(
                self.data_sources["osm_geocoding"],
                params={
                    "q": address,
                    "format": "json",
                    "limit": 1,
                }
            )
            
            if response.status_code == 200:
                results = response.json()
                if results:
                    return {
                        "latitude": float(results[0]["lat"]),
                        "longitude": float(results[0]["lon"]),
                    }
        except Exception as e:
            self.logger.warning(f"Geocoding failed for {address}: {str(e)}")
        
        return None
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.http_client:
            await self.http_client.aclose()
        await super().cleanup()
