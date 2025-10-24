"""
Data Verification Agent - Fetches and validates provider data from multiple sources
"""
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import httpx

from app.core.agent_base import BaseAgent, AgentTask, AgentResult, AgentStatus
from app.core.logging import get_logger


class DataVerificationAgent(BaseAgent):
    """
    Data Verification Agent - Multi-source data validation
    
    Responsibilities:
    - Fetch data from external registries (MCI, IRDAI, etc.)
    - Validate provider credentials
    - Cross-reference data across multiple sources
    - Detect data inconsistencies
    - Update verification records in database
    """
    
    def __init__(self, agent_id: Optional[str] = None):
        super().__init__(agent_id)
        self.http_client = None
        
    async def _get_http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client"""
        if self.http_client is None:
            self.http_client = httpx.AsyncClient(timeout=30.0)
        return self.http_client
    
    def get_agent_type(self) -> str:
        return "data_verification"
    
    async def process_task(self, task: AgentTask) -> AgentResult:
        """Process data verification task"""
        start_time = datetime.utcnow()
        
        try:
            provider_data = task.data
            registration_number = provider_data.get("registration_number")
            provider_type = provider_data.get("provider_type")
            
            if not registration_number:
                raise ValueError("registration_number is required")
            
            # Perform multi-source verification
            verification_results = await self.verify_provider(provider_data)
            
            # Calculate overall verification status
            is_verified = self._calculate_verification_status(verification_results)
            confidence_score = self._calculate_verification_confidence(verification_results)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return AgentResult(
                task_id=task.id,
                agent_id=self.agent_id,
                status=AgentStatus.COMPLETED,
                result={
                    "is_verified": is_verified,
                    "confidence_score": confidence_score,
                    "verification_results": verification_results,
                    "verified_at": datetime.utcnow().isoformat(),
                },
                execution_time=execution_time,
                metadata={
                    "provider_type": provider_type,
                    "registration_number": registration_number,
                }
            )
            
        except Exception as e:
            self.logger.error(f"Data verification failed: {str(e)}", task_id=task.id)
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return AgentResult(
                task_id=task.id,
                agent_id=self.agent_id,
                status=AgentStatus.FAILED,
                error=str(e),
                execution_time=execution_time
            )
    
    async def verify_provider(self, provider_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify provider against multiple data sources"""
        registration_number = provider_data.get("registration_number")
        provider_type = provider_data.get("provider_type")
        
        self.logger.info(
            "Starting multi-source verification",
            registration_number=registration_number,
            provider_type=provider_type
        )
        
        verification_tasks = []
        
        # MCI Registry verification (for doctors)
        if provider_type == "doctor":
            verification_tasks.append(
                self._verify_mci_registry(registration_number, provider_data)
            )
        
        # Insurance Registry verification
        verification_tasks.append(
            self._verify_insurance_registry(registration_number, provider_data)
        )
        
        # Government database verification
        verification_tasks.append(
            self._verify_government_database(registration_number, provider_data)
        )
        
        # Execute all verifications concurrently
        results = await asyncio.gather(*verification_tasks, return_exceptions=True)
        
        # Compile verification results
        verification_results = {
            "mci_registry": None,
            "insurance_registry": None,
            "government_database": None,
        }
        
        result_keys = ["mci_registry", "insurance_registry", "government_database"]
        for i, result in enumerate(results[:len(result_keys)]):
            if isinstance(result, Exception):
                verification_results[result_keys[i]] = {
                    "status": "error",
                    "error": str(result),
                }
            else:
                verification_results[result_keys[i]] = result
        
        return verification_results
    
    async def _verify_mci_registry(self, registration_number: str, provider_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify against MCI (Medical Council of India) registry"""
        try:
            # Simulate MCI API call (in production, make actual API call)
            self.logger.info("Verifying against MCI registry", registration_number=registration_number)
            
            # In production, this would be an actual API call:
            # client = await self._get_http_client()
            # response = await client.get(
            #     f"{self.settings.mci_registry_url}/verify/{registration_number}"
            # )
            
            # For now, simulate verification based on registration number format
            is_valid = len(registration_number) >= 6 and registration_number.isalnum()
            
            return {
                "status": "verified" if is_valid else "not_found",
                "source": "mci_registry",
                "verified_at": datetime.utcnow().isoformat(),
                "confidence": 0.9 if is_valid else 0.0,
                "data": {
                    "registration_number": registration_number,
                    "name": provider_data.get("name"),
                    "specialization": provider_data.get("specialization"),
                } if is_valid else None
            }
            
        except Exception as e:
            self.logger.error(f"MCI verification failed: {str(e)}")
            return {
                "status": "error",
                "source": "mci_registry",
                "error": str(e),
                "confidence": 0.0,
            }
    
    async def _verify_insurance_registry(self, registration_number: str, provider_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify against insurance registry"""
        try:
            self.logger.info("Verifying against insurance registry", registration_number=registration_number)
            
            # Simulate verification
            is_valid = len(registration_number) >= 6
            
            return {
                "status": "verified" if is_valid else "not_found",
                "source": "insurance_registry",
                "verified_at": datetime.utcnow().isoformat(),
                "confidence": 0.85 if is_valid else 0.0,
                "data": {
                    "registration_number": registration_number,
                    "empaneled": is_valid,
                } if is_valid else None
            }
            
        except Exception as e:
            self.logger.error(f"Insurance registry verification failed: {str(e)}")
            return {
                "status": "error",
                "source": "insurance_registry",
                "error": str(e),
                "confidence": 0.0,
            }
    
    async def _verify_government_database(self, registration_number: str, provider_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify against government database"""
        try:
            self.logger.info("Verifying against government database", registration_number=registration_number)
            
            # Simulate verification
            is_valid = len(registration_number) >= 6
            
            return {
                "status": "verified" if is_valid else "not_found",
                "source": "government_database",
                "verified_at": datetime.utcnow().isoformat(),
                "confidence": 0.8 if is_valid else 0.0,
                "data": {
                    "registration_number": registration_number,
                    "licensed": is_valid,
                } if is_valid else None
            }
            
        except Exception as e:
            self.logger.error(f"Government database verification failed: {str(e)}")
            return {
                "status": "error",
                "source": "government_database",
                "error": str(e),
                "confidence": 0.0,
            }
    
    def _calculate_verification_status(self, verification_results: Dict[str, Any]) -> bool:
        """Calculate overall verification status"""
        verified_count = 0
        total_sources = 0
        
        for source, result in verification_results.items():
            if result is not None:
                total_sources += 1
                if result.get("status") == "verified":
                    verified_count += 1
        
        # Consider verified if at least 2 sources confirm
        return verified_count >= 2 if total_sources >= 2 else verified_count >= 1
    
    def _calculate_verification_confidence(self, verification_results: Dict[str, Any]) -> float:
        """Calculate overall verification confidence score"""
        confidences = []
        
        for source, result in verification_results.items():
            if result is not None and "confidence" in result:
                confidences.append(result["confidence"])
        
        if not confidences:
            return 0.0
        
        # Return average confidence
        return sum(confidences) / len(confidences)
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.http_client:
            await self.http_client.aclose()
