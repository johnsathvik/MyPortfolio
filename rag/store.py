import chromadb
from .config import CHROMA_DIR, COLLECTION_NAME


def get_chroma_client():
    """
    Returns a persistent Chroma client.
    Data is stored on disk under rag/chroma_db.
    """
    return chromadb.PersistentClient(path=str(CHROMA_DIR))


def get_collection(client):
    """
    Get or create the main portfolio collection.
    """
    return client.get_or_create_collection(name=COLLECTION_NAME)


def reset_collection(client):
    """
    Deletes and recreates the collection.
    Used during manual re-indexing.
    """
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        # Collection may not exist on first run
        pass

    return client.get_or_create_collection(name=COLLECTION_NAME)
