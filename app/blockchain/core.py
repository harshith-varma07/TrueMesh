"""
Blockchain module for TrueMesh Provider Intelligence

Complete blockchain implementation for immutable provenance tracking.
Includes block structure, Merkle trees, proof of work, and chain validation.
"""

import hashlib
import json
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class Transaction:
    """Transaction data structure"""
    transaction_id: str
    transaction_type: str
    provider_id: str
    data: Dict[str, Any]
    timestamp: str
    created_by: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    def calculate_hash(self) -> str:
        """Calculate transaction hash"""
        tx_string = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(tx_string.encode()).hexdigest()


class MerkleTree:
    """Merkle tree implementation for transaction verification"""
    
    @staticmethod
    def calculate_merkle_root(transactions: List[Transaction]) -> str:
        """
        Calculate Merkle root from list of transactions
        
        Args:
            transactions: List of Transaction objects
            
        Returns:
            Merkle root hash as hex string
        """
        if not transactions:
            return hashlib.sha256(b"").hexdigest()
        
        # Get transaction hashes
        hashes = [tx.calculate_hash() for tx in transactions]
        
        # Build Merkle tree
        while len(hashes) > 1:
            # If odd number of hashes, duplicate the last one
            if len(hashes) % 2 != 0:
                hashes.append(hashes[-1])
            
            # Combine pairs of hashes
            hashes = [
                hashlib.sha256((hashes[i] + hashes[i + 1]).encode()).hexdigest()
                for i in range(0, len(hashes), 2)
            ]
        
        return hashes[0]
    
    @staticmethod
    def verify_transaction(
        transaction: Transaction,
        merkle_root: str,
        proof: List[Tuple[str, str]]
    ) -> bool:
        """
        Verify a transaction is part of the Merkle tree
        
        Args:
            transaction: Transaction to verify
            merkle_root: Expected Merkle root
            proof: Merkle proof (list of sibling hashes and positions)
            
        Returns:
            True if transaction is verified
        """
        current_hash = transaction.calculate_hash()
        
        for sibling_hash, position in proof:
            if position == "left":
                current_hash = hashlib.sha256(
                    (sibling_hash + current_hash).encode()
                ).hexdigest()
            else:
                current_hash = hashlib.sha256(
                    (current_hash + sibling_hash).encode()
                ).hexdigest()
        
        return current_hash == merkle_root


