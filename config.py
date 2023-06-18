from os import getenv

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

B2_BASEURL = getenv('B2_BASEURL')
B2_ENDPOINT_URL = getenv('B2_ENDPOINT_URL')
B2_KEY_ID = getenv('B2_KEY_ID')
B2_APP_KEY = getenv('B2_APP_KEY')
B2_BUCKET_NAME = getenv('B2_BUCKET_NAME')
B2_REGION = getenv('B2_REGION')
UPSTREAM_BASE_DOMAIN = getenv('UPSTREAM_BASE_DOMAIN')
API_SECRET = getenv('API_SECRET')
OCTO_REVISION = getenv('OCTO_REVISION')
FORCED = getenv('FORCED')