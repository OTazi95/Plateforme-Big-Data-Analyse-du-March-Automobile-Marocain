import boto3
import json
import os
from datetime import datetime

MINIO_ENDPOINT = "http://minio:9000"
MINIO_ACCESS = "minioadmin"
MINIO_SECRET = "minioadmin"
BUCKET = "bronze"

def get_minio_client():
    return boto3.client(
        "s3",
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_ACCESS,
        aws_secret_access_key=MINIO_SECRET,
    )

def ensure_bucket(client, bucket):
    try:
        client.head_bucket(Bucket=bucket)
    except:
        client.create_bucket(Bucket=bucket)

def save_to_bronze(articles: list, source: str):
    """Sauvegarde les articles bruts dans MinIO (couche Bronze)"""
    client = get_minio_client()
    ensure_bucket(client, BUCKET)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{source}_{timestamp}.json"
    data = json.dumps(articles, ensure_ascii=False, indent=2)
    client.put_object(
        Bucket=BUCKET,
        Key=f"auto/{source}/{filename}",
        Body=data.encode("utf-8"),
        ContentType="application/json",
    )
    print(f"✅ Sauvegardé dans Bronze: auto/{source}/{filename}")