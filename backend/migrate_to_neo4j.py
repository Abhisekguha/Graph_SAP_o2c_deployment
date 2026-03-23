"""
Data Migration Script for Neo4j

Loads SAP O2C data from JSONL files and populates Neo4j database.
Run this once to initialize the database with your dataset.

Usage:
    python migrate_to_neo4j.py [--clear] [--batch-size 1000]
    
Options:
    --clear         Clear existing data before migration
    --batch-size    Number of nodes/edges to create per transaction (default: 1000)
"""

import sys
import os
import argparse
import logging
from typing import Dict, List
from tqdm import tqdm

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from backend.config import config
from backend.data_loader import DataLoader
from backend.graph_builder import GraphBuilder
from backend.neo4j_adapter import Neo4jAdapter

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Neo4jMigration:
    """Handle migration of SAP O2C data to Neo4j"""
    
    def __init__(self, neo4j_adapter: Neo4jAdapter, batch_size: int = 1000):
        self.db = neo4j_adapter
        self.batch_size = batch_size
    
    def migrate_data(self, entities: Dict[str, List[Dict]], clear_first: bool = False):
        """
        Migrate data from JSONL files to Neo4j
        
        Args:
            entities: Dictionary of entity types and their data
            clear_first: Whether to clear existing data first
        """
        logger.info("=" * 60)
        logger.info("Starting Neo4j Migration")
        logger.info("=" * 60)
        
        # Clear database if requested
        if clear_first:
            logger.warning("Clearing existing database...")
            self.db.clear_database()
            logger.info("✓ Database cleared")
        
        # Verify connectivity
        if not self.db.verify_connectivity():
            raise Exception("Failed to connect to Neo4j database")
        logger.info("✓ Connected to Neo4j")
        
        # Build graph structure using existing GraphBuilder
        logger.info("Building graph structure...")
        builder = GraphBuilder(entities, self.db)
        graph = builder.build_graph()
        logger.info(f"✓ Graph structure built: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")
        
        # Migrate nodes
        logger.info("\nMigrating nodes to Neo4j...")
        self._migrate_nodes(graph)
        
        # Migrate edges
        logger.info("\nMigrating edges to Neo4j...")
        self._migrate_edges(graph)
        
        # Create indexes
        logger.info("\nCreating database indexes...")
        self.db.create_indexes()
        logger.info("✓ Indexes created")
        
        # Verify migration
        logger.info("\nVerifying migration...")
        node_count = self.db.number_of_nodes()
        edge_count = self.db.number_of_edges()
        logger.info(f"✓ Nodes in Neo4j: {node_count}")
        logger.info(f"✓ Edges in Neo4j: {edge_count}")
        
        # Show node type distribution
        node_types = self.db.get_node_types()
        logger.info("\nNode types in database:")
        for node_type, count in sorted(node_types.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"  {node_type}: {count}")
        
        logger.info("\n" + "=" * 60)
        logger.info("Migration completed successfully!")
        logger.info("=" * 60)
    
    def _migrate_nodes(self, graph):
        """Migrate all nodes from NetworkX graph to Neo4j"""
        nodes = list(graph.nodes(data=True))
        total_nodes = len(nodes)
        
        logger.info(f"Migrating {total_nodes} nodes...")
        
        with tqdm(total=total_nodes, desc="Nodes") as pbar:
            for node_id, properties in nodes:
                self.db.add_node(node_id, **properties)
                pbar.update(1)
        
        logger.info(f"✓ Migrated {total_nodes} nodes")
    
    def _migrate_edges(self, graph):
        """Migrate all edges from NetworkX graph to Neo4j"""
        edges = list(graph.edges(data=True, keys=True))
        total_edges = len(edges)
        
        logger.info(f"Migrating {total_edges} edges...")
        
        with tqdm(total=total_edges, desc="Edges") as pbar:
            for source, target, key, properties in edges:
                rel_type = properties.get('label', 'RELATES_TO').upper().replace(' ', '_')
                self.db.add_edge(source, target, rel_type, **properties)
                pbar.update(1)
        
        logger.info(f"✓ Migrated {total_edges} edges")


def main():
    """Main migration function"""
    parser = argparse.ArgumentParser(description="Migrate SAP O2C data to Neo4j")
    parser.add_argument('--clear', action='store_true', help='Clear existing data before migration')
    parser.add_argument('--batch-size', type=int, default=1000, help='Batch size for migration')
    parser.add_argument('--test', action='store_true', help='Test connection only')
    args = parser.parse_args()
    
    try:
        # Check configuration
        if not config.NEO4J_URI or not config.NEO4J_PASSWORD:
            raise Exception(
                "Neo4j configuration missing. Please set NEO4J_URI and NEO4J_PASSWORD environment variables."
            )
        
        logger.info("Configuration:")
        logger.info(f"  Neo4j URI: {config.NEO4J_URI}")
        logger.info(f"  Neo4j User: {config.NEO4J_USERNAME}")
        logger.info(f"  Neo4j Database: {config.NEO4J_DATABASE}")
        logger.info(f"  Data Path: {config.DATA_PATH}")
        logger.info(f"  Batch Size: {args.batch_size}")
        
        # Connect to Neo4j
        logger.info("\nConnecting to Neo4j...")
        neo4j_db = Neo4jAdapter(
            uri=config.NEO4J_URI,
            user=config.NEO4J_USERNAME,
            password=config.NEO4J_PASSWORD,
            database=config.NEO4J_DATABASE
        )
        
        # Test connection
        if neo4j_db.verify_connectivity():
            logger.info("✓ Neo4j connection successful")
        else:
            raise Exception("Failed to connect to Neo4j")
        
        if args.test:
            logger.info("Test mode - connection verified. Exiting.")
            neo4j_db.close()
            return
        
        # Load data
        logger.info(f"\nLoading data from: {config.DATA_PATH}")
        loader = DataLoader(config.DATA_PATH)
        entities = loader.load_all_entities()
        
        entity_counts = loader.get_entity_counts()
        logger.info("Loaded entities:")
        for entity_type, count in entity_counts.items():
            logger.info(f"  {entity_type}: {count}")
        
        # Confirm before clearing
        if args.clear:
            response = input("\n⚠️  This will DELETE all existing data in Neo4j. Continue? (yes/no): ")
            if response.lower() != 'yes':
                logger.info("Migration cancelled.")
                neo4j_db.close()
                return
        
        # Run migration
        migration = Neo4jMigration(neo4j_db, batch_size=args.batch_size)
        migration.migrate_data(entities, clear_first=args.clear)
        
        # Close connection
        neo4j_db.close()
        
        logger.info("\n✅ Migration completed successfully!")
        logger.info("You can now start the application with USE_NEO4J=true")
        
    except KeyboardInterrupt:
        logger.info("\nMigration cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ Migration failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
