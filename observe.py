import json
import requests
import sys
import time
from os import path


import UnityPy

import backblaze
import config
from console import console
import utils
import ffutils
import deobfuscate

ADV_METAFILE_PATH = 'assets/sud/meta.json'
OCTO_API_ENDPOINT = 'https://idoly-backend.outv.im/manage/raw?key=Octo'

def main():
    storage_metadata = json.loads(backblaze.get_file(ADV_METAFILE_PATH))
    db_items = json.loads(
        requests.get(OCTO_API_ENDPOINT,
            headers={
                "Authorization": f"Bearer {config.API_SECRET}"
            }).content
    )
    
    failure = 0
    for item in filter(lambda x: x['name'].startswith("sud_"), db_items['assetBundleList']):
        name = item['name']
        storage_info = storage_metadata.get(name)
        if storage_info is not None:
            if storage_info == item['md5']:
                console.log(f"Skipping {name}")
                continue
            else:
                console.log(f"Updating {name}")
        else:
            console.log(f"Uploading {name}")
        
        # Process an item
        # I guess we don't need to run in parallel here, to be kind to the upstream server
        try:
            console.log(f"Handling {name}")
            origin_url = utils.get_origin_url(item)
            blob = requests.get(origin_url).content
            time.sleep(1) # lower the upstream request rate
            u3d_blob = deobfuscate.deobfuscate(blob, item)
            if u3d_blob[0:7] != b'UnityFS':
                console.warn(f"Skipping {name} due to invalid UnityFS header")
                failure += 1
                continue
            up = UnityPy.load(u3d_blob)
            for clip in filter(lambda x: x.type.name == "AudioClip", up.objects):
                clip_item = clip.read()
                clip_name = clip_item.name
                clip_samples = clip_item.samples
                if len(clip_samples)>1:
                    console.warn(f"Clip sample > 1 is {len(clip_samples)}", clip_name, item["name"], clip_samples.keys())
                wav_blob = list(clip_samples.values())[0]
                opus_blob = ffutils.wav_to_opus(wav_blob)
                pathname = path.join("assets/", *utils.id_to_path_segs(clip_name)) + ".opus"
                backblaze.upload_file(
                    opus_blob,
                    pathname,
                    "audio/ogg"
                )
                console.log(f"Uploaded {clip_item.name} to {pathname}")
        except Exception as e:
            console.error(f"Exception on {name}: {e}")
            failure += 1
        storage_metadata[name] = item['md5']

    # Finally...
    backblaze.upload_file(json.dumps(storage_metadata), ADV_METAFILE_PATH, "application/json")
    if failure == 0:
        console.log("Everything goes well")
    else:
        console.error(f"{failure} items failed to process")
        sys.exit(1)


if __name__ == '__main__':
    main()