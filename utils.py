import config
from typing import Tuple, Union, List
import json

from flask import redirect
import requests


def post_agent(ret: Tuple[int, str]):
    if ret[0] == 302:
        return redirect(ret[1], code=ret[0])
    else:
        return ret[1], ret[0]


def id_to_path_segs(id: str) -> List[str]:
    splits = id.split("_", 2)
    if len(splits) < 3:
        return ["_", "id"]
    return splits


def get_origin_url(item, typ: str = "assetbundle") -> str:
    upload_version_id = item["uploadVersionId"]
    object_name = item["objectName"]
    generation = item["generation"]
    return f"https://d2ilil7yh5oi1v.cloudfront.net/solis-{upload_version_id}-{typ}/{object_name}?generation={generation}&alt=media"


def get_item(name: str, typ: str = "asset") -> Union[dict, None]:
    resp = requests.get(f"{config.API_LOOKUP_URL}/{typ}?name={name}",
                        headers={
                            "Authorization": f"Bearer {config.API_SECRET}"
                        })
    if resp.status_code != 200:
        return None
    return json.loads(resp.text)
