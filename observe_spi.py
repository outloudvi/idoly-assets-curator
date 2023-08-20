import json
import sys
import requests

import config
from observe import OCTO_API_ENDPOINT, process_spi

if __name__ == '__main__':
    db_items = json.loads(
        requests.get(OCTO_API_ENDPOINT,
                     headers={
                         "Authorization": f"Bearer {config.API_SECRET}"
                     }).content
    )
    success = process_spi(db_items)
    if not success:
        sys.exit(1)
