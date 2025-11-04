"""
Entity Resolution Agent - Deduplication and entity matching using fuzzy logic
"""
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import hashlib
from collections import defaultdict

# Fuzzy matching and similarity
from difflib import SequenceMatcher
import re

from app.core.agent_base import BaseAgent, AgentTask, AgentResult, AgentStatus
from app.core.logging import get_logger


class EntityResolutionAgent(BaseAgent):
    """
    Entity Resolution Agent - Record linkage and deduplication
    
    Responsibilities:
    - Identify duplicate provider records across sources
    - Fuzzy matching on names, addresses, registration numbers
    - Graph-based clustering of related entities
    - Assign canonical identifiers to entity groups
    - TF-IDF and Levenshtein distance for similarity
    """
    
    def __init__(self, agent_id: Optional[str] = None):
        super().__init__(agent_id)
        self.similarity_threshold = 0.85  # 85% similarity threshold
        self.entity_graph = defaultdict(set)  # Graph of related entities
        
    def get_agent_type(self) -> str:
        return "entity_resolution"
    
    async def process_task(self, task: AgentTask) -> AgentResult:
        """Process entity resolution task"""
        start_time = datetime.utcnow()
        
        try:
            provider_data = task.data
            providers_list = provider_data.get("providers", [])
            
            if not providers_list:
                raise ValueError("providers list is required")
            
            # Perform entity resolution
            resolution_results = await self.resolve_entities(providers_list)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return AgentResult(
                task_id=task.id,
                agent_id=self.agent_id,
                status=AgentStatus.COMPLETED,
                result={
                    "canonical_entities": resolution_results["canonical_entities"],
                    "duplicate_groups": resolution_results["duplicate_groups"],
                    "entity_count": resolution_results["entity_count"],
                    "duplicate_count": resolution_results["duplicate_count"],
                    "resolution_stats": resolution_results["stats"],
                },
                execution_time=execution_time,
                metadata={
                    "input_count": len(providers_list),
                    "resolved_at": datetime.utcnow().isoformat(),
                }
            )
            
        except Exception as e:
            self.logger.error(f"Entity resolution failed: {str(e)}", task_id=task.id)
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return AgentResult(
                task_id=task.id,
                agent_id=self.agent_id,
                status=AgentStatus.FAILED,
                result={},
                error=str(e),
                execution_time=execution_time
            )
    
    async def resolve_entities(self, providers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Resolve entities using fuzzy matching and clustering
        """
        # Step 1: Normalize all provider records
        normalized_providers = [self._normalize_provider(p) for p in providers]
        
        # Step 2: Build similarity matrix and identify duplicates
        duplicate_groups = []
        processed = set()
        canonical_entities = []
        
        for i, provider_a in enumerate(normalized_providers):
            if i in processed:
                continue
                
            # Find all similar providers
            group = [i]
            for j, provider_b in enumerate(normalized_providers):
                if i != j and j not in processed:
                    similarity = self._calculate_similarity(provider_a, provider_b)
                    if similarity >= self.similarity_threshold:
                        group.append(j)
                        processed.add(j)
            
            # Mark this group as processed
            processed.add(i)
            
            # Create canonical entity for this group
            canonical = self._create_canonical_entity(
                [normalized_providers[idx] for idx in group],
                [providers[idx] for idx in group]
            )
            canonical_entities.append(canonical)
            
            if len(group) > 1:
                duplicate_groups.append({
                    "canonical_id": canonical["canonical_id"],
                    "members": [providers[idx].get("id") or idx for idx in group],
                    "member_count": len(group),
                })
        
        # Step 3: Build entity graph for relationships
        await self._build_entity_graph(canonical_entities)
        
        return {
            "canonical_entities": canonical_entities,
            "duplicate_groups": duplicate_groups,
            "entity_count": len(canonical_entities),
            "duplicate_count": len(duplicate_groups),
            "stats": {
                "input_records": len(providers),
                "unique_entities": len(canonical_entities),
                "duplicate_groups": len(duplicate_groups),
                "deduplication_rate": 1 - (len(canonical_entities) / len(providers)) if providers else 0,
            }
        }
    
    def _normalize_provider(self, provider: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize provider data for comparison"""
        return {
            "name": self._normalize_text(provider.get("name", "")),
            "registration_number": self._normalize_text(provider.get("registration_number", "")),
            "email": self._normalize_text(provider.get("email", "")),
            "phone": self._normalize_phone(provider.get("phone", "")),
            "address": self._normalize_text(
                f"{provider.get('address_line1', '')} {provider.get('city', '')} {provider.get('state', '')}"
            ),
            "provider_type": provider.get("provider_type", "").lower(),
            "original": provider,
        }
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison"""
        if not text:
            return ""
        # Convert to lowercase, remove extra spaces, special chars
        text = text.lower().strip()
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text
    
    def _normalize_phone(self, phone: str) -> str:
        """Normalize phone number"""
        if not phone:
            return ""
        # Remove all non-digits
        digits = re.sub(r'\D', '', phone)
        # Keep last 10 digits for Indian numbers
        return digits[-10:] if len(digits) >= 10 else digits
    
    def _calculate_similarity(self, provider_a: Dict, provider_b: Dict) -> float:
        """
        Calculate overall similarity between two providers
        Uses weighted combination of different fields
        """
        weights = {
            "name": 0.35,
            "registration_number": 0.30,
            "phone": 0.15,
            "email": 0.10,
            "address": 0.10,
        }
        
        total_score = 0.0
        total_weight = 0.0
        
        for field, weight in weights.items():
            val_a = provider_a.get(field, "")
            val_b = provider_b.get(field, "")
            
            if val_a and val_b:
                # Calculate field similarity using Levenshtein-like ratio
                similarity = self._levenshtein_ratio(val_a, val_b)
                total_score += similarity * weight
                total_weight += weight
        
        # Normalize by actual weights used
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def _levenshtein_ratio(self, s1: str, s2: str) -> float:
        """Calculate Levenshtein similarity ratio (0-1)"""
        if not s1 or not s2:
            return 0.0
        return SequenceMatcher(None, s1, s2).ratio()
    
    def _create_canonical_entity(
        self, 
        normalized_group: List[Dict], 
        original_group: List[Dict]
    ) -> Dict[str, Any]:
        """
        Create canonical entity from group of similar providers
        Uses voting/consensus for each field
        """
        # Generate canonical ID from group
        canonical_id = self._generate_canonical_id(original_group)
        
        # Select best values for each field (most common, longest, etc.)
        canonical = {
            "canonical_id": canonical_id,
            "name": self._select_best_value([p.get("name") for p in original_group]),
            "registration_number": self._select_best_value([p.get("registration_number") for p in original_group]),
            "provider_type": self._select_most_common([p.get("provider_type") for p in original_group]),
            "email": self._select_best_value([p.get("email") for p in original_group]),
            "phone": self._select_best_value([p.get("phone") for p in original_group]),
            "address_line1": self._select_best_value([p.get("address_line1") for p in original_group]),
            "city": self._select_best_value([p.get("city") for p in original_group]),
            "state": self._select_best_value([p.get("state") for p in original_group]),
            "postal_code": self._select_best_value([p.get("postal_code") for p in original_group]),
            "member_count": len(original_group),
            "member_ids": [p.get("id") for p in original_group if p.get("id")],
            "sources": list(set([p.get("source", "unknown") for p in original_group])),
            "resolved_at": datetime.utcnow().isoformat(),
        }
        
        return canonical
    
    def _generate_canonical_id(self, group: List[Dict]) -> str:
        """Generate unique canonical ID for entity group"""
        # Use hash of sorted registration numbers or names
        identifiers = sorted([
            p.get("registration_number") or p.get("name", "")
            for p in group
        ])
        identifier_str = "|".join(identifiers)
        return f"ENT-{hashlib.sha256(identifier_str.encode()).hexdigest()[:12].upper()}"
    
    def _select_best_value(self, values: List[Any]) -> Optional[str]:
        """Select best value from list (longest non-empty)"""
        valid_values = [v for v in values if v]
        if not valid_values:
            return None
        # Return longest value as it's likely most complete
        return max(valid_values, key=lambda x: len(str(x)))
    
    def _select_most_common(self, values: List[Any]) -> Optional[str]:
        """Select most common value from list"""
        valid_values = [v for v in values if v]
        if not valid_values:
            return None
        # Count occurrences and return most common
        from collections import Counter
        counter = Counter(valid_values)
        return counter.most_common(1)[0][0]
    
    async def _build_entity_graph(self, entities: List[Dict]) -> None:
        """Build graph of related entities for clustering"""
        # Build graph based on shared attributes (same city, same type, etc.)
        for i, entity_a in enumerate(entities):
            for j, entity_b in enumerate(entities):
                if i < j:
                    # Check for relationships
                    if self._are_related(entity_a, entity_b):
                        self.entity_graph[entity_a["canonical_id"]].add(entity_b["canonical_id"])
                        self.entity_graph[entity_b["canonical_id"]].add(entity_a["canonical_id"])
    
    def _are_related(self, entity_a: Dict, entity_b: Dict) -> bool:
        """Check if two entities are related (same location, type, etc.)"""
        # Same city and provider type
        if (entity_a.get("city") == entity_b.get("city") and 
            entity_a.get("provider_type") == entity_b.get("provider_type") and
            entity_a.get("city")):
            return True
        
        # Same postal code
        if entity_a.get("postal_code") == entity_b.get("postal_code") and entity_a.get("postal_code"):
            return True
        
        return False
