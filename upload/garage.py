import boto3
from botocore.exceptions import ClientError
import config


garage = boto3.resource(
    service_name='s3',
    aws_access_key_id=config.GARAGE_KEY_ID,
    aws_secret_access_key=config.GARAGE_SECRET_KEY,
    endpoint_url=config.GARAGE_ENDPOINT_URL,
    region_name='garage',
)

bucket = garage.Bucket(config.GARAGE_BUCKET_NAME)


def upload_file(byt: bytes, path: str, content_type: str):
    bucket.put_object(Body=byt, Key=path, ContentType=content_type)


def exists_file(path: str) -> bool:
    obj = bucket.Object(path)
    try:
        obj.load()
    except ClientError as e:
        if e.response.get("Error", {}).get("Code") in {"404", "NoSuchKey", "NotFound"}:
            return False
        raise
    return True
