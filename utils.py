import config
from typing import Tuple, Union, List
import json

from flask import redirect, Response
import requests

POSITIVE_CACHE_TIME = 30 * 24 * 60 * 60  # 30 days
POSITIVE_ALT_CACHE_TIME = 3 * 24 * 60 * 60  # 3 hours
NEGATIVE_CACHE_TIME = 30 * 60  # 30 minutes


def post_agent(ret: Tuple[int, str]):
    if ret[0] == 308:
        response = redirect(ret[1], code=ret[0])
        response.headers.add('Cache-Control',
                             f's-maxage={POSITIVE_CACHE_TIME}, stale-while-revalidate={POSITIVE_ALT_CACHE_TIME}')
        return response
    else:
        response = Response(ret[1])
        response.status_code = ret[0]
        response.headers.add(
            'Cache-Control', f's-maxage={NEGATIVE_CACHE_TIME}')
        return response


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
