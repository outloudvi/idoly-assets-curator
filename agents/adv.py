from os import path
from typing import Tuple
import requests
from urllib.parse import urljoin

import config
from agent import Agent
from console import console
from utils import get_item, get_origin_url, id_to_path_segs
from upload.backblaze import exists_file, upload_file

PATH_PREFIX = "assets/"

# Note that Adv files need no post-processing work.
class AdvAgent(Agent):
    asset_path = ""
    full_path = ""

    def __init__(self, slug) -> None:
        super().__init__(slug)
        path_segs = id_to_path_segs(self.slug)
        self.asset_path = path.join(
            PATH_PREFIX, *path_segs
        )
        self.full_path = f"{self.asset_path}.{self.ext}"
    
    def pre_check(self) -> bool:
        return self.slug.startswith("adv_") and self.ext == "txt"
    
    def shall_upload(self) -> bool:
        return not exists_file(self.full_path)
    
    def generate_url(self):
        return urljoin(config.B2_BASEURL, self.full_path)

    def upload_object(self, byt):
        upload_file(
            byt,
            self.full_path,
            "text/plain"
        )

    def process(self) -> Tuple[int, str]:
        console.debug("pre_check")
        if self.pre_check() == False:
            return 400, "Bad slug"

        if not self.shall_upload():
            return 302, self.generate_url()

        console.debug("get_item_meta")
        item = get_item(f"{self.slug}.{self.ext}", "resource")
        if item is None:
            return 400, "Not found in database"

        console.debug("get_item")
        origin_url = get_origin_url(item, "resources")
        resp = requests.get(origin_url)
        if resp.status_code != 200:
            console.debug(f"Failed to fetch item", resp)
            return 500, "Failed to fetch item"
        data = resp.content

        console.debug("upload")
        self.upload_object(data)

        return 302, self.generate_url()

