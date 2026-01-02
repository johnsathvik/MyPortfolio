import boto3
import os

REGION = os.getenv("AWS_REGION", "us-east-2")
KB_ID = os.getenv("BEDROCK_KB_ID")

if not KB_ID:
    raise RuntimeError("BEDROCK_KB_ID is not set")

client = boto3.client("bedrock-agent-runtime", region_name=REGION)

print(f"DEBUG: Initialized Bedrock Client. Region: {REGION}, KB_ID: {KB_ID}")

def retrieve_context(question: str) -> str:
    print(f"DEBUG: Retrieving context for query: '{question}'")
    
    try:
        response = client.retrieve(
            knowledgeBaseId=KB_ID,
            retrievalQuery={"text": question},
            retrievalConfiguration={
                "vectorSearchConfiguration": {
                    "numberOfResults": 5
                }
            }
        )
    except Exception as e:
        print(f"DEBUG: Retrieval Error: {e}")
        raise e

    chunks = []
    results = response.get("retrievalResults", [])
    print(f"DEBUG: Found {len(results)} chunks.")
    
    for item in results:
        text = item.get("content", {}).get("text")
        if text:
            chunks.append(text.strip())

    return "\n\n".join(chunks)

