"""
Neo4j Database Adapter for SAP O2C Graph System

Replaces in-memory NetworkX graph with persistent Neo4j database.
Provides same interface as NetworkX for backward compatibility.
"""

from neo4j import GraphDatabase
from typing import Dict, List, Any, Optional, Tuple
import json
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class Neo4jAdapter:
    """Neo4j database adapter with NetworkX-compatible interface"""
    
    def __init__(self, uri: str, user: str, password: str, database: str = "neo4j"):
        """
        Initialize Neo4j connection
        
        Args:
            uri: Neo4j database URI (e.g., neo4j+s://xxx.databases.neo4j.io)
            user: Database username
            password: Database password
            database: Database name (default: neo4j)
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database
        logger.info(f"Connected to Neo4j at {uri}")
    
    def close(self):
        """Close database connection"""
        self.driver.close()
        logger.info("Neo4j connection closed")
    
    def verify_connectivity(self):
        """Verify database connection"""
        with self.driver.session(database=self.database) as session:
            result = session.run("RETURN 1 as num")
            return result.single()["num"] == 1
    
    # ===== NODE OPERATIONS =====
    
    def add_node(self, node_id: str, **properties):
        """
        Add a node to the graph
        
        Args:
            node_id: Unique identifier for the node
            **properties: Node properties including 'type' and 'label'
        """
        with self.driver.session(database=self.database) as session:
            node_type = properties.get('type', 'Generic')
            
            # Convert properties to Neo4j-compatible format
            props = self._clean_properties(properties)
            props['id'] = node_id
            
            session.run(
                f"""
                MERGE (n:{node_type} {{id: $node_id}})
                SET n += $props
                """,
                node_id=node_id,
                props=props
            )
    
    def add_edge(self, source: str, target: str, relationship_type: str = "RELATES_TO", **properties):
        """
        Add an edge between two nodes
        
        Args:
            source: Source node ID
            target: Target node ID
            relationship_type: Type of relationship
            **properties: Edge properties
        """
        with self.driver.session(database=self.database) as session:
            props = self._clean_properties(properties)
            
            session.run(
                f"""
                MATCH (a {{id: $source}})
                MATCH (b {{id: $target}})
                MERGE (a)-[r:{relationship_type}]->(b)
                SET r += $props
                """,
                source=source,
                target=target,
                props=props
            )
    
    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get node by ID"""
        with self.driver.session(database=self.database) as session:
            result = session.run(
                """
                MATCH (n {id: $node_id})
                RETURN n, labels(n) as labels
                """,
                node_id=node_id
            )
            record = result.single()
            if record:
                node = dict(record["n"])
                node['type'] = record["labels"][0] if record["labels"] else "Generic"
                return node
            return None
    
    def get_neighbors(self, node_id: str, relationship_type: Optional[str] = None) -> List[str]:
        """Get neighboring node IDs"""
        with self.driver.session(database=self.database) as session:
            if relationship_type:
                query = f"""
                MATCH (n {{id: $node_id}})-[:{relationship_type}]-(neighbor)
                RETURN DISTINCT neighbor.id as id
                """
            else:
                query = """
                MATCH (n {id: $node_id})--(neighbor)
                RETURN DISTINCT neighbor.id as id
                """
            
            result = session.run(query, node_id=node_id)
            return [record["id"] for record in result]
    
    # ===== GRAPH STATISTICS =====
    
    def number_of_nodes(self) -> int:
        """Get total number of nodes"""
        with self.driver.session(database=self.database) as session:
            result = session.run("MATCH (n) RETURN count(n) as count")
            return result.single()["count"]
    
    def number_of_edges(self) -> int:
        """Get total number of edges"""
        with self.driver.session(database=self.database) as session:
            result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
            return result.single()["count"]
    
    def get_node_types(self) -> Dict[str, int]:
        """Get count of nodes by type"""
        with self.driver.session(database=self.database) as session:
            result = session.run(
                """
                MATCH (n)
                UNWIND labels(n) as label
                RETURN label, count(*) as count
                """
            )
            return {record["label"]: record["count"] for record in result}
    
    # ===== GRAPH QUERIES =====
    
    def find_nodes_by_type(self, node_type: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Find nodes by type with limit"""
        with self.driver.session(database=self.database) as session:
            result = session.run(
                f"""
                MATCH (n:{node_type})
                RETURN n, labels(n) as labels
                LIMIT $limit
                """,
                limit=limit
            )
            nodes = []
            for record in result:
                node = dict(record["n"])
                node['type'] = record["labels"][0] if record["labels"] else node_type
                nodes.append(node)
            return nodes
    
    def find_nodes_by_property(self, property_name: str, property_value: Any, limit: int = 100) -> List[Dict[str, Any]]:
        """Find nodes by property value"""
        with self.driver.session(database=self.database) as session:
            result = session.run(
                f"""
                MATCH (n)
                WHERE n.{property_name} = $value
                RETURN n, labels(n) as labels
                LIMIT $limit
                """,
                value=property_value,
                limit=limit
            )
            nodes = []
            for record in result:
                node = dict(record["n"])
                node['type'] = record["labels"][0] if record["labels"] else "Generic"
                nodes.append(node)
            return nodes
    
    def get_subgraph(self, node_id: str, depth: int = 2) -> Tuple[List[Dict], List[Dict]]:
        """
        Get subgraph around a node up to specified depth
        
        Returns:
            Tuple of (nodes, edges)
        """
        with self.driver.session(database=self.database) as session:
            result = session.run(
                """
                MATCH path = (start {id: $node_id})-[*1..$depth]-(connected)
                WITH nodes(path) as nodes_list, relationships(path) as rels_list
                UNWIND nodes_list as n
                WITH collect(DISTINCT {id: n.id, properties: properties(n), labels: labels(n)}) as nodes,
                     collect(DISTINCT rels_list) as all_rels
                UNWIND all_rels as rel_list
                UNWIND rel_list as r
                RETURN nodes,
                       collect(DISTINCT {
                           source: startNode(r).id,
                           target: endNode(r).id,
                           type: type(r),
                           properties: properties(r)
                       }) as edges
                """,
                node_id=node_id,
                depth=depth
            )
            
            record = result.single()
            if record:
                nodes = []
                for n in record["nodes"]:
                    node = n["properties"]
                    node['type'] = n["labels"][0] if n["labels"] else "Generic"
                    nodes.append(node)
                
                return nodes, record["edges"]
            
            return [], []
    
    def get_path_between_nodes(self, source_id: str, target_id: str, max_depth: int = 5) -> List[str]:
        """Find shortest path between two nodes"""
        with self.driver.session(database=self.database) as session:
            result = session.run(
                """
                MATCH path = shortestPath((start {id: $source})-[*..10]-(end {id: $target}))
                RETURN [n in nodes(path) | n.id] as node_ids
                """,
                source=source_id,
                target=target_id
            )
            record = result.single()
            return record["node_ids"] if record else []
    
    # ===== GRAPH EXPORT (for visualization) =====
    
    def get_graph_data(self, limit: int = 1000) -> Dict[str, Any]:
        """
        Export graph data for visualization
        
        Args:
            limit: Maximum number of nodes to return
            
        Returns:
            Dict with 'nodes' and 'edges' lists
        """
        with self.driver.session(database=self.database) as session:
            # Get nodes
            nodes_result = session.run(
                """
                MATCH (n)
                RETURN n.id as id, n.label as label, n.type as type, properties(n) as props
                LIMIT $limit
                """,
                limit=limit
            )
            
            nodes = []
            for record in nodes_result:
                node = {
                    'id': record['id'],
                    'label': record.get('label', record['id']),
                    'type': record.get('type', 'Generic')
                }
                nodes.append(node)
            
            # Get edges between these nodes
            node_ids = [n['id'] for n in nodes]
            edges_result = session.run(
                """
                MATCH (a)-[r]->(b)
                WHERE a.id IN $node_ids AND b.id IN $node_ids
                RETURN a.id as source, b.id as target, type(r) as type, properties(r) as props
                """,
                node_ids=node_ids
            )
            
            edges = []
            for record in edges_result:
                edge = {
                    'source': record['source'],
                    'target': record['target'],
                    'label': record.get('type', 'relates_to')
                }
                edges.append(edge)
            
            return {
                'nodes': nodes,
                'edges': edges
            }
    
    # ===== UTILITY METHODS =====
    
    def _clean_properties(self, properties: Dict) -> Dict:
        """Clean properties for Neo4j (remove None, convert types)"""
        cleaned = {}
        for key, value in properties.items():
            if value is None:
                continue
            
            # Convert lists to strings if they're not simple types
            if isinstance(value, (list, dict)):
                cleaned[key] = json.dumps(value)
            elif isinstance(value, (str, int, float, bool)):
                cleaned[key] = value
            else:
                # Convert other types to string
                cleaned[key] = str(value)
        
        return cleaned
    
    def clear_database(self):
        """Clear all nodes and relationships (use with caution!)"""
        with self.driver.session(database=self.database) as session:
            session.run("MATCH (n) DETACH DELETE n")
            logger.warning("Database cleared!")
    
    def create_indexes(self):
        """Create indexes for better query performance"""
        with self.driver.session(database=self.database) as session:
            # Index on node IDs
            session.run("CREATE INDEX node_id_index IF NOT EXISTS FOR (n:SalesOrder) ON (n.id)")
            session.run("CREATE INDEX invoice_id_index IF NOT EXISTS FOR (n:Invoice) ON (n.id)")
            session.run("CREATE INDEX delivery_id_index IF NOT EXISTS FOR (n:Delivery) ON (n.id)")
            session.run("CREATE INDEX customer_id_index IF NOT EXISTS FOR (n:Customer) ON (n.id)")
            session.run("CREATE INDEX product_id_index IF NOT EXISTS FOR (n:Product) ON (n.id)")
            
            # Indexes on common properties
            session.run("CREATE INDEX so_number_index IF NOT EXISTS FOR (n:SalesOrder) ON (n.salesOrder)")
            session.run("CREATE INDEX invoice_number_index IF NOT EXISTS FOR (n:Invoice) ON (n.billingDocument)")
            
            logger.info("Indexes created successfully")
    
    # ===== CYPHER QUERY EXECUTION =====
    
    def run_cypher(self, query: str, parameters: Dict = None) -> List[Dict]:
        """
        Execute custom Cypher query
        
        Args:
            query: Cypher query string
            parameters: Query parameters
            
        Returns:
            List of result records as dictionaries
        """
        with self.driver.session(database=self.database) as session:
            result = session.run(query, parameters or {})
            return [dict(record) for record in result]
