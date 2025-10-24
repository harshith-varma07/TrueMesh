"""
Federated Publisher Agent - Manages decentralized updates across federated nodes
"""
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import httpx

from app.core.agent_base import BaseAgent, AgentTask, AgentResult, AgentStatus
from app.core.logging import get_logger


class FederatedPublisherAgent(BaseAgent):
    """
    Federated Publisher Agent - Decentralized data synchronization
    
    Responsibilities:
    - Publish updates to federated nodes
    - Synchronize provider data across network
    - Handle node communication
    - Manage sync conflicts
    - Track federation health
    """
    
    def __init__(self, agent_id: Optional[str] = None):
        super().__init__(agent_id)
        self.http_client = None
        self.federation_nodes = self._load_federation_nodes()
        
    def get_agent_type(self) -> str:
        return "federated_publisher"
    
    def _load_federation_nodes(self) -> List[Dict[str, str]]:
        """Load federation nodes from configuration"""
        nodes = []
        for node_url in self.settings.federation_nodes:
            nodes.append({
                "url": node_url,
                "status": "active",
                "last_sync": None,
            })
        return nodes
    
    async def _get_http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client"""
        if self.http_client is None:
            self.http_client = httpx.AsyncClient(timeout=30.0)
        return self.http_client
    
    async def process_task(self, task: AgentTask) -> AgentResult:
        """Process federated publishing task"""
        start_time = datetime.utcnow()
        
        try:
            provider_data = task.data
            operation_type = provider_data.get("operation_type", "update")
            
            # Publish to federation
            publish_results = await self.publish_to_federation(provider_data, operation_type)
            
            # Calculate success rate
            successful_nodes = sum(1 for r in publish_results if r.get("success", False))
            total_nodes = len(publish_results)
            success_rate = successful_nodes / total_nodes if total_nodes > 0 else 0.0
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return AgentResult(
                task_id=task.id,
                agent_id=self.agent_id,
                status=AgentStatus.COMPLETED,
                result={
                    "published": True,
                    "operation_type": operation_type,
                    "nodes_contacted": total_nodes,
                    "successful_publications": successful_nodes,
                    "success_rate": success_rate,
                    "publish_results": publish_results,
                    "published_at": datetime.utcnow().isoformat(),
                },
                execution_time=execution_time,
                metadata={
                    "operation_type": operation_type,
                    "success_rate": success_rate,
                }
            )
            
        except Exception as e:
            self.logger.error(f"Federated publishing failed: {str(e)}", task_id=task.id)
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return AgentResult(
                task_id=task.id,
                agent_id=self.agent_id,
                status=AgentStatus.FAILED,
                error=str(e),
                execution_time=execution_time
            )
    
    async def publish_to_federation(
        self,
        provider_data: Dict[str, Any],
        operation_type: str
    ) -> List[Dict[str, Any]]:
        """Publish data to all federation nodes"""
        if not self.federation_nodes:
            self.logger.info("No federation nodes configured, skipping federation sync")
            return []
        
        self.logger.info(
            "Publishing to federation",
            operation_type=operation_type,
            node_count=len(self.federation_nodes)
        )
        
        # Prepare publication payload
        payload = {
            "operation": operation_type,
            "timestamp": datetime.utcnow().isoformat(),
            "source_node": self.settings.node_id,
            "provider_data": provider_data,
        }
        
        # Publish to all nodes concurrently
        publish_tasks = [
            self._publish_to_node(node, payload)
            for node in self.federation_nodes
        ]
        
        results = await asyncio.gather(*publish_tasks, return_exceptions=True)
        
        # Process results
        publish_results = []
        for i, result in enumerate(results):
            node = self.federation_nodes[i]
            if isinstance(result, Exception):
                publish_results.append({
                    "node_url": node["url"],
                    "success": False,
                    "error": str(result),
                })
            else:
                publish_results.append(result)
        
        return publish_results
    
    async def _publish_to_node(
        self,
        node: Dict[str, str],
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Publish data to a specific federation node"""
        try:
            client = await self._get_http_client()
            
            # In production, this would make actual API call to federation node
            # For now, simulate the publication
            self.logger.info(f"Publishing to node: {node['url']}")
            
            # Simulate API call
            # response = await client.post(
            #     f"{node['url']}/api/v1/federation/sync",
            #     json=payload,
            #     headers={"X-Node-ID": self.settings.node_id}
            # )
            
            # Simulate success
            node["last_sync"] = datetime.utcnow().isoformat()
            
            return {
                "node_url": node["url"],
                "success": True,
                "response": {
                    "status": "synced",
                    "timestamp": datetime.utcnow().isoformat(),
                },
            }
            
        except Exception as e:
            self.logger.error(f"Failed to publish to node {node['url']}: {str(e)}")
            return {
                "node_url": node["url"],
                "success": False,
                "error": str(e),
            }
    
    async def sync_from_federation(self) -> Dict[str, Any]:
        """Pull updates from federation nodes"""
        if not self.federation_nodes:
            return {"synced_updates": [], "message": "No federation nodes configured"}
        
        self.logger.info("Syncing from federation", node_count=len(self.federation_nodes))
        
        sync_tasks = [
            self._sync_from_node(node)
            for node in self.federation_nodes
        ]
        
        results = await asyncio.gather(*sync_tasks, return_exceptions=True)
        
        # Collect all updates
        all_updates = []
        for result in results:
            if isinstance(result, dict) and "updates" in result:
                all_updates.extend(result["updates"])
        
        return {
            "synced_updates": all_updates,
            "update_count": len(all_updates),
            "nodes_synced": len([r for r in results if not isinstance(r, Exception)]),
        }
    
    async def _sync_from_node(self, node: Dict[str, str]) -> Dict[str, Any]:
        """Sync data from a specific federation node"""
        try:
            client = await self._get_http_client()
            
            # In production, make actual API call
            self.logger.info(f"Syncing from node: {node['url']}")
            
            # Simulate sync
            # response = await client.get(
            #     f"{node['url']}/api/v1/federation/updates",
            #     params={"since": node.get("last_sync")},
            #     headers={"X-Node-ID": self.settings.node_id}
            # )
            
            # Simulate response
            return {
                "node_url": node["url"],
                "updates": [],  # Would contain actual updates in production
                "success": True,
            }
            
        except Exception as e:
            self.logger.error(f"Failed to sync from node {node['url']}: {str(e)}")
            return {
                "node_url": node["url"],
                "updates": [],
                "success": False,
                "error": str(e),
            }
    
    def get_federation_status(self) -> Dict[str, Any]:
        """Get current federation network status"""
        active_nodes = [n for n in self.federation_nodes if n.get("status") == "active"]
        
        return {
            "total_nodes": len(self.federation_nodes),
            "active_nodes": len(active_nodes),
            "local_node_id": self.settings.node_id,
            "nodes": [
                {
                    "url": node["url"],
                    "status": node.get("status"),
                    "last_sync": node.get("last_sync"),
                }
                for node in self.federation_nodes
            ],
        }
    
    async def health_check_federation(self) -> Dict[str, Any]:
        """Check health of all federation nodes"""
        if not self.federation_nodes:
            return {"healthy_nodes": 0, "total_nodes": 0}
        
        health_tasks = [
            self._check_node_health(node)
            for node in self.federation_nodes
        ]
        
        results = await asyncio.gather(*health_tasks, return_exceptions=True)
        
        healthy_count = sum(1 for r in results if isinstance(r, dict) and r.get("healthy", False))
        
        return {
            "healthy_nodes": healthy_count,
            "total_nodes": len(self.federation_nodes),
            "health_rate": healthy_count / len(self.federation_nodes),
            "node_health": results,
        }
    
    async def _check_node_health(self, node: Dict[str, str]) -> Dict[str, Any]:
        """Check health of a specific node"""
        try:
            client = await self._get_http_client()
            
            # In production, make actual health check call
            # response = await client.get(
            #     f"{node['url']}/health",
            #     timeout=5.0
            # )
            
            # Simulate health check
            return {
                "node_url": node["url"],
                "healthy": True,
                "response_time": 0.05,
            }
            
        except Exception as e:
            return {
                "node_url": node["url"],
                "healthy": False,
                "error": str(e),
            }
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.http_client:
            await self.http_client.aclose()
