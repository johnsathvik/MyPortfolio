import hashlib
from pathlib import Path

from .config import KNOWLEDGE_FILE, EMBED_MODEL
from .gemini_client import get_gemini_client
from .store import get_chroma_client, reset_collection


def chunk_text(text: str, chunk_size: int = 900, overlap: int = 150):
    """
    Split text into overlapping chunks.
    This improves retrieval accuracy.
    """
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap

    return chunks


def stable_chunk_id(text: str) -> str:
    """
    Generate a stable ID so re-indexing does not duplicate chunks.
    """
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:24]


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings using Gemini.
    """
    client = get_gemini_client()

    response = client.models.embed_content(
        model=EMBED_MODEL,
        contents=texts,
    )

    embeddings = response.embeddings
    return [list(e.values) for e in embeddings]


def rebuild_knowledge():
    """
    Manual re-learning entry point.
    Deletes old vectors and rebuilds from the text file.
    """
    if not KNOWLEDGE_FILE.exists():
        raise FileNotFoundError(f"Knowledge file not found: {KNOWLEDGE_FILE}")

    raw_text = KNOWLEDGE_FILE.read_text(encoding="utf-8")

    chunks = chunk_text(raw_text)

    chroma = get_chroma_client()
    collection = reset_collection(chroma)

    batch_size = 32
    total_chunks = 0

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        embeddings = embed_texts(batch)

        ids = [stable_chunk_id(text) for text in batch]
        metadatas = [
            {"source": str(KNOWLEDGE_FILE), "chunk_index": i + idx}
            for idx in range(len(batch))
        ]

        collection.add(
            ids=ids,
            documents=batch,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        total_chunks += len(batch)

    return {
        "status": "success",
        "chunks_indexed": total_chunks,
    }
