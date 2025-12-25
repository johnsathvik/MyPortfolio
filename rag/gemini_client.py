from google import genai
from .config import get_gemini_api_key


def get_gemini_client():
    api_key = get_gemini_api_key()

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY not set. Add it to .env or environment variables."
        )

    return genai.Client(api_key=api_key)
