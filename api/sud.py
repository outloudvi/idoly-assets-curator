import io
from urllib.parse import urljoin
from os import path
import requests

import config
from agent import Agent
from utils import id_to_path_segs
from upload.backblaze import upload_file

PATH_PREFIX = "assets/"


class SoundAgent(Agent):
    asset_path = ""
    filter_asset_type = "AudioClip"

    def __init__(self, slug) -> None:
        super().__init__(slug)
        self.check_url = slug
        path_segs = id_to_path_segs(slug)
        self.asset_path = path.join(
            PATH_PREFIX, *path_segs
        )

    def pre_check(self) -> bool:
        return self.slug.startswith("sud_")

    def shall_upload(self) -> bool:
        assets_url = urljoin(config.B2_BASEURL, self.asset_path + ".wav")
        resp = requests.get(assets_url, headers={
            "Range": "Bytes=0-1"
        })
        return resp.status_code != 206

    def pick_item(self, items):
        return list(filter(lambda x: x.type.name == self.filter_asset_type, items))[0]

    def object_to_bytes(self, obj):
        return list(obj.read().samples.values())[0]

    def upload_object(self, byt):
        upload_file(
            byt,
            self.asset_path + ".wav",
            "audio/wav"
        )

    def generate_url(self):
        return urljoin(config.B2_BASEURL, self.asset_path + ".wav")
