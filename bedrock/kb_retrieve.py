import boto3
import os

REGION = os.getenv("AWS_REGION", "us-east-2")

def get_bedrock_client():
    kb_id = os.getenv("BEDROCK_KB_ID")
    if not kb_id:
        raise RuntimeError("BEDROCK_KB_ID is not set")

    client = boto3.client(
        "bedrock-agent-runtime",
        region_name=REGION
    )

    return client, kb_id


def retrieve_context(question: str) -> str:
    client, kb_id = get_bedrock_client()

    print(f"DEBUG: Retrieving context for query: '{question}'", flush=True)

    response = client.retrieve(
        knowledgeBaseId=kb_id,
        retrievalQuery={"text": question},
        retrievalConfiguration={
            "vectorSearchConfiguration": {
                "numberOfResults": 5
            }
        }
    )

    chunks = []
    results = response.get("retrievalResults", [])
    print(f"DEBUG: Found {len(results)} chunks.", flush=True)

    for item in results:
        text = item.get("content", {}).get("text")
        if text:
            chunks.append(text.strip())

    return "\n\n".join(chunks)
