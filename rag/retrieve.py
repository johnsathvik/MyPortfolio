from .store import get_chroma_client
from .config import COLLECTION_NAME, EMBED_MODEL
from .gemini_client import get_gemini_client


def embed_query(query: str) -> list[float]:
    """
    Generate an embedding for the user query using Gemini.
    """
    client = get_gemini_client()

    response = client.models.embed_content(
        model=EMBED_MODEL,
        contents=[query],
    )

    return list(response.embeddings[0].values)


def retrieve_relevant_chunks(query: str, top_k: int = 4):
    """
    Retrieve relevant chunks using Gemini embeddings (dimension-safe).
    """
    query_embedding = embed_query(query)

    client = get_chroma_client()
    collection = client.get_collection(COLLECTION_NAME)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
    )

    documents = results.get("documents", [[]])[0]
    distances = results.get("distances", [[]])[0]

    return documents, distances
