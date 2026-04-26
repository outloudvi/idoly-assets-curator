import config
from typing import Tuple, Union, List
import json
import threading
import random

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


def _send_matomo_log(url: str, params: dict):
    try:
        requests.post(url, params=params, timeout=2)
    except Exception as e:
        print(f"Matomo logging failed: {e}")


def log_to_matomo(request: Request, duration: int):
    if config.MATOMO_DOMAIN is None or config.MATOMO_WEBSITE_ID is None:
        return

    is_cloudflare = (config.IS_BEHIND_CLOUDFLARE or "").lower() == 'true'

    cip = request.headers.get(
        'Cf-Connecting-Ip') if is_cloudflare else ''
    country = (request.headers.get('Cf-Ipcountry')
               or '').lower() if is_cloudflare else ''

    params = {
        "idsite": config.MATOMO_WEBSITE_ID,
        "rec": 1,
        "url": request.url,
        "rand": str(random.random()),
        "apiv": 1,
        "urlref": request.headers.get('Referer'),
        "ua": request.headers.get('User-Agent'),
        "lang": request.headers.get('Accept-Language'),
        "token_auth": config.MATOMO_TOKEN,
        "cip": cip,
        "country": country,
        "pf_srv": duration * 1000
    }

    url = f"https://{config.MATOMO_DOMAIN}/matomo.php"
    threading.Thread(target=_send_matomo_log, args=(
        url, params), daemon=True).start()
