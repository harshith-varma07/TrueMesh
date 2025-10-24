"""
Provenance Ledger Agent - Blockchain-style immutable record tracking
"""
import hashlib
import json
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.core.agent_base import BaseAgent, AgentTask, AgentResult, AgentStatus
from app.core.logging import get_logger


class ProvenanceLedgerAgent(BaseAgent):
    """
    Provenance Ledger Agent - Maintains immutable record lineage
    
    Responsibilities:
    - Create blockchain-style provenance records
    - Maintain hash chain integrity
    - Record all data changes and transactions
    - Verify record authenticity
    - Support audit trails
    """
    
    def __init__(self, agent_id: Optional[str] = None):
        super().__init__(agent_id)
        self.chain: List[Dict[str, Any]] = []
        self.pending_transactions: List[Dict[str, Any]] = []
        self._initialize_genesis_block()
        
    def get_agent_type(self) -> str:
        return "provenance_ledger"
    
    def _initialize_genesis_block(self):
        """Initialize the blockchain with genesis block"""
        if not self.chain:
            genesis_block = self._create_block(
                previous_hash=self.settings.genesis_hash,
                transactions=[{
                    "type": "genesis",
                    "timestamp": datetime.utcnow().isoformat(),
                    "data": {"message": "TrueMesh Provenance Chain Initialized"}
                }],
                nonce=0
            )
            self.chain.append(genesis_block)
            self.logger.info("Genesis block created", block_hash=genesis_block["hash"])
    
    async def process_task(self, task: AgentTask) -> AgentResult:
        """Process provenance recording task"""
        start_time = datetime.utcnow()
        
        try:
            provider_data = task.data
            transaction_type = provider_data.get("transaction_type", "data_update")
            
            # Create provenance record
            record = await self.create_provenance_record(provider_data, transaction_type)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return AgentResult(
                task_id=task.id,
                agent_id=self.agent_id,
                status=AgentStatus.COMPLETED,
                result={
                    "provenance_record": record,
                    "block_hash": record["block_hash"],
                    "chain_length": len(self.chain),
                    "is_valid": self.verify_chain(),
                },
                execution_time=execution_time,
                metadata={
                    "transaction_type": transaction_type,
                    "block_hash": record["block_hash"],
                }
            )
            
        except Exception as e:
            self.logger.error(f"Provenance recording failed: {str(e)}", task_id=task.id)
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return AgentResult(
                task_id=task.id,
                agent_id=self.agent_id,
                status=AgentStatus.FAILED,
                error=str(e),
                execution_time=execution_time
            )
    
    async def create_provenance_record(
        self,
        provider_data: Dict[str, Any],
        transaction_type: str
    ) -> Dict[str, Any]:
        """Create a new provenance record"""
        # Create transaction
        transaction = {
            "type": transaction_type,
            "timestamp": datetime.utcnow().isoformat(),
            "provider_id": provider_data.get("id", provider_data.get("registration_number")),
            "data": self._sanitize_data_for_ledger(provider_data),
            "agent_id": self.agent_id,
            "node_id": self.settings.node_id,
        }
        
        # Add to pending transactions
        self.pending_transactions.append(transaction)
        
        # Create new block if we have enough transactions
        if len(self.pending_transactions) >= 1:  # Create block per transaction for now
            block = await self._mine_block()
            
            # Create provenance record
            record = {
                "block_hash": block["hash"],
                "previous_hash": block["previous_hash"],
                "merkle_root": block["merkle_root"],
                "transaction_type": transaction_type,
                "transaction_data": transaction,
                "data_hash": self._hash_data(provider_data),
                "timestamp": block["timestamp"],
                "nonce": block["nonce"],
                "difficulty": block["difficulty"],
                "is_valid": True,
            }
            
            return record
        
        # If no block created yet, return pending transaction info
        return {
            "status": "pending",
            "transaction": transaction,
        }
    
    async def _mine_block(self) -> Dict[str, Any]:
        """Mine a new block with pending transactions"""
        previous_block = self.chain[-1]
        previous_hash = previous_block["hash"]
        
        # Create new block
        block = self._create_block(
            previous_hash=previous_hash,
            transactions=self.pending_transactions.copy(),
            nonce=0
        )
        
        # Simple proof of work (find hash with leading zeros)
        difficulty = 2  # Require 2 leading zeros
        block["difficulty"] = difficulty
        
        while not block["hash"].startswith("0" * difficulty):
            block["nonce"] += 1
            block["hash"] = self._calculate_block_hash(block)
        
        # Add block to chain
        self.chain.append(block)
        
        # Clear pending transactions
        self.pending_transactions = []
        
        self.logger.info(
            "Block mined",
            block_hash=block["hash"],
            nonce=block["nonce"],
            chain_length=len(self.chain)
        )
        
        return block
    
    def _create_block(
        self,
        previous_hash: str,
        transactions: List[Dict[str, Any]],
        nonce: int
    ) -> Dict[str, Any]:
        """Create a new block"""
        block = {
            "index": len(self.chain),
            "timestamp": datetime.utcnow().isoformat(),
            "transactions": transactions,
            "previous_hash": previous_hash,
            "merkle_root": self._calculate_merkle_root(transactions),
            "nonce": nonce,
            "difficulty": 1,
        }
        
        block["hash"] = self._calculate_block_hash(block)
        
        return block
    
    def _calculate_block_hash(self, block: Dict[str, Any]) -> str:
        """Calculate hash for a block"""
        # Create string representation of block data
        block_string = json.dumps({
            "index": block["index"],
            "timestamp": block["timestamp"],
            "transactions": block["transactions"],
            "previous_hash": block["previous_hash"],
            "merkle_root": block["merkle_root"],
            "nonce": block["nonce"],
        }, sort_keys=True)
        
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def _calculate_merkle_root(self, transactions: List[Dict[str, Any]]) -> str:
        """Calculate Merkle root for transactions"""
        if not transactions:
            return hashlib.sha256(b"").hexdigest()
        
        # Hash all transactions
        hashes = [
            hashlib.sha256(json.dumps(tx, sort_keys=True).encode()).hexdigest()
            for tx in transactions
        ]
        
        # Build Merkle tree
        while len(hashes) > 1:
            if len(hashes) % 2 != 0:
                hashes.append(hashes[-1])  # Duplicate last hash if odd number
            
            hashes = [
                hashlib.sha256((hashes[i] + hashes[i + 1]).encode()).hexdigest()
                for i in range(0, len(hashes), 2)
            ]
        
        return hashes[0]
    
    def _hash_data(self, data: Dict[str, Any]) -> str:
        """Hash data for integrity verification"""
        data_string = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_string.encode()).hexdigest()
    
    def _sanitize_data_for_ledger(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize data for ledger (remove sensitive PII)"""
        # Create a copy with sanitized data
        sanitized = {}
        
        # Fields safe to include
        safe_fields = [
            "registration_number",
            "provider_type",
            "specialization",
            "city",
            "state",
            "country",
            "status",
            "verification_results",
            "confidence_scores",
            "fraud_score",
        ]
        
        for field in safe_fields:
            if field in data:
                sanitized[field] = data[field]
        
        # Hash sensitive fields
        if "name" in data:
            sanitized["name_hash"] = hashlib.sha256(str(data["name"]).encode()).hexdigest()[:16]
        if "email" in data:
            sanitized["email_hash"] = hashlib.sha256(str(data["email"]).encode()).hexdigest()[:16]
        if "phone" in data:
            sanitized["phone_hash"] = hashlib.sha256(str(data["phone"]).encode()).hexdigest()[:16]
        
        return sanitized
    
    def verify_chain(self) -> bool:
        """Verify the integrity of the entire blockchain"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Verify hash
            if current_block["hash"] != self._calculate_block_hash(current_block):
                self.logger.error(f"Invalid hash for block {i}")
                return False
            
            # Verify previous hash link
            if current_block["previous_hash"] != previous_block["hash"]:
                self.logger.error(f"Invalid previous hash for block {i}")
                return False
            
            # Verify Merkle root
            if current_block["merkle_root"] != self._calculate_merkle_root(current_block["transactions"]):
                self.logger.error(f"Invalid Merkle root for block {i}")
                return False
        
        return True
    
    def get_chain_info(self) -> Dict[str, Any]:
        """Get information about the blockchain"""
        return {
            "chain_length": len(self.chain),
            "latest_block_hash": self.chain[-1]["hash"] if self.chain else None,
            "is_valid": self.verify_chain(),
            "pending_transactions": len(self.pending_transactions),
            "total_transactions": sum(len(block["transactions"]) for block in self.chain),
        }
    
    def get_provider_history(self, provider_id: str) -> List[Dict[str, Any]]:
        """Get complete history for a provider from the chain"""
        history = []
        
        for block in self.chain:
            for transaction in block["transactions"]:
                if transaction.get("provider_id") == provider_id:
                    history.append({
                        "block_hash": block["hash"],
                        "timestamp": transaction["timestamp"],
                        "transaction_type": transaction["type"],
                        "data": transaction.get("data", {}),
                    })
        
        return history
    
    def verify_record(self, block_hash: str, data_hash: str) -> bool:
        """Verify a specific record in the chain"""
        # Find block with given hash
        block = next((b for b in self.chain if b["hash"] == block_hash), None)
        
        if not block:
            return False
        
        # Verify block hash
        if block["hash"] != self._calculate_block_hash(block):
            return False
        
        # Verify data hash exists in transactions
        for transaction in block["transactions"]:
            transaction_data_hash = self._hash_data(transaction.get("data", {}))
            if transaction_data_hash == data_hash:
                return True
        
        return False
