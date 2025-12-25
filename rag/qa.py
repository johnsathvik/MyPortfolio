from .retrieve import retrieve_relevant_chunks
from .gemini_client import get_gemini_client
from .config import GEN_MODEL


# Neutral, professional fallback
FALLBACK_RESPONSE = (
    "John’s portfolio does not provide information to answer that question."
)


def _question_type(question: str) -> str:
    q = question.lower()

    if any(k in q for k in ["everything you know", "about john in short", "summary", "overview"]):
        return "overview"

    if any(k in q for k in ["can john", "can he", "is john able", "could john"]):
        return "capability"

    if any(
        k in q
        for k in [
            "portfolio project",
            "portfolio website",
            "myportfolio",
            "deploy",
            "deployment",
            "ci/cd",
            "nginx",
            "gunicorn",
            "firebase role",
            "github actions",
        ]
    ):
        return "project"

    return "general"


def soften_absence(answer: str) -> str:
    """
    Makes absence responses sound professional instead of robotic.
    """
    replacements = {
        "is not listed in John’s portfolio": "is not documented in John’s portfolio",
        "is not listed in John's portfolio": "is not documented in John’s portfolio",
        "does not list": "does not document",
        "does not provide information": "does not document information",
    }

    for old, new in replacements.items():
        answer = answer.replace(old, new)

    return answer


SYSTEM_PROMPT = """
You are an AI assistant for a developer portfolio website.

Hard rules:
- Use ONLY the provided portfolio context.
- Do NOT add new facts, assumptions, or exaggerations.
- If something is not mentioned, clearly state that it is not documented in John’s portfolio.

Answer style:
- Respond in complete, professional sentences.
- Write strictly in third person (John…).
- Avoid resume filler phrases such as "has experience with" for project-specific questions.
- For project questions: explain HOW technologies were used, not just what was used.
- For capability questions: answer ONLY if the portfolio provides evidence, and reference it explicitly.
- Keep answers concise, confident, and recruiter-friendly.
"""


def answer_question(question: str):
    documents, distances, metadatas = retrieve_relevant_chunks(question)

    # No context retrieved
    if not documents:
        return FALLBACK_RESPONSE

    # Similarity guard
    if distances and min(distances) > 1.0:
        return FALLBACK_RESPONSE

    qtype = _question_type(question)

    # Merge retrieved context cleanly
    context = "\n\n".join(documents)

    # Controller instructions reduce generation drift
    if qtype == "project":
        controller = (
            "This is a PROJECT question. "
            "Answer only using project-related context and explain how technologies were used."
        )
    elif qtype == "capability":
        controller = (
            "This is a CAPABILITY question. "
            "Only answer if the portfolio provides direct evidence, and cite the supporting project or role."
        )
    elif qtype == "overview":
        controller = (
            "This is an OVERVIEW request. "
            "Provide a short professional summary covering education, experience, and one key project."
        )
    else:
        controller = "This is a GENERAL portfolio question. Answer directly using the context."

    prompt = f"""
{SYSTEM_PROMPT}

Controller:
{controller}

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
        # Recommended if available:
        # config={"temperature": 0.2, "max_output_tokens": 220}
    )

    raw_answer = (response.text or "").strip()

    if not raw_answer:
        return FALLBACK_RESPONSE

    return soften_absence(raw_answer)
