from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime

from models import QueryRequest, QueryResponse, GraphData, Node, Edge
from config import config
from data_loader import DataLoader
from graph_builder import GraphBuilder
from query_engine import QueryEngine
from neo4j_adapter import Neo4jAdapter

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="SAP O2C Graph Query System",
    description="Graph-based data modeling and natural language query system for SAP Order-to-Cash data",
    version="1.0.0"
)

# CORS middleware - Update with your Vercel domain in production
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://*.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if config.ENVIRONMENT == "development" else allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state for graph and query engine
graph_adapter = None
query_engine = None
graph_builder = None
stats = {}

@app.on_event("startup")
async def startup_event():
    """Initialize the graph on startup"""
    global graph_adapter, query_engine, graph_builder, stats
    
    logger.info("Starting SAP O2C Graph System...")
    logger.info(f"Environment: {config.ENVIRONMENT}")
    logger.info(f"Using Neo4j: {config.USE_NEO4J}")
    
    try:
        # Initialize graph adapter (Neo4j or NetworkX)
        if config.USE_NEO4J:
            logger.info("Connecting to Neo4j database...")
            graph_adapter = Neo4jAdapter(
                uri=config.NEO4J_URI,
                user=config.NEO4J_USERNAME,  # ← Changed to 'user'
                password=config.NEO4J_PASSWORD,
                database=config.NEO4J_DATABASE  # ← ADD THIS LINE
            )
            logger.info("✓ Connected to Neo4j")
            
            # Check if graph is already populated
            node_count = graph_adapter.number_of_nodes()
            
            if node_count == 0:
                logger.info("Graph is empty. Loading and building graph...")
                
                # Load data
                logger.info("Loading data from JSONL files...")
                loader = DataLoader(config.DATA_PATH)
                entities = loader.load_all_entities()
                
                entity_counts = loader.get_entity_counts()
                logger.info(f"Loaded entities: {entity_counts}")
                
                # Build graph in Neo4j
                logger.info("Building graph in Neo4j...")
                graph_builder = GraphBuilder(entities, graph_adapter)
                graph_builder.build_graph()
                
                node_count = graph_adapter.number_of_nodes()
                edge_count = graph_adapter.number_of_edges()
                logger.info(f"Graph built: {node_count} nodes, {edge_count} edges")
            else:
                logger.info(f"Graph already populated with {node_count} nodes")
                
                # Still need entities for query engine
                logger.info("Loading entities for query engine...")
                loader = DataLoader(config.DATA_PATH)
                entities = loader.load_all_entities()
        else:
            # In-memory NetworkX fallback
            logger.info("Using in-memory NetworkX graph...")
            from graph_interface import NetworkXAdapter
            
            loader = DataLoader(config.DATA_PATH)
            entities = loader.load_all_entities()
            
            entity_counts = loader.get_entity_counts()
            logger.info(f"Loaded entities: {entity_counts}")
            
            graph_adapter = NetworkXAdapter()
            graph_builder = GraphBuilder(entities, graph_adapter)
            graph_builder.build_graph()
            
            logger.info(f"Graph built: {graph_adapter.number_of_nodes()} nodes, {graph_adapter.number_of_edges()} edges")
        
        # Get stats
        try:
            stats = graph_builder.get_stats() if graph_builder else {
                'total_nodes': graph_adapter.number_of_nodes(),
                'total_edges': graph_adapter.number_of_edges()
            }
        except AttributeError:
            # If get_stats fails, just use basic stats
            stats = {
                'total_nodes': 0,
                'total_edges': 0
            }
        # Initialize query engine
        logger.info("Initializing query engine...")
        query_engine = QueryEngine(graph_adapter, entities)
        
        logger.info("✓ System ready!")
        
    except Exception as e:
        logger.error(f"Failed to initialize system: {e}", exc_info=True)
        raise

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "SAP O2C Graph Query System",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    if graph_adapter is None:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    return {
        "status": "healthy",
        "graph_loaded": True,
        "total_nodes": stats.get('total_nodes', 0),
        "total_edges": stats.get('total_edges', 0),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/graph/stats")
async def get_graph_stats():
    """Get graph statistics"""
    if graph_adapter is None:
        raise HTTPException(status_code=503, detail="Graph not initialized")
    
    return {
        **stats,
        'total_nodes': graph_adapter.number_of_nodes(),
        'total_edges': graph_adapter.number_of_edges()
    }

@app.get("/api/graph/data")
async def get_full_graph(
    limit: Optional[int] = 1000
):
    """Get complete graph data (nodes and edges)"""
    if graph_adapter is None:
        raise HTTPException(status_code=503, detail="Graph not initialized")
    
    return graph_adapter.get_graph_data(limit=limit)

@app.get("/api/graph/nodes")
async def get_nodes(
    node_type: Optional[str] = None,
    limit: Optional[int] = 100,
    offset: Optional[int] = 0
):
    """Get nodes with optional filtering"""
    if graph_adapter is None:
        raise HTTPException(status_code=503, detail="Graph not initialized")
    
    if node_type:
        nodes = graph_adapter.find_nodes_by_type(node_type, limit=limit)
    else:
        # Get all nodes with limit
        graph_data = graph_adapter.get_graph_data(limit=limit)
        nodes = graph_data['nodes']
    
    return {
        "nodes": nodes,
        "total": len(nodes),
        "limit": limit,
        "offset": offset
    }

@app.get("/api/graph/node/{node_id}")
async def get_node(node_id: str):
    """Get specific node by ID"""
    if graph_adapter is None:
        raise HTTPException(status_code=503, detail="Graph not initialized")
    
    # Get node data
    node_data = graph_adapter.get_node(node_id)
    
    if node_data is None:
        raise HTTPException(status_code=404, detail=f"Node {node_id} not found")
    
    # Get neighbors
    neighbor_ids = graph_adapter.get_neighbors(node_id)
    neighbors = [graph_adapter.get_node(nid) for nid in neighbor_ids[:20]]  # Limit neighbors
    neighbors = [n for n in neighbors if n is not None]
    
    return {
        "node": {"id": node_id, **node_data},
        "neighbors": neighbors,
        "neighbor_count": len(neighbor_ids)
    }

@app.get("/api/graph/edges")
async def get_edges(
    edge_type: Optional[str] = None,
    limit: Optional[int] = 100,
    offset: Optional[int] = 0
):
    """Get edges with optional filtering"""
    if graph_adapter is None:
        raise HTTPException(status_code=503, detail="Graph not initialized")
    
    graph_data = graph_adapter.get_graph_data(limit=limit*10)
    edges = graph_data['edges']
    
    # Filter by type if specified
    if edge_type:
        edges = [e for e in edges if e['type'] == edge_type]
    
    # Apply pagination
    total = len(edges)
    edges = edges[offset:offset + limit]
    
    return {
        "edges": edges,
        "total": total,
        "limit": limit,
        "offset": offset
    }

@app.post("/api/query")
async def query_graph(request: QueryRequest):
    """Process natural language query"""
    if query_engine is None:
        raise HTTPException(status_code=503, detail="Query engine not initialized")
    
    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    try:
        logger.info(f"Processing query: {request.query}")
        
        # Process query
        result = query_engine.process_query(
            request.query,
            request.conversation_history
        )
        
        logger.info(f"Query type: {result.get('query_type')}")
        
        return QueryResponse(
            answer=result['answer'],
            query_type=result.get('query_type'),
            structured_query=result.get('structured_query'),
            data=result.get('data'),
            highlighted_nodes=result.get('highlighted_nodes', [])
        )
        
    except Exception as e:
        logger.error(f"Query processing error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")

@app.get("/api/search/nodes")
async def search_nodes(q: str, limit: int = 20):
    """Search nodes by label or properties"""
    if graph_adapter is None:
        raise HTTPException(status_code=503, detail="Graph not initialized")
    
    if not q or not q.strip():
        return {"nodes": [], "total": 0}
    
    # Use graph adapter's search functionality
    matches = []
    
    # Search by node ID pattern
    if "_" in q:
        node_data = graph_adapter.get_node(q.upper())
        if node_data:
            matches.append({"id": q.upper(), **node_data})
    
    # For more complex searches, get sample of nodes and filter
    # In production, implement full-text search in Neo4j
    graph_data = graph_adapter.get_graph_data(limit=500)
    q_lower = q.lower()
    
    for node in graph_data['nodes']:
        if len(matches) >= limit:
            break
        
        if node['id'] in [m['id'] for m in matches]:
            continue
            
        # Search in label
        if q_lower in node.get('label', '').lower():
            matches.append(node)
            continue
        
        # Search in properties
        for key, value in node.get('properties', {}).items():
            if isinstance(value, str) and q_lower in str(value).lower():
                matches.append(node)
                break
    
    return {
        "nodes": matches[:limit],
        "total": len(matches),
        "query": q
    }

@app.get("/api/analyze/broken-flows")
async def analyze_broken_flows():
    """Analyze and return broken or incomplete document flows"""
    if graph_adapter is None:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        broken_flows = {
            'orders_without_delivery': [],
            'deliveries_without_invoice': [],
            'invoices_without_payment': []
        }
        
        graph = graph_adapter
        
        # Find sales orders without deliveries
        for node_id in graph.nodes():
            if node_id.startswith('SO_'):
                has_delivery = any(
                    succ.startswith('DEL_') for succ in graph.successors(node_id)
                )
                if not has_delivery:
                    node_data = graph_adapter.get_node(node_id) or {'id': node_id, 'label': node_id}
                    node_data['id'] = node_id
                    broken_flows['orders_without_delivery'].append(node_data)
        
        # Find deliveries without invoices 
        for node_id in graph.nodes():
            if node_id.startswith('DEL_'):
                # Check predecessors (sales orders) for invoices
                has_invoice = False
                for pred in graph.predecessors(node_id):
                    if pred.startswith('SO_'):
                        for succ in graph.successors(pred):
                            if succ.startswith('INV_'):
                                has_invoice = True
                                break
                
                if not has_invoice:
                    node_data = graph_adapter.get_node(node_id) or {'id': node_id, 'label': node_id}
                    node_data['id'] = node_id
                    broken_flows['deliveries_without_invoice'].append(node_data)
        
        # Find invoices without payments (no clearing document)
        for node_id in graph.nodes():
            if node_id.startswith('INV_'):
                has_payment = any(
                    succ.startswith('JE_') for succ in graph.successors(node_id)
                )
                
                if has_payment:
                    # Check if journal entry has payment
                    je_has_payment = False
                    for je_id in graph.successors(node_id):
                        if any(succ.startswith('PAY_') for succ in graph.successors(je_id)):
                            je_has_payment = True
                            break
                    
                    if not je_has_payment:
                        node_data = graph_adapter.get_node(node_id) or {'id': node_id, 'label': node_id}
                        node_data['id'] = node_id
                        broken_flows['invoices_without_payment'].append(node_data)
        
        # Limit results
        for key in broken_flows:
            broken_flows[key] = broken_flows[key][:50]
        
        return {
            "summary": {
                "orders_without_delivery": len(broken_flows['orders_without_delivery']),
                "deliveries_without_invoice": len(broken_flows['deliveries_without_invoice']),
                "invoices_without_payment": len(broken_flows['invoices_without_payment'])
            },
            "details": broken_flows
        }
        
    except Exception as e:
        logger.error(f"Broken flow analysis error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/trace/{node_id}")
async def trace_document(node_id: str):
    """Trace complete document flow from a given node"""
    if graph_adapter is None:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    if not graph_adapter.has_node(node_id):
        raise HTTPException(status_code=404, detail=f"Node {node_id} not found")
    
    # BFS to find all connected nodes
    visited = set()
    queue = [node_id]
    
    while queue:
        current = queue.pop(0)
        if current in visited:
            continue
        visited.add(current)
        
        # Add predecessors and successors
        for pred in graph_adapter.predecessors(current):
            if pred not in visited:
                queue.append(pred)
        
        for succ in graph_adapter.successors(current):
            if succ not in visited:
                queue.append(succ)
    
    # Get nodes and edges for this flow
    flow_nodes = []
    for vid in visited:
        node_data = graph_adapter.get_node(vid)
        if node_data:
            node_data['id'] = vid
            flow_nodes.append(node_data)
    
    # Get edges - fetch from adapter
    all_edges = graph_adapter.get_graph_data(limit=10000)['edges']
    flow_edges = [
        e for e in all_edges
        if e['source'] in visited and e['target'] in visited
    ]
    
    return {
        "origin_node": node_id,
        "flow": {
            "nodes": flow_nodes,
            "edges": flow_edges
        },
        "stats": {
            "total_nodes": len(flow_nodes),
            "total_edges": len(flow_edges)
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=config.PORT)
