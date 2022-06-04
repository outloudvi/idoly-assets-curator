import cloudinary
from cloudinary.uploader import upload
import config

cloudinary.config(
    cloud_name=config.CLOUDINARY_CLOUD_NAME,
    api_key=config.CLOUDINARY_API_KEY,
    api_secret=config.CLOUDINARY_API_SECRET,
    secure=True
)


def upload_file(byt: bytes, path: str):
    upload(byt, public_id=path)
