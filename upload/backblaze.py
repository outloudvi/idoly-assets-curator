import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
import config

b2 = boto3.resource(
    service_name='s3',
    aws_access_key_id=config.B2_KEY_ID,
    aws_secret_access_key=config.B2_APP_KEY,
    endpoint_url=config.B2_ENDPOINT_URL,
    config=Config(
        signature_version='s3v4')
)
bucket = b2.Bucket(config.B2_BUCKET_NAME)


def upload_file(byt: bytes, path: str, content_type: str):
    bucket.put_object(Body=byt, Key=path, ContentType=content_type)


def exists_file(path: str) -> bool:
    obj = bucket.Object(path)
    try:
        obj.load()
    except ClientError as e:
        if e.response.get("Error")["Code"] == "404":
            return False
    return True
