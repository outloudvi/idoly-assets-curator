from io import BytesIO
import boto3
from botocore.config import Config
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


def upload_file(byt: bytes, path: str):
    bucket.put_object(Body=byt, Key=path, ContentType="image/png")
