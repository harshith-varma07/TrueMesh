"""
Base agent class and agent framework for TrueMesh Provider Intelligence
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type
from enum import Enum
import asyncio
import uuid
from datetime import datetime
import json

from pydantic import BaseModel, Field
from app.core.logging import get_logger
from app.core.config import get_settings


class AgentStatus(str, Enum):
    """Agent execution status"""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class TaskPriority(int, Enum):
    """Task priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class AgentTask(BaseModel):
    """Agent task definition"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_type: str
    priority: TaskPriority = TaskPriority.MEDIUM
    data: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: AgentStatus = AgentStatus.IDLE
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3


class AgentResult(BaseModel):
    """Agent execution result"""
    task_id: str
    agent_id: str
    status: AgentStatus
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BaseAgent(ABC):
    """Base class for all agents in the TrueMesh system"""
    
    def __init__(self, agent_id: Optional[str] = None):
        self.agent_id = agent_id or f"{self.__class__.__name__}_{uuid.uuid4().hex[:8]}"
        self.logger = get_logger(self.agent_id)
        self.settings = get_settings()
        self.status = AgentStatus.IDLE
        self.current_task: Optional[AgentTask] = None
        self.task_history: List[AgentResult] = []
        
    @abstractmethod
    async def process_task(self, task: AgentTask) -> AgentResult:
        """Process a given task and return the result"""
        pass
    
    @abstractmethod
    def get_agent_type(self) -> str:
        """Return the agent type identifier"""
        pass
    
    async def execute_task(self, task: AgentTask) -> AgentResult:
        """Execute a task with error handling and timeout"""
        self.status = AgentStatus.RUNNING
        self.current_task = task
        task.started_at = datetime.utcnow()
        task.status = AgentStatus.RUNNING
        
        start_time = datetime.utcnow()
        
        try:
            self.logger.info(
                "Starting task execution",
                task_id=task.id,
                agent_type=self.get_agent_type(),
                priority=task.priority.name
            )
            
            # Execute with timeout
            result = await asyncio.wait_for(
                self.process_task(task),
                timeout=self.settings.agent_timeout_seconds
            )
            
            task.completed_at = datetime.utcnow()
            task.status = AgentStatus.COMPLETED
            self.status = AgentStatus.COMPLETED
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            result.execution_time = execution_time
            
            self.logger.info(
                "Task completed successfully",
                task_id=task.id,
                execution_time=execution_time
            )
            
            self.task_history.append(result)
            return result
            
        except asyncio.TimeoutError:
            error_msg = f"Task {task.id} timed out after {self.settings.agent_timeout_seconds} seconds"
            self.logger.error(error_msg, task_id=task.id)
            
            task.status = AgentStatus.TIMEOUT
            self.status = AgentStatus.TIMEOUT
            
            result = AgentResult(
                task_id=task.id,
                agent_id=self.agent_id,
                status=AgentStatus.TIMEOUT,
                error=error_msg,
                execution_time=(datetime.utcnow() - start_time).total_seconds()
            )
            
            self.task_history.append(result)
            return result
            
        except Exception as e:
            error_msg = f"Task {task.id} failed: {str(e)}"
            self.logger.error(error_msg, task_id=task.id, error=str(e))
            
            task.status = AgentStatus.FAILED
            task.error = str(e)
            self.status = AgentStatus.FAILED
            
            result = AgentResult(
                task_id=task.id,
                agent_id=self.agent_id,
                status=AgentStatus.FAILED,
                error=error_msg,
                execution_time=(datetime.utcnow() - start_time).total_seconds()
            )
            
            self.task_history.append(result)
            return result
        
        finally:
            self.current_task = None
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.get_agent_type(),
            "status": self.status,
            "current_task": self.current_task.dict() if self.current_task else None,
            "task_history_count": len(self.task_history),
            "last_task_result": self.task_history[-1].dict() if self.task_history else None
        }


class AgentRegistry:
    """Registry for managing agent instances"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.agent_types: Dict[str, Type[BaseAgent]] = {}
        self.logger = get_logger("AgentRegistry")
    
    def register_agent_type(self, agent_type: str, agent_class: Type[BaseAgent]):
        """Register an agent class"""
        self.agent_types[agent_type] = agent_class
        self.logger.info(f"Registered agent type: {agent_type}")
    
    def create_agent(self, agent_type: str, agent_id: Optional[str] = None) -> BaseAgent:
        """Create a new agent instance"""
        if agent_type not in self.agent_types:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        agent_class = self.agent_types[agent_type]
        agent = agent_class(agent_id=agent_id)
        
        self.agents[agent.agent_id] = agent
        self.logger.info(f"Created agent: {agent.agent_id} of type {agent_type}")
        
        return agent
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get an agent by ID"""
        return self.agents.get(agent_id)
    
    def get_agents_by_type(self, agent_type: str) -> List[BaseAgent]:
        """Get all agents of a specific type"""
        return [
            agent for agent in self.agents.values()
            if agent.get_agent_type() == agent_type
        ]
    
    def remove_agent(self, agent_id: str):
        """Remove an agent from the registry"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            self.logger.info(f"Removed agent: {agent_id}")
    
    def get_all_agents(self) -> List[BaseAgent]:
        """Get all registered agents"""
        return list(self.agents.values())
    
    def get_agent_status_summary(self) -> Dict[str, Any]:
        """Get status summary of all agents"""
        return {
            "total_agents": len(self.agents),
            "agent_types": list(self.agent_types.keys()),
            "agents_by_status": {
                status: len([
                    agent for agent in self.agents.values()
                    if agent.status == status
                ])
                for status in AgentStatus
            },
            "agents": [agent.get_status() for agent in self.agents.values()]
        }


# Global agent registry instance
agent_registry = AgentRegistry()