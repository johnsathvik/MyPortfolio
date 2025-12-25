import hashlib
from pathlib import Path

from .config import KNOWLEDGE_DIR, EMBED_MODEL
from .gemini_client import get_gemini_client
from .store import get_chroma_client, reset_collection


def chunk_text(text: str, chunk_size: int = 900, overlap: int = 150):
    """
    Split text into overlapping chunks.
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


def stable_chunk_id(text: str, source: str) -> str:
    """
    Generate stable chunk IDs using content + source filename.
    Prevents duplication across re-indexing.
    """
    raw = f"{source}:{text}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings using Gemini.
    """
    client = get_gemini_client()

    response = client.models.embed_content(
        model=EMBED_MODEL,
        contents=texts,
    )

    return [list(e.values) for e in response.embeddings]


def rebuild_knowledge():
    """
    Manual re-learning entry point.
    Rebuilds the vector database from all .txt files.
    """
    if not KNOWLEDGE_DIR.exists():
        raise FileNotFoundError(f"Knowledge directory not found: {KNOWLEDGE_DIR}")

    txt_files = sorted(KNOWLEDGE_DIR.glob("*.txt"))

    if not txt_files:
        raise RuntimeError("No .txt knowledge files found.")

    chroma = get_chroma_client()
    collection = reset_collection(chroma)

    batch_size = 32
    total_chunks = 0

    for file_path in txt_files:
        raw_text = file_path.read_text(encoding="utf-8")
        chunks = chunk_text(raw_text)

        source_name = file_path.name
        section_name = file_path.stem  # about, experience, projects, etc.

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]

            embeddings = embed_texts(batch)

            ids = [
                stable_chunk_id(text, source_name)
                for text in batch
            ]

            metadatas = [
                {
                    "source_file": source_name,
                    "section": section_name,
                }
                for _ in batch
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
        "files_indexed": len(txt_files),
        "chunks_indexed": total_chunks,
    }
    