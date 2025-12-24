from pathlib import Path
import os
from dotenv import load_dotenv

# Load .env safely
load_dotenv()

# Project root
BASE_DIR = Path(__file__).resolve().parent.parent

KNOWLEDGE_FILE = (
    BASE_DIR
    / "PortfolioMain"
    / "data"
    / "portfolio_knowledge.txt"
)

CHROMA_DIR = BASE_DIR / "rag" / "chroma_db"
COLLECTION_NAME = "portfolio_knowledge"

EMBED_MODEL = "gemini-embedding-001"
GEN_MODEL = "gemini-2.0-flash"


def get_gemini_api_key():
    """
    Always fetch the API key at runtime, never at import time.
    """
    return os.getenv("GEMINI_API_KEY")
