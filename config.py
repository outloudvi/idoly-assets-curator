from os import getenv as _getenv
from typing import Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

def getenv(env_name: str, default_value: Optional[str] = None):
    v =  _getenv(env_name) or default_value
    if v is None:
        raise ValueError(f"No env {env_name} and no fallback")
    return v

B2_ASSET_DIR = getenv('B2_ASSET_DIR', 'assets')
RATE_LIMIT_DB_PATH = getenv('RATE_LIMIT_DB_PATH', '/tmp/idoly-asset-curator-rate-limit.sqlite3')
B2_BASEURL = getenv('B2_BASEURL')
B2_ENDPOINT_URL = getenv('B2_ENDPOINT_URL')
B2_KEY_ID = getenv('B2_KEY_ID')
B2_APP_KEY = getenv('B2_APP_KEY')
B2_BUCKET_NAME = getenv('B2_BUCKET_NAME')
GARAGE_BASEURL = getenv('GARAGE_BASEURL')
GARAGE_ENDPOINT_URL = getenv('GARAGE_ENDPOINT_URL')
GARAGE_KEY_ID = getenv('GARAGE_KEY_ID')
GARAGE_SECRET_KEY = getenv('GARAGE_SECRET_KEY')
GARAGE_BUCKET_NAME = getenv('GARAGE_BUCKET_NAME')
CL_BASEURL = getenv('CL_BASEURL')
CL_ASSET_DIR = getenv('CL_ASSET_DIR')
API_LOOKUP_URL = getenv('API_LOOKUP_URL')
API_SECRET = getenv('API_SECRET')
CL_CLOUD_NAME = getenv('CL_CLOUD_NAME')
CL_API_KEY = getenv('CL_API_KEY')
CL_API_SECRET = getenv('CL_API_SECRET')
MATOMO_DOMAIN = getenv('MATOMO_DOMAIN')
MATOMO_WEBSITE_ID = getenv('MATOMO_WEBSITE_ID')
MATOMO_TOKEN = getenv('MATOMO_TOKEN')
IS_BEHIND_CLOUDFLARE = getenv('IS_BEHIND_CLOUDFLARE')
BYPASS_RATE_LIMIT_IP_RANGE = getenv('BYPASS_RATE_LIMIT_IP_RANGE', "")
