from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project root
BASE_DIR = Path(__file__).resolve().parent.parent

# Directory containing multiple knowledge files
KNOWLEDGE_DIR = (
    BASE_DIR
    / "PortfolioMain"
    / "data"
    / "rag_knowledge"
)

# Chroma persistence
CHROMA_DIR = BASE_DIR / "rag" / "chroma_db"
COLLECTION_NAME = "rag_knowledge"

# Gemini models
EMBED_MODEL = "gemini-embedding-001"
GEN_MODEL = "gemini-2.0-flash"  # works once billing is enabled

def get_gemini_api_key():
    """
    Fetch Gemini API key at runtime.
    """
    return os.getenv("GEMINI_API_KEY")
