import io
from posixpath import join
from urllib.parse import quote, urljoin

import config
from agent import Agent
from utils import id_to_path_segs
from upload.garage import exists_file, upload_file


class ImageAgent(Agent):
    asset_path = ""
    filter_asset_type = "Texture2D"

    def __init__(self, slug) -> None:
        super().__init__(slug)
        path_segs = id_to_path_segs(self.slug)
        self.asset_path = join(
            config.B2_ASSET_DIR.strip('/'), *path_segs
        ) + '.webp'

    def pre_check(self) -> bool:
        return self.slug.startswith("img_")

    def shall_upload(self) -> bool:
        return not exists_file(self.asset_path)

    def pick_item(self, items):
        return list(filter(lambda x: x.type.name == self.filter_asset_type, items))[0]

    def object_to_bytes(self, obj):
        return obj.read().image

    def upload_object(self, byt):
        png_bytesio_w = io.BytesIO()
        byt.save(png_bytesio_w, format='WEBP')
        upload_file(
            png_bytesio_w.getvalue(),
            self.asset_path,
            "image/webp"
        )

    def generate_url(self):
        return urljoin(config.GARAGE_BASEURL.rstrip('/') + '/', quote(self.asset_path))
