from .gemini_client import get_gemini_client
from .config import EMBED_MODEL


def embed_query(text: str) -> list[float]:
    client = get_gemini_client()
    resp = client.models.embed_content(
        model=EMBED_MODEL,
        contents=[text],
    )
    return list(resp.embeddings[0].values)
