import config
from typing import Tuple, Union, List
import json
import requests


def id_to_path_segs(id: str) -> List[str]:
    splits = id.split("_", 2)
    if len(splits) < 3:
        return ["_", id]
    return splits


def get_origin_url(item, typ: str = "assetbundle") -> str:
    upload_version_id = item["uploadVersionId"]
    object_name = item["objectName"]
    generation = item["generation"]
    return f"https://{config.UPSTREAM_BASE_DOMAIN}/solis-{upload_version_id}-{typ}/{object_name}?generation={generation}&alt=media"