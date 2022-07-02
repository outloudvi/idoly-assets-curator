from os import getenv

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

B2_ENDPOINT_URL = getenv('B2_ENDPOINT_URL')
B2_KEY_ID = getenv('B2_KEY_ID')
B2_APP_KEY = getenv('B2_APP_KEY')
B2_BUCKET_NAME = getenv('B2_BUCKET_NAME')
CL_BASEURL = getenv('CL_BASEURL')
CL_ASSET_DIR = getenv('CL_ASSET_DIR')
API_LOOKUP_URL = getenv('API_LOOKUP_URL')
API_SECRET = getenv('API_SECRET')
CL_CLOUD_NAME = getenv('CL_CLOUD_NAME')
CL_API_KEY = getenv('CL_API_KEY')
CL_API_SECRET = getenv('CL_API_SECRET')
