"""
Blockchain module initialization

This module will contain blockchain implementation for 
immutable provenance record tracking.

Status: Placeholder - To be implemented

Current implementation is embedded in:
- app/agents/provenance_ledger.py (ProvenanceLedgerAgent)

Future components:
- core.py: Core blockchain logic (Block, Chain, Mining)
- merkle.py: Merkle tree implementation
- consensus.py: Consensus mechanism (PoW, PoS, etc.)
- persistence.py: Chain storage and recovery
- network.py: Blockchain network synchronization
"""

from app.blockchain.core import Block, Blockchain

__all__ = ["Block", "Blockchain"]
