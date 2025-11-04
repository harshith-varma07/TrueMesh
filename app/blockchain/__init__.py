"""
Blockchain module for TrueMesh Provider Intelligence

Complete blockchain implementation for immutable provenance tracking.

Components:
- core.py: Complete blockchain with blocks, Merkle trees, and proof of work
- Transaction: Transaction data structure with hash calculation
- MerkleTree: Merkle tree implementation for transaction verification
- Block: Block structure with mining and validation
- Blockchain: Full blockchain with mining, validation, and chain management
"""

from app.blockchain.core import Block, Blockchain, Transaction, MerkleTree

__all__ = ["Block", "Blockchain", "Transaction", "MerkleTree"]