class Block:
    """
    Block structure for the blockchain
    
    Contains block header and body with transactions,
    Merkle root calculation, and proof of work.
    """
    
    def __init__(
        self,
        index: int,
        timestamp: str,
        transactions: List[Transaction],
        previous_hash: str,
        nonce: int = 0,
        difficulty: int = 2
    ):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.difficulty = difficulty
        self.merkle_root = MerkleTree.calculate_merkle_root(transactions)
        self.hash = self._calculate_hash()
    
    def _calculate_hash(self) -> str:
        """Calculate SHA-256 hash of the block header"""
        block_header = {
            "index": self.index,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "merkle_root": self.merkle_root,
            "nonce": self.nonce,
            "difficulty": self.difficulty,
            "transaction_count": len(self.transactions)
        }
        block_string = json.dumps(block_header, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def mine_block(self, difficulty: int) -> None:
        """
        Mine block using proof of work
        
        Args:
            difficulty: Number of leading zeros required in hash
        """
        target = "0" * difficulty
        
        while not self.hash.startswith(target):
            self.nonce += 1
            self.hash = self._calculate_hash()
    
    def is_valid(self) -> bool:
        """Verify block hash matches expected pattern"""
        target = "0" * self.difficulty
        return (
            self.hash.startswith(target) and
            self.hash == self._calculate_hash() and
            self.merkle_root == MerkleTree.calculate_merkle_root(self.transactions)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert block to dictionary"""
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "difficulty": self.difficulty,
            "merkle_root": self.merkle_root,
            "hash": self.hash
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Block":
        """Create block from dictionary"""
        transactions = [
            Transaction(**tx) for tx in data["transactions"]
        ]
        block = cls(
            index=data["index"],
            timestamp=data["timestamp"],
            transactions=transactions,
            previous_hash=data["previous_hash"],
            nonce=data["nonce"],
            difficulty=data["difficulty"]
        )
        return block


class Blockchain:
    """
    Complete blockchain implementation with:
    - Genesis block initialization
    - Block mining and validation
    - Chain verification and integrity checks
    - Transaction management
    """
    
    def __init__(self, genesis_hash: str, difficulty: int = 2):
        self.chain: List[Block] = []
        self.genesis_hash = genesis_hash
        self.difficulty = difficulty
        self.pending_transactions: List[Transaction] = []
        self._initialize_genesis_block()
    
    def _initialize_genesis_block(self) -> None:
        """Initialize blockchain with genesis block"""
        genesis_transaction = Transaction(
            transaction_id="genesis",
            transaction_type="genesis",
            provider_id="system",
            data={"message": "TrueMesh Genesis Block"},
            timestamp=datetime.utcnow().isoformat(),
            created_by="system"
        )
        
        genesis_block = Block(
            index=0,
            timestamp=datetime.utcnow().isoformat(),
            transactions=[genesis_transaction],
            previous_hash=self.genesis_hash,
            nonce=0,
            difficulty=self.difficulty
        )
        
        # Mine genesis block
        genesis_block.mine_block(self.difficulty)
        self.chain.append(genesis_block)
    
    def get_latest_block(self) -> Block:
        """Get the most recent block in the chain"""
        return self.chain[-1]
    
    def add_transaction(self, transaction: Transaction) -> None:
        """Add transaction to pending transactions"""
        self.pending_transactions.append(transaction)
    
    def mine_pending_transactions(self, miner_address: str = "system") -> Optional[Block]:
        """
        Mine a new block with pending transactions
        
        Args:
            miner_address: Address of the miner
            
        Returns:
            The newly mined block or None if no pending transactions
        """
        if not self.pending_transactions:
            return None
        
        latest_block = self.get_latest_block()
        
        new_block = Block(
            index=len(self.chain),
            timestamp=datetime.utcnow().isoformat(),
            transactions=self.pending_transactions.copy(),
            previous_hash=latest_block.hash,
            nonce=0,
            difficulty=self.difficulty
        )
        
        # Mine the block
        new_block.mine_block(self.difficulty)
        
        # Add to chain
        self.chain.append(new_block)
        
        # Clear pending transactions
        self.pending_transactions = []
        
        return new_block
    
    def add_block(
        self,
        transactions: List[Transaction],
        mine: bool = True
    ) -> Block:
        """
        Add a new block to the chain
        
        Args:
            transactions: List of transactions for the block
            mine: Whether to mine the block (proof of work)
            
        Returns:
            The newly created block
        """
        latest_block = self.get_latest_block()
        
        new_block = Block(
            index=len(self.chain),
            timestamp=datetime.utcnow().isoformat(),
            transactions=transactions,
            previous_hash=latest_block.hash,
            nonce=0,
            difficulty=self.difficulty
        )
        
        if mine:
            new_block.mine_block(self.difficulty)
        
        self.chain.append(new_block)
        return new_block
    
    def verify_chain(self) -> bool:
        """
        Verify the integrity of the entire blockchain
        
        Returns:
            True if chain is valid, False otherwise
        """
        # Check genesis block
        if not self.chain:
            return False
        
        genesis = self.chain[0]
        if genesis.index != 0 or genesis.previous_hash != self.genesis_hash:
            return False
        
        # Verify each block
        for i in range(len(self.chain)):
            current_block = self.chain[i]
            
            # Verify block itself is valid
            if not current_block.is_valid():
                return False
            
            # Verify chain linkage (except genesis)
            if i > 0:
                previous_block = self.chain[i - 1]
                if current_block.previous_hash != previous_block.hash:
                    return False
        
        return True
    
    def get_block_by_hash(self, block_hash: str) -> Optional[Block]:
        """Find block by hash"""
        for block in self.chain:
            if block.hash == block_hash:
                return block
        return None
    
    def get_block_by_index(self, index: int) -> Optional[Block]:
        """Find block by index"""
        if 0 <= index < len(self.chain):
            return self.chain[index]
        return None
    
    def get_transactions_by_provider(self, provider_id: str) -> List[Transaction]:
        """Get all transactions for a specific provider"""
        transactions = []
        for block in self.chain:
            for tx in block.transactions:
                if tx.provider_id == provider_id:
                    transactions.append(tx)
        return transactions
    
    def get_chain_info(self) -> Dict[str, Any]:
        """Get blockchain statistics and information"""
        total_transactions = sum(len(block.transactions) for block in self.chain)
        
        return {
            "chain_length": len(self.chain),
            "total_transactions": total_transactions,
            "latest_block_hash": self.get_latest_block().hash,
            "latest_block_timestamp": self.get_latest_block().timestamp,
            "genesis_hash": self.genesis_hash,
            "difficulty": self.difficulty,
            "is_valid": self.verify_chain(),
            "pending_transactions": len(self.pending_transactions)
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert blockchain to dictionary"""
        return {
            "genesis_hash": self.genesis_hash,
            "difficulty": self.difficulty,
            "chain": [block.to_dict() for block in self.chain],
            "pending_transactions": [tx.to_dict() for tx in self.pending_transactions]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Blockchain":
        """Create blockchain from dictionary"""
        blockchain = cls(
            genesis_hash=data["genesis_hash"],
            difficulty=data["difficulty"]
        )
        
        # Clear genesis block
        blockchain.chain = []
        
        # Reconstruct chain
        for block_data in data["chain"]:
            block = Block.from_dict(block_data)
            blockchain.chain.append(block)
        
        # Restore pending transactions
        blockchain.pending_transactions = [
            Transaction(**tx) for tx in data["pending_transactions"]
        ]
        
        return blockchain
