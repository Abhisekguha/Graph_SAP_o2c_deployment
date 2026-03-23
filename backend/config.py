import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Gemini API Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # Server Configuration
    PORT = int(os.getenv("PORT", 8000))
    DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    
    # Neo4j Configuration
    USE_NEO4J = os.getenv("USE_NEO4J", "false").lower() == "true"
    NEO4J_URI = os.getenv("NEO4J_URI", "neo4j+s://localhost:7687")
    NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")
    NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")
    
    # Graph Configuration
    MAX_GRAPH_NODES = int(os.getenv("MAX_GRAPH_NODES", 1000))
    
config = Config()
