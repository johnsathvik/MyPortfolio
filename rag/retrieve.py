from .store import get_chroma_client, get_collection
from .embed import embed_query


def infer_section_filter(question: str):
    q = question.lower()

    # Portfolio project / deployment questions should hit projects
    if any(k in q for k in ["portfolio project", "portfolio website", "myportfolio"]):
        return {"section": "projects"}

    # If user asks "tell me everything" → no filter, search all
    if any(k in q for k in ["everything you know", "summary", "about john in short", "overview"]):
        return None

    # Section routing
    if any(k in q for k in ["project", "architecture", "deploy", "deployment", "ci/cd", "cicd", "github actions", "nginx", "gunicorn", "firebase role"]):
        return {"section": "projects"}

    if any(k in q for k in ["experience", "intern", "job", "worked at", "responsibilities"]):
        return {"section": "experience"}

    if any(k in q for k in ["education", "degree", "university", "graduate", "graduation"]):
        return {"section": "education"}

    if any(k in q for k in ["certification", "certifications", "certified", "az-900", "aws solutions architect"]):
        return {"section": "certifications"}

    if any(k in q for k in ["tech stack", "skills", "languages", "tools", "technology"]):
        return {"section": "tech_stack"}

    if any(k in q for k in ["contact", "linkedin", "github", "portfolio website", "reach", "connect"]):
        return {"section": "contact"}

    return None


def retrieve_relevant_chunks(question: str, k: int = 5):
    client = get_chroma_client()
    collection = get_collection(client)

    where_filter = infer_section_filter(question)
    q_emb = embed_query(question)

    results = collection.query(
        query_embeddings=[q_emb],
        n_results=k,
        where=where_filter,
    )

    documents = results.get("documents", [[]])[0]
    distances = results.get("distances", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    return documents, distances, metadatas
