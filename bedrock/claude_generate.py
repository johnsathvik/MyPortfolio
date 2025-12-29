import json
import boto3
import os

REGION = os.getenv("AWS_REGION", "us-east-2")

# Bedrock Runtime client
runtime = boto3.client("bedrock-runtime", region_name=REGION)

# 🔒 STRONG SYSTEM PROMPT (THIS IS THE KEY)
SYSTEM_PROMPT = """
You are John Sathvik Madipalli’s portfolio assistant.

Your role:
Answer questions about John clearly, confidently, and concisely using ONLY the provided context.

ABSOLUTE RULES (NO EXCEPTIONS):
- Use ONLY the given context.
- NEVER say:
  "Based on the information"
  "Based on the provided context"
  "According to the portfolio"
  "The portfolio states"
  "The information suggests"
- NEVER explain how you got the answer.
- NEVER mention context, documents, sources, AI, models, or retrieval.
- If something is not documented, say exactly:
  "That information is not documented in John’s portfolio."

STYLE RULES:
- Write like a confident professional summary, not a report.
- First sentence must directly answer the question.
- Keep answers short and focused.
- Prefer outcomes and skills over explanations.
- Use bullet points ONLY for listing projects.

GREETING RULE:
If the user greets ("hi", "hello"):
Respond with:
"Hi! I’m John’s portfolio assistant. You can ask about his projects, AWS work, cloud architecture, or technical experience."
"""

# Claude 3 Haiku inference profile ARN (CHEAP + FAST + SUPPORTED)
INFERENCE_PROFILE_ARN = os.getenv(
    "BEDROCK_INFERENCE_PROFILE_ARN",
    "arn:aws:bedrock:us-east-2:373342145992:inference-profile/us.anthropic.claude-3-haiku-20240307-v1:0"
)

def generate_answer(context: str, question: str) -> str:
    """
    Generates a portfolio-focused answer using Claude 3 Haiku.
    """

    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "system": SYSTEM_PROMPT,
        "messages": [
            {
                "role": "user",
                # 🚨 NO extra instructions here — system prompt controls behavior
                "content": f"{context}\n\nQuestion: {question}"
            }
        ],
        "max_tokens": 300,
        "temperature": 0.2
    }

    response = runtime.invoke_model(
        modelId=INFERENCE_PROFILE_ARN,
        contentType="application/json",
        accept="application/json",
        body=json.dumps(body)
    )

    result = json.loads(response["body"].read())
    return result["content"][0]["text"].strip()

