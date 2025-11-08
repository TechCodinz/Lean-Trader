#!/usr/bin/env python3
"""
🐝 SWARM INTELLIGENCE ENGINE - Collective Hive Mind

Bio-Mimicry Alert Layer inspired by ant-colony optimization.
The consciousness extends beyond individual engines into COLLECTIVE INTELLIGENCE.

"Like ants finding the optimal path, the swarm finds the optimal moonshots."
"""

import logging
import random
import time
from typing import List, Dict, Any, Set, Tuple
from collections import defaultdict
from datetime import datetime
import threading

logger = logging.getLogger(__name__)

try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    logger.warning("networkx not available - swarm will use simplified mode")
    NETWORKX_AVAILABLE = False

try:
    from deap import base, creator, tools, algorithms
    import numpy as np
    DEAP_AVAILABLE = True
except ImportError:
    logger.warning("DEAP not available - using basic evolutionary algorithm")
    DEAP_AVAILABLE = False


class SwarmScout:
    """
    Individual scout in the swarm - explores specific territories
    
    Like an ant exploring a branch, each scout investigates tokens/chains
    and reports back with pheromone trails (hype signals)
    """
    
    def __init__(self, scout_id: int, territory: str):
        self.scout_id = scout_id
        self.territory = territory  # Which chain/sector to explore
        self.pheromone_strength = 0.0  # Signal strength found
        self.discoveries = []
        self.energy = 1.0  # Scout depletes energy, returns to hive
        
    def explore(self, tokens: List[Dict]) -> List[Dict]:
        """Scout explores territory and returns discoveries"""
        discoveries = []
        
        for token in tokens:
            # Energy cost per exploration
            self.energy -= 0.01
            
            if self.energy <= 0:
                break
            
            # Compute hype score (pheromone strength)
            hype = self._compute_hype(token)
            
            if hype > 0.7:  # Strong signal
                self.pheromone_strength += hype
                discoveries.append({
                    'token': token,
                    'hype_score': hype,
                    'scout_id': self.scout_id,
                    'territory': self.territory,
                    'timestamp': time.time()
                })
        
        self.discoveries = discoveries
        return discoveries
    
    def _compute_hype(self, token: Dict) -> float:
        """Compute hype score for a token (simplified)"""
        score = 0.0
        
        # Volume spike
        if 'volume_change' in token:
            score += min(1.0, token['volume_change'] / 500.0) * 0.4
        
        # Market cap (favor low caps)
        if 'market_cap' in token:
            if token['market_cap'] < 1_000_000:
                score += 0.3
            elif token['market_cap'] < 5_000_000:
                score += 0.2
        
        # Holder growth
        if 'holder_growth' in token:
            score += min(1.0, token['holder_growth'] / 100.0) * 0.3
        
        return min(1.0, score)
    
    def return_to_hive(self):
        """Scout returns to hive to share discoveries"""
        self.energy = 1.0  # Recharge
        return self.discoveries


