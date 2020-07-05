import json
import logging
from pocket import Pocket
from typing import List, Dict
from constants import CACHE_FILE, CONSUMER_KEY, ACCESS_TOKEN


api = Pocket(consumer_key=CONSUMER_KEY, access_token=ACCESS_TOKEN)


def fetch_data(offset: int = 0, limit: int = None, overwrite_cache: bool = False) -> List[Dict]:
    ans = []
    count = limit if (limit is not None) else 100
    while True:
        response = api.retrieve(offset=offset, count=count)
        items = response.get('list', [])
        ans.extend(item for k, item in items.items())
        if (limit is not None) or (len(items) == 0):
            break
    if overwrite_cache:
        logging.info(f'Writing data to cache file {CACHE_FILE}')
        with open(CACHE_FILE, 'w') as fo:
            json.dump(ans, fo)
    return ans
