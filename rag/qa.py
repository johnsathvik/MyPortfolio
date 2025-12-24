from .retrieve import retrieve_relevant_chunks
from .gemini_client import get_gemini_client
from .config import GEN_MODEL


SYSTEM_PROMPT = """
You are an AI assistant for a personal portfolio website.

Rules:
- Answer ONLY using the provided portfolio context.
- Do NOT introduce new facts.
- Do NOT guess or hallucinate.
- If the answer is not clearly present, say:
  "I don’t have that information in my portfolio."

Formatting rules:
- Respond in complete, professional sentences.
- Combine related technologies into a single coherent explanation.
- Do NOT use bullet points unless explicitly asked.
- Write in third person (e.g., "John has used...").
"""


def answer_question(question: str):
    documents, distances = retrieve_relevant_chunks(question)

    if not documents:
        return "I don’t have that information in my portfolio."

    # Optional safety threshold
    if distances and min(distances) > 1.0:
        return "I don’t have that information in my portfolio."

    context = "\n".join(f"- {doc}" for doc in documents)

    prompt = f"""
{SYSTEM_PROMPT}

Portfolio Context:
{context}

Question:
{question}

Answer:
"""

    client = get_gemini_client()
    response = client.models.generate_content(
        model=GEN_MODEL,
        contents=prompt,
    )

    return response.text.strip()
