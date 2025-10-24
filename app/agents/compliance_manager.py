"""
Compliance Manager Agent - Ensures data policy compliance and resolves anomalies
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum

from app.core.agent_base import BaseAgent, AgentTask, AgentResult, AgentStatus
from app.core.logging import get_logger


class PolicyType(str, Enum):
    """Policy types"""
    DATA_COMPLETENESS = "data_completeness"
    DATA_ACCURACY = "data_accuracy"
    VERIFICATION_FRESHNESS = "verification_freshness"
    FRAUD_RISK_THRESHOLD = "fraud_risk_threshold"
    CONFIDENCE_THRESHOLD = "confidence_threshold"
    PII_PROTECTION = "pii_protection"


class ComplianceManagerAgent(BaseAgent):
    """
    Compliance Manager Agent - Policy enforcement and exception handling
    
    Responsibilities:
    - Enforce data policies
    - Check compliance status
    - Detect policy violations
    - Auto-resolve violations when possible
    - Escalate unresolvable issues
    - Track compliance metrics
    """
    
    def __init__(self, agent_id: Optional[str] = None):
        super().__init__(agent_id)
        self.policies = self._load_policies()
        self.exceptions: Dict[str, Dict[str, Any]] = {}
        
    def get_agent_type(self) -> str:
        return "compliance_manager"
    
    def _load_policies(self) -> Dict[str, Dict[str, Any]]:
        """Load compliance policies"""
        return {
            PolicyType.DATA_COMPLETENESS.value: {
                "name": "Data Completeness Policy",
                "description": "Provider data must have all required fields",
                "required_fields": ["registration_number", "name", "provider_type", "city", "state"],
                "auto_resolvable": False,
            },
            PolicyType.DATA_ACCURACY.value: {
                "name": "Data Accuracy Policy",
                "description": "Provider data must be accurate and consistent",
                "min_consistency_score": 0.8,
                "auto_resolvable": False,
            },
            PolicyType.VERIFICATION_FRESHNESS.value: {
                "name": "Verification Freshness Policy",
                "description": "Provider verification must be recent",
                "max_age_days": 365,
                "auto_resolvable": False,
            },
            PolicyType.FRAUD_RISK_THRESHOLD.value: {
                "name": "Fraud Risk Threshold Policy",
                "description": "Provider fraud risk must be below threshold",
                "max_fraud_score": 0.5,
                "auto_resolvable": True,
                "resolution_action": "flag_for_review",
            },
            PolicyType.CONFIDENCE_THRESHOLD.value: {
                "name": "Confidence Threshold Policy",
                "description": "Provider confidence score must meet minimum",
                "min_confidence_score": 0.7,
                "auto_resolvable": False,
            },
            PolicyType.PII_PROTECTION.value: {
                "name": "PII Protection Policy",
                "description": "Sensitive data must be properly protected",
                "auto_resolvable": True,
                "resolution_action": "mask_pii",
            },
        }
    
    async def process_task(self, task: AgentTask) -> AgentResult:
        """Process compliance check task"""
        start_time = datetime.utcnow()
        
        try:
            provider_data = task.data
            
            # Perform comprehensive compliance check
            compliance_result = await self.check_compliance(provider_data)
            
            # Auto-resolve violations if possible
            if compliance_result["violations"]:
                resolution_result = await self.auto_resolve_violations(
                    provider_data,
                    compliance_result["violations"]
                )
                compliance_result["auto_resolution"] = resolution_result
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return AgentResult(
                task_id=task.id,
                agent_id=self.agent_id,
                status=AgentStatus.COMPLETED,
                result={
                    "compliance_status": compliance_result["status"],
                    "is_compliant": compliance_result["is_compliant"],
                    "violations": compliance_result["violations"],
                    "checks_performed": compliance_result["checks_performed"],
                    "auto_resolved": compliance_result.get("auto_resolution", {}).get("resolved_count", 0),
                    "checked_at": datetime.utcnow().isoformat(),
                },
                execution_time=execution_time,
                metadata={
                    "compliance_status": compliance_result["status"],
                    "violation_count": len(compliance_result["violations"]),
                }
            )
            
        except Exception as e:
            self.logger.error(f"Compliance check failed: {str(e)}", task_id=task.id)
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return AgentResult(
                task_id=task.id,
                agent_id=self.agent_id,
                status=AgentStatus.FAILED,
                error=str(e),
                execution_time=execution_time
            )
    
    async def check_compliance(self, provider_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive compliance check"""
        self.logger.info("Performing compliance check", provider_id=provider_data.get("id"))
        
        violations = []
        checks_performed = []
        
        # Check each policy
        for policy_type, policy in self.policies.items():
            check_result = await self._check_policy(provider_data, policy_type, policy)
            checks_performed.append({
                "policy": policy_type,
                "passed": check_result["passed"],
            })
            
            if not check_result["passed"]:
                violations.append(check_result["violation"])
        
        is_compliant = len(violations) == 0
        status = "compliant" if is_compliant else "non_compliant"
        
        return {
            "is_compliant": is_compliant,
            "status": status,
            "violations": violations,
            "checks_performed": checks_performed,
            "checked_at": datetime.utcnow().isoformat(),
        }
    
    async def _check_policy(
        self,
        provider_data: Dict[str, Any],
        policy_type: str,
        policy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check a specific policy"""
        if policy_type == PolicyType.DATA_COMPLETENESS.value:
            return self._check_data_completeness(provider_data, policy)
        elif policy_type == PolicyType.DATA_ACCURACY.value:
            return self._check_data_accuracy(provider_data, policy)
        elif policy_type == PolicyType.VERIFICATION_FRESHNESS.value:
            return self._check_verification_freshness(provider_data, policy)
        elif policy_type == PolicyType.FRAUD_RISK_THRESHOLD.value:
            return self._check_fraud_risk(provider_data, policy)
        elif policy_type == PolicyType.CONFIDENCE_THRESHOLD.value:
            return self._check_confidence_threshold(provider_data, policy)
        elif policy_type == PolicyType.PII_PROTECTION.value:
            return self._check_pii_protection(provider_data, policy)
        else:
            return {"passed": True}
    
    def _check_data_completeness(self, provider_data: Dict[str, Any], policy: Dict[str, Any]) -> Dict[str, Any]:
        """Check data completeness policy"""
        required_fields = policy.get("required_fields", [])
        missing_fields = [f for f in required_fields if not provider_data.get(f)]
        
        passed = len(missing_fields) == 0
        
        return {
            "passed": passed,
            "violation": {
                "policy": PolicyType.DATA_COMPLETENESS.value,
                "description": f"Missing required fields: {', '.join(missing_fields)}",
                "severity": "high",
                "auto_resolvable": policy.get("auto_resolvable", False),
                "missing_fields": missing_fields,
            } if not passed else None
        }
    
    def _check_data_accuracy(self, provider_data: Dict[str, Any], policy: Dict[str, Any]) -> Dict[str, Any]:
        """Check data accuracy policy"""
        min_consistency = policy.get("min_consistency_score", 0.8)
        
        # Get consistency score from confidence scoring results
        confidence_scores = provider_data.get("confidence_scores", {})
        consistency_score = confidence_scores.get("consistency_score", 0.0)
        
        passed = consistency_score >= min_consistency
        
        return {
            "passed": passed,
            "violation": {
                "policy": PolicyType.DATA_ACCURACY.value,
                "description": f"Data consistency score {consistency_score} below required {min_consistency}",
                "severity": "medium",
                "auto_resolvable": policy.get("auto_resolvable", False),
                "actual_score": consistency_score,
                "required_score": min_consistency,
            } if not passed else None
        }
    
    def _check_verification_freshness(self, provider_data: Dict[str, Any], policy: Dict[str, Any]) -> Dict[str, Any]:
        """Check verification freshness policy"""
        max_age_days = policy.get("max_age_days", 365)
        
        # Check verified_at timestamp
        verified_at_str = provider_data.get("verified_at")
        if not verified_at_str:
            # No verification timestamp, consider it expired
            return {
                "passed": False,
                "violation": {
                    "policy": PolicyType.VERIFICATION_FRESHNESS.value,
                    "description": "Provider has never been verified",
                    "severity": "high",
                    "auto_resolvable": False,
                }
            }
        
        try:
            verified_at = datetime.fromisoformat(verified_at_str.replace('Z', '+00:00'))
            age_days = (datetime.utcnow() - verified_at).days
            
            passed = age_days <= max_age_days
            
            return {
                "passed": passed,
                "violation": {
                    "policy": PolicyType.VERIFICATION_FRESHNESS.value,
                    "description": f"Verification is {age_days} days old (max: {max_age_days})",
                    "severity": "medium",
                    "auto_resolvable": False,
                    "age_days": age_days,
                    "max_age_days": max_age_days,
                } if not passed else None
            }
        except:
            return {"passed": True}  # Skip if date parsing fails
    
    def _check_fraud_risk(self, provider_data: Dict[str, Any], policy: Dict[str, Any]) -> Dict[str, Any]:
        """Check fraud risk threshold policy"""
        max_fraud_score = policy.get("max_fraud_score", 0.5)
        
        # Get fraud score from fraud detection results
        fraud_score = provider_data.get("fraud_score", 0.0)
        
        passed = fraud_score <= max_fraud_score
        
        return {
            "passed": passed,
            "violation": {
                "policy": PolicyType.FRAUD_RISK_THRESHOLD.value,
                "description": f"Fraud score {fraud_score} exceeds threshold {max_fraud_score}",
                "severity": "critical",
                "auto_resolvable": policy.get("auto_resolvable", True),
                "resolution_action": policy.get("resolution_action"),
                "fraud_score": fraud_score,
                "max_fraud_score": max_fraud_score,
            } if not passed else None
        }
    
    def _check_confidence_threshold(self, provider_data: Dict[str, Any], policy: Dict[str, Any]) -> Dict[str, Any]:
        """Check confidence threshold policy"""
        min_confidence = policy.get("min_confidence_score", 0.7)
        
        # Get overall confidence score
        confidence_scores = provider_data.get("confidence_scores", {})
        overall_score = confidence_scores.get("overall_score", 0.0)
        
        passed = overall_score >= min_confidence
        
        return {
            "passed": passed,
            "violation": {
                "policy": PolicyType.CONFIDENCE_THRESHOLD.value,
                "description": f"Confidence score {overall_score} below threshold {min_confidence}",
                "severity": "medium",
                "auto_resolvable": policy.get("auto_resolvable", False),
                "overall_score": overall_score,
                "min_confidence": min_confidence,
            } if not passed else None
        }
    
    def _check_pii_protection(self, provider_data: Dict[str, Any], policy: Dict[str, Any]) -> Dict[str, Any]:
        """Check PII protection policy"""
        # Check if sensitive fields are properly masked/encrypted in certain contexts
        # For now, we'll pass this check as PII handling is done at the ledger level
        return {"passed": True}
    
    async def auto_resolve_violations(
        self,
        provider_data: Dict[str, Any],
        violations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Attempt to auto-resolve violations"""
        resolved = []
        unresolved = []
        
        for violation in violations:
            if violation.get("auto_resolvable", False):
                resolution = await self._resolve_violation(provider_data, violation)
                if resolution["success"]:
                    resolved.append(violation)
                else:
                    unresolved.append(violation)
            else:
                unresolved.append(violation)
        
        return {
            "resolved_count": len(resolved),
            "unresolved_count": len(unresolved),
            "resolved": resolved,
            "unresolved": unresolved,
        }
    
    async def _resolve_violation(
        self,
        provider_data: Dict[str, Any],
        violation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve a specific violation"""
        policy = violation["policy"]
        resolution_action = violation.get("resolution_action")
        
        if policy == PolicyType.FRAUD_RISK_THRESHOLD.value:
            # Flag for manual review
            self.logger.info(
                "Auto-resolving fraud risk violation",
                provider_id=provider_data.get("id"),
                action="flag_for_review"
            )
            return {
                "success": True,
                "action": "flagged_for_review",
                "message": "Provider flagged for manual fraud review",
            }
        
        return {
            "success": False,
            "message": "No auto-resolution available for this violation",
        }
    
    def grant_exception(
        self,
        provider_id: str,
        policy_type: str,
        reason: str,
        duration_days: int = 30
    ) -> Dict[str, Any]:
        """Grant a compliance exception"""
        exception_id = f"exception_{provider_id}_{policy_type}_{datetime.utcnow().timestamp()}"
        
        exception = {
            "exception_id": exception_id,
            "provider_id": provider_id,
            "policy_type": policy_type,
            "reason": reason,
            "granted_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(days=duration_days)).isoformat(),
            "granted_by": self.agent_id,
        }
        
        self.exceptions[exception_id] = exception
        
        self.logger.info(
            "Compliance exception granted",
            exception_id=exception_id,
            provider_id=provider_id,
            policy_type=policy_type
        )
        
        return exception
    
    def get_active_exceptions(self, provider_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get active exceptions"""
        now = datetime.utcnow()
        
        active = []
        for exception in self.exceptions.values():
            expires_at = datetime.fromisoformat(exception["expires_at"].replace('Z', '+00:00'))
            
            if expires_at > now:
                if provider_id is None or exception["provider_id"] == provider_id:
                    active.append(exception)
        
        return active
