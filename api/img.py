import io
from urllib.parse import urljoin
from os import path
import requests

import config
from agent import Agent
from utils import id_to_path_segs
from upload.cloudinary import upload_file


class ImageAgent(Agent):
    asset_path = ""
    filter_asset_type = "Texture2D"

    def __init__(self, slug) -> None:
        super().__init__(slug)
        self.check_url = slug
        path_segs = id_to_path_segs(slug)
        self.asset_path = path.join(
            config.CL_ASSET_DIR, *path_segs
        )

    def pre_check(self) -> bool:
        return self.slug.startswith("img_")

    def shall_upload(self) -> bool:
        assets_url = urljoin(config.CL_BASEURL, self.asset_path + ".png")
        resp = requests.get(assets_url, headers={
            "Range": "Bytes=0-1"
        })
        return resp.status_code != 206

    def pick_item(self, items):
        return list(filter(lambda x: x.type.name == self.filter_asset_type, items))[0]

    def object_to_bytes(self, obj):
        return obj.read().image

    def upload_object(self, byt):
        png_bytesio_w = io.BytesIO()
        byt.save(png_bytesio_w, format='PNG')
        upload_file(
            png_bytesio_w.getvalue(),
            self.asset_path,
            "image/png"
        )

    def generate_url(self):
        return urljoin(config.CL_BASEURL, f"f_auto/{self.asset_path}.png")
