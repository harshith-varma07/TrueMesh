"""
Orchestrator Agent - Coordinates all agents and workflows
"""
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

from app.core.agent_base import BaseAgent, AgentTask, AgentResult, AgentStatus, TaskPriority, agent_registry
from app.core.logging import get_logger


class WorkflowType(str, Enum):
    """Workflow types"""
    PROVIDER_REGISTRATION = "provider_registration"
    PROVIDER_VERIFICATION = "provider_verification"
    PROVIDER_UPDATE = "provider_update"
    FRAUD_INVESTIGATION = "fraud_investigation"
    COMPLIANCE_CHECK = "compliance_check"
    FEDERATION_SYNC = "federation_sync"


class OrchestratorAgent(BaseAgent):
    """
    Orchestrator Agent - Central coordinator for all agent workflows
    
    Responsibilities:
    - Route tasks to appropriate agents
    - Manage workflow execution
    - Handle task dependencies and sequencing
    - Monitor agent health and performance
    - Coordinate multi-agent workflows
    """
    
    def __init__(self, agent_id: Optional[str] = None):
        super().__init__(agent_id)
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.running = False
        self.workflows: Dict[str, List[str]] = self._define_workflows()
        
    def get_agent_type(self) -> str:
        return "orchestrator"
    
    def _define_workflows(self) -> Dict[str, List[str]]:
        """Define workflow sequences"""
        return {
            WorkflowType.PROVIDER_REGISTRATION.value: [
                "data_verification",
                "fraud_detection",
                "confidence_scoring",
                "provenance_ledger",
                "compliance_manager",
            ],
            WorkflowType.PROVIDER_VERIFICATION.value: [
                "data_verification",
                "confidence_scoring",
                "provenance_ledger",
            ],
            WorkflowType.PROVIDER_UPDATE.value: [
                "pitl",
                "data_verification",
                "confidence_scoring",
                "provenance_ledger",
                "federated_publisher",
            ],
            WorkflowType.FRAUD_INVESTIGATION.value: [
                "fraud_detection",
                "data_verification",
                "compliance_manager",
            ],
            WorkflowType.COMPLIANCE_CHECK.value: [
                "compliance_manager",
                "data_verification",
            ],
            WorkflowType.FEDERATION_SYNC.value: [
                "federated_publisher",
                "provenance_ledger",
            ],
        }
    
    async def process_task(self, task: AgentTask) -> AgentResult:
        """Process orchestration task"""
        start_time = datetime.utcnow()
        
        try:
            workflow_type = task.data.get("workflow_type")
            provider_data = task.data.get("provider_data", {})
            
            if not workflow_type:
                raise ValueError("workflow_type is required")
            
            # Execute workflow
            workflow_result = await self.execute_workflow(workflow_type, provider_data)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return AgentResult(
                task_id=task.id,
                agent_id=self.agent_id,
                status=AgentStatus.COMPLETED,
                result={
                    "workflow_type": workflow_type,
                    "workflow_result": workflow_result,
                    "completed_steps": len(workflow_result.get("steps", [])),
                },
                execution_time=execution_time,
                metadata={
                    "workflow_type": workflow_type,
                    "provider_id": provider_data.get("id"),
                }
            )
            
        except Exception as e:
            self.logger.error(f"Orchestration failed: {str(e)}", task_id=task.id)
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return AgentResult(
                task_id=task.id,
                agent_id=self.agent_id,
                status=AgentStatus.FAILED,
                error=str(e),
                execution_time=execution_time
            )
    
    async def execute_workflow(self, workflow_type: str, provider_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a complete workflow"""
        if workflow_type not in self.workflows:
            raise ValueError(f"Unknown workflow type: {workflow_type}")
        
        agent_sequence = self.workflows[workflow_type]
        results = []
        
        self.logger.info(
            f"Starting workflow execution",
            workflow_type=workflow_type,
            agent_sequence=agent_sequence
        )
        
        # Execute agents in sequence
        for agent_type in agent_sequence:
            try:
                # Get or create agent
                agents = agent_registry.get_agents_by_type(agent_type)
                if not agents:
                    agent = agent_registry.create_agent(agent_type)
                else:
                    agent = agents[0]
                
                # Create task for agent
                task = AgentTask(
                    agent_type=agent_type,
                    priority=TaskPriority.HIGH,
                    data=provider_data
                )
                
                # Execute agent task
                result = await agent.execute_task(task)
                
                results.append({
                    "agent_type": agent_type,
                    "status": result.status.value,
                    "result": result.result,
                    "execution_time": result.execution_time,
                })
                
                # Update provider data with results for next agent
                if result.result:
                    provider_data.update(result.result)
                
                # Stop workflow if agent failed critically
                if result.status == AgentStatus.FAILED:
                    self.logger.warning(
                        f"Workflow step failed, continuing anyway",
                        agent_type=agent_type,
                        error=result.error
                    )
                    
            except Exception as e:
                self.logger.error(
                    f"Agent execution failed in workflow",
                    agent_type=agent_type,
                    error=str(e)
                )
                results.append({
                    "agent_type": agent_type,
                    "status": "failed",
                    "error": str(e),
                })
        
        return {
            "workflow_type": workflow_type,
            "steps": results,
            "success": all(r.get("status") != "failed" for r in results),
            "completed_at": datetime.utcnow().isoformat(),
        }
    
    async def submit_task(self, workflow_type: str, provider_data: Dict[str, Any], priority: TaskPriority = TaskPriority.MEDIUM) -> str:
        """Submit a task to the orchestrator"""
        task = AgentTask(
            agent_type=self.get_agent_type(),
            priority=priority,
            data={
                "workflow_type": workflow_type,
                "provider_data": provider_data,
            }
        )
        
        await self.task_queue.put(task)
        self.logger.info(f"Task submitted", task_id=task.id, workflow_type=workflow_type)
        
        return task.id
    
    async def start(self):
        """Start the orchestrator background worker"""
        self.running = True
        self.logger.info("Orchestrator agent started")
        
        while self.running:
            try:
                # Wait for tasks with timeout
                task = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)
                
                # Execute task in background
                asyncio.create_task(self.execute_task(task))
                
            except asyncio.TimeoutError:
                # No tasks in queue, continue waiting
                continue
            except Exception as e:
                self.logger.error(f"Orchestrator error: {str(e)}")
                await asyncio.sleep(1)
    
    async def stop(self):
        """Stop the orchestrator"""
        self.running = False
        self.logger.info("Orchestrator agent stopped")
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Get current workflow status"""
        return {
            "agent_id": self.agent_id,
            "status": self.status.value,
            "queue_size": self.task_queue.qsize(),
            "available_workflows": list(self.workflows.keys()),
            "task_history_count": len(self.task_history),
        }
