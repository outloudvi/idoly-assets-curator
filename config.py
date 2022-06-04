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
BASEURL = getenv('BASEURL')
ASSET_DIR = getenv('ASSET_DIR')
API_LOOKUP_URL = getenv('API_LOOKUP_URL')
API_SECRET = getenv('API_SECRET')
CLOUDINARY_CLOUD_NAME = getenv('CLOUDINARY_CLOUD_NAME')
CLOUDINARY_API_KEY = getenv('CLOUDINARY_API_KEY')
CLOUDINARY_API_SECRET = getenv('CLOUDINARY_API_SECRET')
