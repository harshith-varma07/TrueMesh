"""
Agent registry initialization
"""
from app.core.agent_base import agent_registry
from app.agents.orchestrator import OrchestratorAgent
from app.agents.data_verification import DataVerificationAgent
from app.agents.confidence_scoring import ConfidenceScoringAgent
from app.agents.fraud_detection import FraudDetectionAgent
from app.agents.provenance_ledger import ProvenanceLedgerAgent
from app.agents.federated_publisher import FederatedPublisherAgent
from app.agents.pitl import PITLAgent
from app.agents.compliance_manager import ComplianceManagerAgent


def register_all_agents():
    """Register all agent types with the agent registry"""
    agent_registry.register_agent_type("orchestrator", OrchestratorAgent)
    agent_registry.register_agent_type("data_verification", DataVerificationAgent)
    agent_registry.register_agent_type("confidence_scoring", ConfidenceScoringAgent)
    agent_registry.register_agent_type("fraud_detection", FraudDetectionAgent)
    agent_registry.register_agent_type("provenance_ledger", ProvenanceLedgerAgent)
    agent_registry.register_agent_type("federated_publisher", FederatedPublisherAgent)
    agent_registry.register_agent_type("pitl", PITLAgent)
    agent_registry.register_agent_type("compliance_manager", ComplianceManagerAgent)
