import json
import requests
import sys
import time
from io import BytesIO
from os import path


import UnityPy
import backblaze
import config
from console import console
import utils
import ffutils
import deobfuscate

SUD_METAFILE_PATH = 'assets/sud/meta.json'
SPI_METAFILE_PATH = 'assets/spi/meta.json'
OCTO_API_ENDPOINT = 'https://idoly-backend.outv.im/manage/raw?key=Octo'


def build_spi_basepath(name):
    return name.split("_", 4)[0:4]


def process_sud(db_items):
    storage_metadata = json.loads(backblaze.get_file(SUD_METAFILE_PATH))

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
            time.sleep(1)  # lower the upstream request rate
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
                if len(clip_samples) > 1:
                    console.warn(
                        f"Clip sample > 1 is {len(clip_samples)}", clip_name, item["name"], clip_samples.keys())
                wav_blob = list(clip_samples.values())[0]
                opus_blob = ffutils.wav_to_opus(wav_blob)
                pathname = path.join(
                    "assets/", *utils.id_to_path_segs(clip_name)) + ".opus"
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
    backblaze.upload_file(json.dumps(storage_metadata),
                          SUD_METAFILE_PATH, "application/json")
    if failure == 0:
        console.log("Everything goes well")
        return True
    else:
        console.error(f"{failure} items failed to process")
        return False


def process_spi(db_items):
    storage_metadata = json.loads(backblaze.get_file(SPI_METAFILE_PATH))

    failure = 0
    for item in filter(lambda x: x['name'].startswith("spi_"), db_items['assetBundleList']):
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
            time.sleep(1)  # lower the upstream request rate
            u3d_blob = deobfuscate.deobfuscate(blob, item)
            if u3d_blob[0:7] != b'UnityFS':
                console.warn(f"Skipping {name} due to invalid UnityFS header")
                failure += 1
                continue
            up = UnityPy.load(u3d_blob)
            if name.endswith(".atlas"):
                # atlas file - plaintext
                obj = filter(lambda x: x.type.name ==
                             "TextAsset", up.objects).__next__()
                pathname = path.join(
                    "assets/", *build_spi_basepath(name), name)
                backblaze.upload_file(
                    obj.read().text,
                    pathname,
                    "text/plain"
                )
            elif name.endswith(".skl"):
                # skl file - JSON
                obj = filter(lambda x: x.type.name ==
                             "TextAsset", up.objects).__next__()
                pathname = path.join(
                    "assets/", *build_spi_basepath(name), name + ".json")
                backblaze.upload_file(
                    obj.read().text,
                    pathname,
                    "application/json"
                )
            else:
                # texture file - PNG
                obj = filter(lambda x: x.type.name ==
                             "Texture2D", up.objects).__next__()
                pathname = path.join(
                    "assets/", *build_spi_basepath(name), name + ".png")
                png_bytesio_w = BytesIO()
                obj.read().image.save(png_bytesio_w, format='PNG')
                backblaze.upload_file(
                    png_bytesio_w.getvalue(),
                    pathname,
                    "image/png"
                )
            console.log(f"Uploaded {name} to {pathname}")
        except Exception as e:
            console.error(f"Exception on {name}: {e}")
            failure += 1
        storage_metadata[name] = item['md5']

    # Finally...
    backblaze.upload_file(json.dumps(storage_metadata),
                          SPI_METAFILE_PATH, "application/json")
    if failure == 0:
        console.log("Everything goes well")
        return True
    else:
        console.error(f"{failure} items failed to process")
        return False


if __name__ == '__main__':
    db_items = json.loads(
        requests.get(OCTO_API_ENDPOINT,
                     headers={
                         "Authorization": f"Bearer {config.API_SECRET}"
                     }).content
    )
    success_sud = process_sud(db_items)
    success_spi = process_spi(db_items)
    if not (success_sud and success_spi):
        sys.exit(1)
