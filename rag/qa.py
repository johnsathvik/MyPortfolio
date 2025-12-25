from .retrieve import retrieve_relevant_chunks
from .gemini_client import get_gemini_client
from .config import GEN_MODEL


# ----------------------------------
# Global fallback (safe + professional)
# ----------------------------------

FALLBACK_RESPONSE = (
    "John’s portfolio does not document information to answer that question."
)


# ----------------------------------
# Intent guards (NO RAG)
# ----------------------------------

def is_greeting(question: str) -> bool:
    q = question.lower().strip()

    greetings = {
        "hi",
        "hello",
        "hey",
        "hi!",
        "hello!",
        "hey!",
        "good morning",
        "good afternoon",
        "good evening",
    }

    if q in greetings:
        return True

    # Handle casual greetings like "hello there", "hi john"
    return q.startswith(("hi ", "hello ", "hey "))


def is_too_short(question: str) -> bool:
    return len(question.strip()) < 4


# ----------------------------------
# Question classification
# ----------------------------------

def _question_type(question: str) -> str:
    q = question.lower()

    if any(k in q for k in [
        "everything you know",
        "about john in short",
        "summary",
        "overview",
        "who is john",
    ]):
        return "overview"

    if any(k in q for k in [
        "can john",
        "can he",
        "is john able",
        "could john",
    ]):
        return "capability"

    if any(k in q for k in [
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
    ]):
        return "project"

    return "general"


# ----------------------------------
# Absence softening
# ----------------------------------

def soften_absence(answer: str) -> str:
    replacements = {
        "is not listed in John’s portfolio": "is not documented in John’s portfolio",
        "is not listed in John's portfolio": "is not documented in John’s portfolio",
        "does not list": "does not document",
        "does not provide information": "does not document information",
    }

    for old, new in replacements.items():
        answer = answer.replace(old, new)

    return answer


# ----------------------------------
# System prompt
# ----------------------------------

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


# ----------------------------------
# Main entry point
# ----------------------------------

def answer_question(question: str):
    # Greeting guard
    if is_greeting(question):
        return (
            "Hi! I’m John’s portfolio assistant. "
            "You can ask me about his projects, experience, AWS architecture work, or technical skills."
        )

    # Noise / meaningless input guard
    if is_too_short(question):
        return (
            "You can ask me about John’s projects, experience, education, or cloud architecture work."
        )

    # Retrieve context
    documents, distances, metadatas = retrieve_relevant_chunks(question)

    if not documents:
        return FALLBACK_RESPONSE

    # Similarity guard (important for correctness)
    if distances and min(distances) > 1.2:
        return FALLBACK_RESPONSE

    qtype = _question_type(question)

    # Merge context cleanly
    context = "\n\n".join(documents)

    # Controller to reduce drift
    if qtype == "project":
        controller = (
            "This is a PROJECT question. "
            "Answer only using project-related context and explain how technologies were used."
        )
    elif qtype == "capability":
        controller = (
            "This is a CAPABILITY question. "
            "Only answer if the portfolio provides direct evidence, and reference it explicitly."
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
        # Recommended if supported:
        # config={"temperature": 0.2, "max_output_tokens": 220}
    )

    raw_answer = (response.text or "").strip()

    if not raw_answer:
        return FALLBACK_RESPONSE

    return soften_absence(raw_answer)
