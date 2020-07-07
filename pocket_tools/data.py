import nltk
import os
import json
import logging
import tldextract
from datetime import datetime
from pocket import Pocket
from typing import List, Dict
from collections import Counter
from nltk.corpus import stopwords
import pandas as pd
from constants import CACHE_FILE, CONSUMER_KEY, ACCESS_TOKEN, DEFAULT_READING_SPEED


api = Pocket(consumer_key=CONSUMER_KEY, access_token=ACCESS_TOKEN)
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
invalid_words = stopwords.words('english')


def fetch_data(offset: int = 0, limit: int = None, overwrite_cache: bool = False) -> List[Dict]:
    ans = []
    count = 500
    if limit is not None:
        limit += offset
        count = min(count, limit)
    while (limit is None) or (offset < limit):
        response = api.retrieve(
            offset=offset, count=count,
            state='all',  # both unread and archived items
        )
        items = response.get('list', {})
        n = len(items)
        if n == 0:
            break
        ans.extend(item for k, item in items.items())
        logging.info(f'Fetched {n} records. Total = {len(ans)} now.')
        offset += n
    if overwrite_cache:
        logging.info(f'Writing data to cache file {CACHE_FILE}')
        with open(CACHE_FILE, 'w') as fo:
            json.dump(ans, fo)
    return ans


def load_cache() -> List[Dict]:
    if not os.path.isfile(CACHE_FILE):
        return []
    with open(CACHE_FILE, 'r') as fi:
        return json.load(fi)


def is_valid_word(w):
    if len(w) == 0:
        return False
    if w in invalid_words:
        return False
    return True


def count_words_in_title(data: List[Dict]) -> Dict[str, int]:
    words = []
    for record in data:
        title = record['given_title']
        words.extend(x.strip().lower() for x in title.split(' ') if is_valid_word(x.strip().lower()))
    return Counter(words)


def get_word_counts(data: List[Dict]) -> List[int]:
    return [int(record.get('word_count', -99999)) for record in data]


def get_reading_time(data: List[Dict], reading_speed: int = DEFAULT_READING_SPEED) -> List[int]:
    # because some records in data don't have the 'time_to_read' field
    word_counts = get_word_counts(data)
    return [wc / DEFAULT_READING_SPEED for wc in word_counts if wc > 0]


def get_added_time_series(data: List[Dict]) -> pd.DataFrame:
    added_date_counts = Counter(datetime.fromtimestamp(int(record['time_added'])).strftime('%Y%m%d') for record in data)
    df = pd.DataFrame.from_dict({datetime.strptime(d, '%Y%m%d'): cnt for d, cnt in added_date_counts.items()},
                                orient='index', columns=['added_articles_count'])
    return df


def get_archived_time_series(data: List[Dict]) -> pd.DataFrame:
    added_date_counts = Counter(
        datetime.fromtimestamp(int(record['time_updated'])).strftime('%Y%m%d')
        for record in data if int(record['status']) == 1
    )
    df = pd.DataFrame.from_dict({datetime.strptime(d, '%Y%m%d'): cnt for d, cnt in added_date_counts.items()},
                                orient='index', columns=['archived_articles_count'])
    return df


def get_domain_from_url(url: str) -> str:
    extract_result = tldextract.extract(url)
    return extract_result.domain + '.' + extract_result.suffix


def get_domain_counts(data: List[Dict]) -> Dict[str, int]:
    return Counter(get_domain_from_url(record['resolved_url']) for record in data)


def normalize_language_name(lang: str) -> str:
    lang = lang.strip()
    if len(lang) == 0:
        return 'unknown'
    return lang


def get_language_counts(data: List[Dict]) -> Dict[str, int]:
    return Counter(normalize_language_name(record['lang']) for record in data)
