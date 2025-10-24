"""
PITL Agent - Provider-Initiated Trust Loop for secure provider updates
"""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from app.core.agent_base import BaseAgent, AgentTask, AgentResult, AgentStatus
from app.core.logging import get_logger


class PITLAgent(BaseAgent):
    """
    PITL Agent - Provider-Initiated Trust Loop
    
    Responsibilities:
    - Handle provider-initiated update requests
    - Validate provider authentication
    - Process challenge requests
    - Track provider-initiated changes
    - Maintain trust loop integrity
    """
    
    def __init__(self, agent_id: Optional[str] = None):
        super().__init__(agent_id)
        self.pending_challenges: Dict[str, Dict[str, Any]] = {}
        
    def get_agent_type(self) -> str:
        return "pitl"
    
    async def process_task(self, task: AgentTask) -> AgentResult:
        """Process PITL task"""
        start_time = datetime.utcnow()
        
        try:
            provider_data = task.data
            operation = provider_data.get("pitl_operation", "update_request")
            
            # Route to appropriate PITL operation
            if operation == "update_request":
                result_data = await self.handle_update_request(provider_data)
            elif operation == "challenge":
                result_data = await self.handle_challenge(provider_data)
            elif operation == "verify_challenge":
                result_data = await self.verify_challenge(provider_data)
            else:
                raise ValueError(f"Unknown PITL operation: {operation}")
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return AgentResult(
                task_id=task.id,
                agent_id=self.agent_id,
                status=AgentStatus.COMPLETED,
                result=result_data,
                execution_time=execution_time,
                metadata={
                    "operation": operation,
                    "provider_id": provider_data.get("id"),
                }
            )
            
        except Exception as e:
            self.logger.error(f"PITL operation failed: {str(e)}", task_id=task.id)
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return AgentResult(
                task_id=task.id,
                agent_id=self.agent_id,
                status=AgentStatus.FAILED,
                error=str(e),
                execution_time=execution_time
            )
    
    async def handle_update_request(self, provider_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle provider update request"""
        provider_id = provider_data.get("id") or provider_data.get("registration_number")
        updates = provider_data.get("updates", {})
        
        if not provider_id:
            raise ValueError("Provider ID is required")
        
        if not updates:
            raise ValueError("Update data is required")
        
        self.logger.info(
            "Processing provider update request",
            provider_id=provider_id,
            update_fields=list(updates.keys())
        )
        
        # Validate update request
        validation_result = self._validate_update_request(provider_data, updates)
        
        if not validation_result["is_valid"]:
            return {
                "status": "rejected",
                "reason": validation_result["reason"],
                "provider_id": provider_id,
            }
        
        # Create update record
        update_record = {
            "provider_id": provider_id,
            "updates": updates,
            "requested_at": datetime.utcnow().isoformat(),
            "status": "approved",
            "approved_by": self.agent_id,
        }
        
        return {
            "status": "approved",
            "update_record": update_record,
            "provider_id": provider_id,
            "updated_fields": list(updates.keys()),
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    async def handle_challenge(self, provider_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle provider challenge to existing data"""
        provider_id = provider_data.get("id") or provider_data.get("registration_number")
        challenge_data = provider_data.get("challenge_data", {})
        challenge_reason = provider_data.get("challenge_reason", "")
        
        if not provider_id:
            raise ValueError("Provider ID is required")
        
        if not challenge_data:
            raise ValueError("Challenge data is required")
        
        self.logger.info(
            "Processing provider challenge",
            provider_id=provider_id,
            reason=challenge_reason
        )
        
        # Create challenge record
        challenge_id = f"challenge_{provider_id}_{datetime.utcnow().timestamp()}"
        
        challenge_record = {
            "challenge_id": challenge_id,
            "provider_id": provider_id,
            "challenge_data": challenge_data,
            "challenge_reason": challenge_reason,
            "status": "pending_review",
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(days=7)).isoformat(),
        }
        
        # Store challenge for review
        self.pending_challenges[challenge_id] = challenge_record
        
        return {
            "status": "challenge_received",
            "challenge_id": challenge_id,
            "challenge_record": challenge_record,
            "next_steps": "Challenge will be reviewed within 48 hours",
        }
    
    async def verify_challenge(self, provider_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify and resolve a provider challenge"""
        challenge_id = provider_data.get("challenge_id")
        resolution = provider_data.get("resolution", "approve")  # approve, reject
        
        if not challenge_id:
            raise ValueError("Challenge ID is required")
        
        if challenge_id not in self.pending_challenges:
            raise ValueError(f"Challenge not found: {challenge_id}")
        
        challenge = self.pending_challenges[challenge_id]
        
        self.logger.info(
            "Verifying provider challenge",
            challenge_id=challenge_id,
            resolution=resolution
        )
        
        # Update challenge status
        challenge["status"] = "approved" if resolution == "approve" else "rejected"
        challenge["resolved_at"] = datetime.utcnow().isoformat()
        challenge["resolved_by"] = self.agent_id
        
        # If approved, apply the challenged data
        if resolution == "approve":
            return {
                "status": "challenge_approved",
                "challenge_id": challenge_id,
                "provider_id": challenge["provider_id"],
                "updates_applied": challenge["challenge_data"],
                "timestamp": datetime.utcnow().isoformat(),
            }
        else:
            return {
                "status": "challenge_rejected",
                "challenge_id": challenge_id,
                "provider_id": challenge["provider_id"],
                "reason": "Challenge did not meet verification criteria",
                "timestamp": datetime.utcnow().isoformat(),
            }
    
    def _validate_update_request(
        self,
        provider_data: Dict[str, Any],
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate provider update request"""
        # Check for critical fields that shouldn't be changed directly
        restricted_fields = ["registration_number", "provider_type"]
        
        for field in restricted_fields:
            if field in updates:
                return {
                    "is_valid": False,
                    "reason": f"Field '{field}' cannot be updated directly",
                }
        
        # Validate update data format
        if "email" in updates:
            email = updates["email"]
            if not email or "@" not in email:
                return {
                    "is_valid": False,
                    "reason": "Invalid email format",
                }
        
        if "phone" in updates:
            phone = updates["phone"]
            if not phone or len(phone) < 10:
                return {
                    "is_valid": False,
                    "reason": "Invalid phone number format",
                }
        
        return {
            "is_valid": True,
            "reason": "Validation passed",
        }
    
    def get_pending_challenges(self) -> Dict[str, Any]:
        """Get all pending challenges"""
        pending = [
            c for c in self.pending_challenges.values()
            if c["status"] == "pending_review"
        ]
        
        return {
            "pending_count": len(pending),
            "challenges": pending,
        }
    
    def get_challenge_status(self, challenge_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific challenge"""
        return self.pending_challenges.get(challenge_id)
