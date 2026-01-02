from .kb_retrieve import retrieve_context
from .claude_generate import generate_answer

def ask_portfolio(question: str) -> str:
    question = question.strip()

    # Safety guard
    if len(question) < 2:
        return "Please ask a complete question."

    print(f"DEBUG: rag.py calling retrieve_context for: '{question}'", flush=True)
    
    print(f"DEBUG: rag.py calling retrieve_context for: '{question}'", flush=True)
    
    context = retrieve_context(question)

    # Pass context (even if empty) to the LLM so it can handle greetings/general queries
    return generate_answer(context or "", question)

