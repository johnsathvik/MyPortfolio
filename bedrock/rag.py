from kb_retrieve import retrieve_context
from claude_generate import generate_answer

def ask_portfolio(question: str) -> str:
    question = question.strip()

    # Safety guard
    if len(question) < 2:
        return "Please ask a complete question."

    context = retrieve_context(question)

    if not context:
        return "That information is not documented in John’s portfolio."

    return generate_answer(context, question)

