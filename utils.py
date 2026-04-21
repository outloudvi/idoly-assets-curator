import config
from typing import Tuple, Union, List
import json

from flask import g, redirect, Response, Request
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


def log_to_umami(request: Request, duration: int):
    if config.UMAMI_WEBSITE_ID is None or config.UMAMI_DOMAIN is None:
        return
    body = {
        "payload": {
            "website": config.UMAMI_WEBSITE_ID,
            "url": request.url,
            "referrer": request.referrer or "",
            "ip": request.remote_addr,
            "user_agent": request.headers.get("User-Agent", "Unknown-User-Agent/0.1"),
            "data": {
                "duration": duration,
                "storage_hit": g.get("storage_hit", False)
            }
        },
        "type": "event"
    }
    requests.post(
        f"https://{config.UMAMI_DOMAIN}/api/send",
        json=body,
        timeout=2
    )
