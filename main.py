import io
import json
import requests
import UnityPy
from os import path
from typing import Union
from console import console
from urllib.parse import urljoin
from deobfuscate import deobfuscate
from upload_file import upload_file
from utils import file_exists, get_origin_url, id_to_path_segs


import config


def get_item(name: str) -> Union[dict, None]:
    resp = requests.get(f"{config.API_LOOKUP_URL}?name={name}",
                        headers={
                            "Authorization": f"Bearer {config.API_SECRET}"
                        })
    if resp.status_code != 200:
        return None
    return json.loads(resp.text)


def get_image_url(id: str, force_upload: bool = False) -> Union[str, None]:
    console.debug(f"Requesting {id}")
    path_segs = id_to_path_segs(id)
    asset_path = path.join(
        config.ASSET_DIR, *path_segs
    ) + ".png"
    assets_url = urljoin(config.BASEURL, asset_path)
    if not force_upload:
        console.debug(f"Checking {assets_url}")
        if file_exists(assets_url):
            console.debug(f"Found {assets_url} , exiting")
            return assets_url
        console.debug(f"Not found {assets_url} , gonna download it")
    item = get_item(id)
    if item is None:
        console.debug(f"Not found {id} in database")
        return None
    console.debug(f"Found {id} in database")
    origin_url = get_origin_url(item)
    console.debug(f"Download the asset from: {origin_url}")
    resp = requests.get(origin_url)
    if resp.status_code != 200:
        console.debug(f"Failed to fetch, quiting", resp)
        return None
    resource = resp.content
    deobfs_resource = deobfuscate(resource, item)
    if deobfs_resource is None:
        console.debug(f"Failed to deobfuscate, quiting")
        return None
    console.debug("Deobfuscated")
    env = UnityPy.load(deobfs_resource)
    env_texture2ds = list(
        filter(lambda x: x.type.name == "Texture2D", env.objects))
    if len(env_texture2ds) == 0:
        console.debug("No texture2ds found from", env.objects)
        return None
    if len(env_texture2ds) > 1:
        console.warn("Multiple texture2ds found from", env.objects)
    pic_object = env_texture2ds[0]
    pic_data = pic_object.read().image
    png_bytesio_w = io.BytesIO()
    pic_data.save(png_bytesio_w, format='PNG')
    console.debug(f"Uploading to {asset_path}")
    upload_file(
        png_bytesio_w.getvalue(),
        asset_path
    )
    return assets_url


print(get_image_url("img_banner_s_birthday-21-0913-suz"))
