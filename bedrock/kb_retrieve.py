import boto3
import os

REGION = os.getenv("AWS_REGION", "us-east-2")
KB_ID = os.getenv("BEDROCK_KB_ID")

if not KB_ID:
    raise RuntimeError("BEDROCK_KB_ID is not set")

client = boto3.client("bedrock-agent-runtime", region_name=REGION)

def retrieve_context(question: str) -> str:
    response = client.retrieve(
        knowledgeBaseId=KB_ID,
        retrievalQuery={"text": question},
        retrievalConfiguration={
            "vectorSearchConfiguration": {
                "numberOfResults": 5
            }
        }
    )

    chunks = []
    for item in response.get("retrievalResults", []):
        text = item.get("content", {}).get("text")
        if text:
            chunks.append(text.strip())

    return "\n\n".join(chunks)

