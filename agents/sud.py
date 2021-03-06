from urllib.parse import urljoin
from os import path

import config
from agent import Agent
from utils import id_to_path_segs
from upload.backblaze import exists_file, upload_file
from ffutils import wav_to_mp3, wav_to_opus

PATH_PREFIX = "assets/"


class SoundAgent(Agent):
    asset_path = ""
    filter_asset_type = "AudioClip"

    def __init__(self, slug) -> None:
        super().__init__(slug)
        path_segs = id_to_path_segs(self.slug)
        self.asset_path = path.join(
            PATH_PREFIX, *path_segs
        )

    def pre_check(self) -> bool:
        return self.slug.startswith("sud_")

    def shall_upload(self) -> bool:
        if self.ext != "opus":
            # Only upload/convert on requesting opus, not mp3
            return False
        return not exists_file(self.asset_path + ".opus")

    def pick_item(self, items):
        return list(filter(lambda x: x.type.name == self.filter_asset_type, items))[0]

    def object_to_bytes(self, obj):
        return list(obj.read().samples.values())[0]

    def upload_object(self, byt):
        opus_byt = wav_to_opus(byt)
        upload_file(
            opus_byt,
            self.asset_path + ".opus",
            "audio/ogg"
        )
        mp3_byt = wav_to_mp3(byt)
        upload_file(
            mp3_byt,
            self.asset_path + ".mp3",
            "audio/mpeg"
        )

    def generate_url(self):
        if self.ext == "mp3":
            return urljoin(config.B2_BASEURL, self.asset_path + ".mp3")
        else:
            return urljoin(config.B2_BASEURL, self.asset_path + ".opus")
