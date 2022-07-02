import cloudinary
from cloudinary.uploader import upload
import config

cloudinary.config(
    cloud_name=config.CL_CLOUD_NAME,
    api_key=config.CL_API_KEY,
    api_secret=config.CL_API_SECRET,
    secure=True
)


def upload_file(byt: bytes, path: str, content_type: str):
    upload(byt, public_id=path)