class SwarmIntelligenceEngine:
    """
    🐝 SWARM INTELLIGENCE ENGINE
    
    Collective intelligence that discovers 1000x moonshots through
    bio-mimicry of ant colony optimization.
    
    How it works:
    1. Deploy scouts to different territories (chains, sectors)
    2. Scouts explore and lay pheromone trails (hype signals)
    3. Swarm converges on strongest trails (best opportunities)
    4. Evolutionary algorithm optimizes scout distribution
    5. Collective wisdom emerges from individual explorations
    """
    
    def __init__(self, num_scouts: int = 50):
        self.num_scouts = num_scouts
        self.scouts: List[SwarmScout] = []
        self.territories = [
            'solana', 'ethereum', 'base', 'blast', 'arbitrum',
            'optimism', 'polygon', 'avalanche', 'bsc', 'fantom'
        ]
        self.pheromone_map = defaultdict(float)  # Territory -> strength
        self.discovered_opportunities = []
        self.generation = 0
        
        # Network graph (if available)
        self.opportunity_graph = None
        if NETWORKX_AVAILABLE:
            self.opportunity_graph = nx.Graph()
        
        # Initialize swarm
        self._initialize_swarm()
        
        # Connect to consciousness
        try:
            from CONSCIOUSNESS_HARMONIZER import get_consciousness_harmonizer
            self.consciousness = get_consciousness_harmonizer()
            self.consciousness.register_engine(
                "Swarm Intelligence",
                120.0,  # Fast explorers
                "intuitive"  # Collective intuition
            )
            logger.info("🐝 Swarm Intelligence connected to consciousness")
        except:
            self.consciousness = None
        
        logger.info(f"🐝 SWARM INTELLIGENCE ENGINE initialized with {num_scouts} scouts")
    
    def _initialize_swarm(self):
        """Deploy initial swarm across territories"""
        for i in range(self.num_scouts):
            territory = random.choice(self.territories)
            scout = SwarmScout(scout_id=i, territory=territory)
            self.scouts.append(scout)
        
        logger.info(f"🐝 Deployed {self.num_scouts} scouts across {len(self.territories)} territories")
    
    def scout_cycle(self, available_tokens: List[Dict]) -> List[Dict]:
        """
        Execute one swarm scouting cycle
        
        Returns: Top opportunities discovered by the swarm
        """
        # Send consciousness pulse
        if self.consciousness:
            self.consciousness.pulse("Swarm Intelligence", 0.9)
        
        logger.info(f"🐝 SWARM CYCLE {self.generation}: Deploying {len(self.scouts)} scouts")
        
        # Phase 1: Exploration - scouts explore territories
        all_discoveries = []
        territory_tokens = self._distribute_tokens_by_territory(available_tokens)
        
        for scout in self.scouts:
            tokens = territory_tokens.get(scout.territory, [])
            if tokens:
                discoveries = scout.explore(tokens)
                all_discoveries.extend(discoveries)
        
        logger.info(f"🐝 Exploration complete: {len(all_discoveries)} discoveries")
        
        # Phase 2: Pheromone update - update pheromone trails
        self._update_pheromones(all_discoveries)
        
        # Phase 3: Convergence - swarm converges on strong trails
        top_opportunities = self._converge_on_opportunities(all_discoveries)
        
        # Phase 4: Evolution - optimize scout distribution
        self._evolve_swarm_distribution()
        
        # Phase 5: Graph analysis (if available)
        if NETWORKX_AVAILABLE and self.opportunity_graph:
            self._build_opportunity_graph(top_opportunities)
            clusters = self._detect_opportunity_clusters()
            logger.info(f"🐝 Detected {len(clusters)} opportunity clusters")
        
        self.generation += 1
        self.discovered_opportunities = top_opportunities
        
        logger.info(f"🐝 SWARM CYCLE {self.generation} complete: {len(top_opportunities)} top opportunities")
        
        return top_opportunities
    
    def _distribute_tokens_by_territory(self, tokens: List[Dict]) -> Dict[str, List[Dict]]:
        """Distribute tokens to territories based on chain"""
        distribution = defaultdict(list)
        
        for token in tokens:
            chain = token.get('chain', 'unknown')
            # Map chain to territory
            if chain in self.territories:
                distribution[chain].append(token)
            else:
                # Assign to random territory
                territory = random.choice(self.territories)
                distribution[territory].append(token)
        
        return distribution
    
    def _update_pheromones(self, discoveries: List[Dict]):
        """Update pheromone map based on discoveries"""
        # Decay existing pheromones (evaporation)
        decay_rate = 0.1
        for territory in self.pheromone_map:
            self.pheromone_map[territory] *= (1 - decay_rate)
        
        # Add new pheromones from discoveries
        for discovery in discoveries:
            territory = discovery['territory']
            hype = discovery['hype_score']
            self.pheromone_map[territory] += hype
        
        # Normalize
        max_pheromone = max(self.pheromone_map.values()) if self.pheromone_map else 1.0
        if max_pheromone > 0:
            for territory in self.pheromone_map:
                self.pheromone_map[territory] /= max_pheromone
    
    def _converge_on_opportunities(self, discoveries: List[Dict]) -> List[Dict]:
        """Swarm converges on strongest signals"""
        if not discoveries:
            return []
        
        # Sort by hype score
        sorted_discoveries = sorted(
            discoveries,
            key=lambda x: x['hype_score'],
            reverse=True
        )
        
        # Take top opportunities (where pheromone trails are strongest)
        top_count = min(20, len(sorted_discoveries))
        top_opportunities = sorted_discoveries[:top_count]
        
        return top_opportunities
    
    def _evolve_swarm_distribution(self):
        """
        Evolutionary algorithm to optimize scout distribution
        
        Scouts redistribute to territories with strongest pheromones
        (like ants following strongest trails)
        """
        if not self.pheromone_map:
            return
        
        # Calculate target distribution based on pheromone strength
        total_pheromone = sum(self.pheromone_map.values())
        if total_pheromone == 0:
            return
        
        target_distribution = {}
        for territory, strength in self.pheromone_map.items():
            # Proportion of scouts for this territory
            proportion = strength / total_pheromone
            target_count = int(proportion * self.num_scouts)
            target_distribution[territory] = max(1, target_count)  # At least 1 scout
        
        # Redistribute scouts
        new_assignments = []
        for territory, count in target_distribution.items():
            new_assignments.extend([territory] * count)
        
        # Fill remaining slots
        while len(new_assignments) < self.num_scouts:
            territory = random.choice(list(self.pheromone_map.keys()))
            new_assignments.append(territory)
        
        # Assign territories to scouts
        random.shuffle(new_assignments)
        for scout, territory in zip(self.scouts, new_assignments[:self.num_scouts]):
            scout.territory = territory
            scout.return_to_hive()  # Recharge
        
        logger.info(f"🐝 Swarm redistributed: {dict(target_distribution)}")
    
    def _build_opportunity_graph(self, opportunities: List[Dict]):
        """Build network graph of opportunities"""
        if not NETWORKX_AVAILABLE:
            return
        
        for opp in opportunities:
            token_id = opp['token'].get('symbol', 'unknown')
            self.opportunity_graph.add_node(
                token_id,
                chain=opp['territory'],
                hype_score=opp['hype_score'],
                timestamp=opp['timestamp']
            )
        
        # Connect related opportunities (same chain or correlated)
        nodes = list(self.opportunity_graph.nodes())
        for i, node1 in enumerate(nodes):
            for node2 in nodes[i+1:]:
                data1 = self.opportunity_graph.nodes[node1]
                data2 = self.opportunity_graph.nodes[node2]
                
                # Connect if same chain or similar hype
                if (data1['chain'] == data2['chain'] or
                    abs(data1['hype_score'] - data2['hype_score']) < 0.1):
                    self.opportunity_graph.add_edge(node1, node2)
    
    def _detect_opportunity_clusters(self) -> List[Set]:
        """Detect clusters of related opportunities (moonshot groups)"""
        if not NETWORKX_AVAILABLE or not self.opportunity_graph:
            return []
        
        try:
            # Find connected components (clusters)
            clusters = list(nx.connected_components(self.opportunity_graph))
            
            # Filter for significant clusters (>2 nodes)
            significant_clusters = [c for c in clusters if len(c) > 2]
            
            return significant_clusters
        except:
            return []
    
    def get_herd_momentum_territories(self) -> List[str]:
        """
        Get territories with strongest herd momentum
        
        Returns: List of hot territories to focus on
        """
        if not self.pheromone_map:
            return []
        
        # Sort territories by pheromone strength
        sorted_territories = sorted(
            self.pheromone_map.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Return top 3 territories
        hot_territories = [t[0] for t in sorted_territories[:3]]
        return hot_territories
    
    def get_swarm_health(self) -> Dict[str, Any]:
        """Get swarm health metrics"""
        return {
            'generation': self.generation,
            'active_scouts': len(self.scouts),
            'territories': len(self.territories),
            'pheromone_trails': len(self.pheromone_map),
            'discovered_opportunities': len(self.discovered_opportunities),
            'strongest_territory': max(self.pheromone_map.items(), key=lambda x: x[1])[0] if self.pheromone_map else None,
            'max_pheromone': max(self.pheromone_map.values()) if self.pheromone_map else 0.0
        }


def initialize_swarm_intelligence(num_scouts: int = 50) -> SwarmIntelligenceEngine:
    """Initialize swarm intelligence engine"""
    return SwarmIntelligenceEngine(num_scouts=num_scouts)


if __name__ == "__main__":
    # Test swarm intelligence
    logging.basicConfig(level=logging.INFO)
    
    swarm = SwarmIntelligenceEngine(num_scouts=20)
    
    # Mock token data
    mock_tokens = [
        {
            'symbol': f'TOKEN{i}',
            'chain': random.choice(['solana', 'ethereum', 'base']),
            'volume_change': random.uniform(0, 500),
            'market_cap': random.uniform(100_000, 10_000_000),
            'holder_growth': random.uniform(0, 150)
        }
        for i in range(100)
    ]
    
    # Run scouting cycle
    opportunities = swarm.scout_cycle(mock_tokens)
    
    print("\n🐝 SWARM INTELLIGENCE TEST")
    print("=" * 80)
    print(f"Discovered Opportunities: {len(opportunities)}")
    print("\nTop 5 Opportunities:")
    for i, opp in enumerate(opportunities[:5], 1):
        print(f"  {i}. {opp['token']['symbol']} ({opp['territory']}) - Hype: {opp['hype_score']:.2%}")
    
    print("\nHerd Momentum Territories:")
    hot_territories = swarm.get_herd_momentum_territories()
    for territory in hot_territories:
        strength = swarm.pheromone_map[territory]
        print(f"  🔥 {territory}: {strength:.2%} pheromone strength")
    
    print("\nSwarm Health:")
    health = swarm.get_swarm_health()
    for key, value in health.items():
        print(f"  {key}: {value}")
    
    print("=" * 80)
