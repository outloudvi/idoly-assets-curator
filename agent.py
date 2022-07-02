from typing import Tuple
from console import console
from deobfuscate import deobfuscate
from utils import get_item, get_origin_url

import requests
import UnityPy


class Agent:

    def __init__(self, slug) -> None:
        self.slug = slug

    def pre_check(self) -> bool:
        return True

    def shall_upload(self) -> bool:
        return True

    def pick_item(self, items):
        return items[0]

    def object_to_bytes(self, obj):
        pass

    def upload_object(self, byt):
        pass

    def generate_url(self):
        pass

    def process(self) -> Tuple[int, str]:
        console.debug("pre_check")
        if self.pre_check() == False:
            return 400, "Bad slug"

        if not self.shall_upload():
            return 302, self.generate_url()

        console.debug("get_item_meta")
        item = get_item(self.slug)
        if item is None:
            return 400, "Not found in database"

        console.debug("get_item")
        origin_url = get_origin_url(item)
        resp = requests.get(origin_url)
        if resp.status_code != 200:
            console.debug(f"Failed to fetch item", resp)
            return 500, "Failed to fetch item"
        resource = resp.content

        console.debug("deobfuscate")
        deobfs_res = deobfuscate(resource, item)
        if deobfs_res is None:
            return 500, "Failed to deobfuscate item"

        console.debug("load & select")
        env = UnityPy.load(deobfs_res)
        target_object = self.pick_item(env.objects)
        data = self.object_to_bytes(target_object)

        console.debug("upload")
        self.upload_object(data)

        return 302, self.generate_url()
