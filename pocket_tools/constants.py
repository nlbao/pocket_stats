import sys
import logging
import os


CONSUMER_KEY = os.environ['POCKET_TOOLS_CONSUMER_KEY']
ACCESS_TOKEN = os.environ['POCKET_TOOLS_ACCESS_TOKEN']
CACHE_FILE = os.environ.get('POCKET_TOOLS_CACHE_FILE', os.path.expanduser('~/pocket-tools.cache'))

root = logging.getLogger()
root.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(name)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)
