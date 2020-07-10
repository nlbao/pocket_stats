import sys
import logging
import os
import pytz


DEFAULT_TZINFO = pytz.utc
CONSUMER_KEY = os.environ.get('POCKET_STATS_CONSUMER_KEY', None)
ACCESS_TOKEN = os.environ.get('POCKET_STATS_ACCESS_TOKEN', None)
CACHE_FILE = os.environ.get('POCKET_STATS_CACHE_FILE', os.path.expanduser('~/pocket-tools.cache'))
DEFAULT_READING_SPEED = 225  # words per minute


root = logging.getLogger()
root.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(name)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)
