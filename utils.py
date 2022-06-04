from typing import List
import requests


def id_to_path_segs(id: str) -> List[str]:
    splits = id.split("_", 2)
    if len(splits) < 3:
        return ["_", "id"]
    return splits


def get_origin_url(item) -> str:
    upload_version_id = item["uploadVersionId"]
    typ = "assetbundle"
    object_name = item["objectName"]
    generation = item["generation"]
    return f"https://d2ilil7yh5oi1v.cloudfront.net/solis-{upload_version_id}-{typ}/{object_name}?generation={generation}&alt=media"


def file_exists(url: str) -> bool:
    resp = requests.get(url, headers={
        "Range": "Bytes=0-1"
    })
    return resp.status_code == 206
