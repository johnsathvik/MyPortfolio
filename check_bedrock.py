import boto3
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_bedrock():
    print("--- Bedrock Knowledge Base Diagnostic ---")
    
    # 1. Check Environment Variables
    region = os.getenv("AWS_REGION", "us-east-2")
    kb_id = os.getenv("BEDROCK_KB_ID")
    
    print(f"Region: {region}")
    
    if not kb_id:
        print("[FAIL] BEDROCK_KB_ID is NOT set in environment variables.")
        return
    
    # Show last 4 chars for safety/verification
    print(f"KB ID found: ...{kb_id[-4:] if len(kb_id) > 4 else kb_id}")
    
    # 2. Initialize Client
    try:
        client = boto3.client("bedrock-agent-runtime", region_name=region)
        print("[OK] Bedrock Agent Runtime client initialized.")
    except Exception as e:
        print(f"[FAIL] Failed to initialize client: {e}")
        return

    # 3. Test Retrieval
    query = "John"
    print(f"\nAttempting retrieval for query: '{query}'...")
    
    try:
        response = client.retrieve(
            knowledgeBaseId=kb_id,
            retrievalQuery={"text": query},
            retrievalConfiguration={
                "vectorSearchConfiguration": {
                    "numberOfResults": 5
                }
            }
        )
        
        results = response.get("retrievalResults", [])
        count = len(results)
        
        print(f"Retrieval Status: {response['ResponseMetadata']['HTTPStatusCode']}")
        print(f"Chunks Retrieved: {count}")
        
        if count == 0:
            print("[WARN] 0 chunks returned. This explains why the assistant says 'not documented'.")
            print("Possible causes:")
            print("  - KB ID is incorrect (points to empty KB)")
            print("  - Data source sync failed or hasn't run")
            print("  - Permissions issue (though usually throws error)")
        else:
            print("[OK] Retrieval successful!")
            print("--- First Chunk Preview ---")
            print(results[0].get("content", {}).get("text", "")[:100] + "...")
            
    except Exception as e:
        print(f"[FAIL] Retrieval failed with error: {e}")

if __name__ == "__main__":
    check_bedrock()
