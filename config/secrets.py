import boto3
import os
import logging

log = logging.getLogger(__name__)

SSM_PATH = "/myportfolio/"

def load_secrets():
    try:
        ssm = boto3.client("ssm", region_name=os.getenv("AWS_REGION", "us-east-2"))

        response = ssm.get_parameters_by_path(
            Path=SSM_PATH,
            Recursive=True,
            WithDecryption=True
        )

        for param in response["Parameters"]:
            key = param["Name"].split("/")[-1].upper()
            os.environ[key] = param["Value"]

        log.info("SSM secrets loaded successfully")

    except Exception as e:
        log.warning(f"SSM not available, falling back to .env if present: {e}")
