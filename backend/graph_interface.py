"""
Unified Graph Interface

Provides a consistent interface for both NetworkX (in-memory) and Neo4j (persistent) graphs.
"""

from typing import Dict, List, Any, Optional, Tuple
from abc import ABC, abstractmethod
import networkx as nx
import json


class GraphInterface(ABC):
    """Abstract interface for graph storage backends"""
    
    @abstractmethod
    def add_node(self, node_id: str, **properties):
        """Add a node to the graph"""
        pass
    
    @abstractmethod
    def add_edge(self, source: str, target: str, relationship_type: str = "RELATES_TO", **properties):
        """Add an edge between two nodes"""
        pass
    
    @abstractmethod
    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get node by ID"""
        pass
    
    @abstractmethod
    def get_neighbors(self, node_id: str, relationship_type: Optional[str] = None) -> List[str]:
        """Get neighboring node IDs"""
        pass
    
    @abstractmethod
    def number_of_nodes(self) -> int:
        """Get total number of nodes"""
        pass
    
    @abstractmethod
    def number_of_edges(self) -> int:
        """Get total number of edges"""
        pass
    
    @abstractmethod
    def get_graph_data(self, limit: int = 1000) -> Dict[str, Any]:
        """Export graph data for visualization"""
        pass
    
    @abstractmethod
    def find_nodes_by_type(self, node_type: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Find nodes by type"""
        pass
    
    @abstractmethod
    def find_nodes_by_property(self, property_name: str, property_value: Any, limit: int = 100) -> List[Dict[str, Any]]:
        """Find nodes by property value"""
        pass


class NetworkXAdapter(GraphInterface):
    """NetworkX in-memory graph adapter"""
    
    def __init__(self, graph: nx.MultiDiGraph = None):
        self.graph = graph or nx.MultiDiGraph()
    
    def add_node(self, node_id: str, **properties):
        self.graph.add_node(node_id, **properties)
    
    def add_edge(self, source: str, target: str, relationship_type: str = "RELATES_TO", **properties):
        self.graph.add_edge(source, target, label=relationship_type, **properties)
    
    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        if node_id in self.graph:
            return dict(self.graph.nodes[node_id])
        return None
    
    def get_neighbors(self, node_id: str, relationship_type: Optional[str] = None) -> List[str]:
        if node_id not in self.graph:
            return []
        
        neighbors = list(self.graph.neighbors(node_id))
        
        if relationship_type:
            # Filter by edge type
            filtered = []
            for neighbor in neighbors:
                for _, _, data in self.graph.edges(node_id, neighbor, data=True):
                    if data.get('label') == relationship_type:
                        filtered.append(neighbor)
                        break
            return filtered
        
        return neighbors
    
    def number_of_nodes(self) -> int:
        return self.graph.number_of_nodes()
    
    def number_of_edges(self) -> int:
        return self.graph.number_of_edges()
    
    def get_graph_data(self, limit: int = 1000) -> Dict[str, Any]:
        """Export graph data for visualization"""
        nodes = []
        for node_id, data in list(self.graph.nodes(data=True))[:limit]:
            nodes.append({
                'id': node_id,
                'label': data.get('label', node_id),
                'type': data.get('type', 'Generic')
            })
        
        node_ids = {n['id'] for n in nodes}
        edges = []
        for source, target, data in self.graph.edges(data=True):
            if source in node_ids and target in node_ids:
                edges.append({
                    'source': source,
                    'target': target,
                    'label': data.get('label', 'relates_to')
                })
        
        return {
            'nodes': nodes,
            'edges': edges
        }
    
    def find_nodes_by_type(self, node_type: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Find nodes by type"""
        nodes = []
        for node_id, data in self.graph.nodes(data=True):
            if data.get('type') == node_type:
                node_data = dict(data)
                node_data['id'] = node_id
                nodes.append(node_data)
                if len(nodes) >= limit:
                    break
        return nodes
    
    def find_nodes_by_property(self, property_name: str, property_value: Any, limit: int = 100) -> List[Dict[str, Any]]:
        """Find nodes by property value"""
        nodes = []
        for node_id, data in self.graph.nodes(data=True):
            if data.get(property_name) == property_value:
                node_data = dict(data)
                node_data['id'] = node_id
                nodes.append(node_data)
                if len(nodes) >= limit:
                    break
        return nodes
    
    def get_subgraph(self, node_id: str, depth: int = 2) -> Tuple[List[Dict], List[Dict]]:
        """Get subgraph around a node"""
        if node_id not in self.graph:
            return [], []
        
        # BFS to get nodes within depth
        visited = {node_id}
        current_level = {node_id}
        
        for _ in range(depth):
            next_level = set()
            for node in current_level:
                neighbors = set(self.graph.neighbors(node)) | set(self.graph.predecessors(node))
                next_level.update(neighbors - visited)
            visited.update(next_level)
            current_level = next_level
        
        # Get nodes
        nodes = []
        for nid in visited:
            node_data = dict(self.graph.nodes[nid])
            node_data['id'] = nid
            nodes.append(node_data)
        
        # Get edges
        edges = []
        for source, target, data in self.graph.edges(data=True):
            if source in visited and target in visited:
                edges.append({
                    'source': source,
                    'target': target,
                    'type': data.get('label', 'relates_to'),
                    'properties': data
                })
        
        return nodes, edges
    
    def get_raw_graph(self) -> nx.MultiDiGraph:
        """Get the underlying NetworkX graph"""
        return self.graph


def get_graph_adapter(config) -> GraphInterface:
    """
    Factory function to get appropriate graph adapter based on configuration
    
    Args:
        config: Configuration object
        
    Returns:
        GraphInterface instance (either NetworkXAdapter or Neo4jAdapter)
    """
    if config.USE_NEO4J:
        from neo4j_adapter import Neo4jAdapter
        return Neo4jAdapter(
            uri=config.NEO4J_URI,
            user=config.NEO4J_USER,
            password=config.NEO4J_PASSWORD,
            database=config.NEO4J_DATABASE
        )
    else:
        return NetworkXAdapter()
