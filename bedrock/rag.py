from .kb_retrieve import retrieve_context
from .claude_generate import generate_answer

def ask_portfolio(question: str) -> str:
    question = question.strip()

    # Safety guard
    if len(question) < 2:
        return "Please ask a complete question."

    print(f"DEBUG: rag.py calling retrieve_context for: '{question}'", flush=True)
    
    # --- DEBUG PROBE START ---
    import os
    kb_id = os.environ.get("BEDROCK_KB_ID", "MISSING")
    region = os.environ.get("AWS_REGION", "MISSING")
    
    try:
        context = retrieve_context(question)
        return f"DEBUG PROBE:\nKB_ID: {kb_id}\nREGION: {region}\nContext Length: {len(context)}\nContent: {context[:100]}..."
    except Exception as e:
        return f"DEBUG PROBE ERROR:\nKB_ID: {kb_id}\nREGION: {region}\nError: {str(e)}"
    # --- DEBUG PROBE END ---

    # context = retrieve_context(question)

    # Pass context (even if empty) to the LLM so it can handle greetings/general queries
    return generate_answer(context or "", question)

