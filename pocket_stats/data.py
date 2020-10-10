import nltk
import errno
import os
import json
import logging
import tldextract
from datetime import datetime, timedelta
from pocket import Pocket
from typing import List, Dict
from collections import Counter
from nltk.corpus import stopwords
import pandas as pd
from constants import CACHE_FILE, CONSUMER_KEY, ACCESS_TOKEN, DEFAULT_READING_SPEED, DEFAULT_TZINFO


# ------- Helper functions ------- #
def download_ntlk():
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords')


download_ntlk()
invalid_words = stopwords.words('english')


def is_valid_word(w):
    if len(w) == 0:
        return False
    return w not in invalid_words


def normalize_language_name(lang: str) -> str:
    lang = lang.strip()
    if len(lang) == 0:
        return 'unknown'
    return lang


def get_domain_from_url(url: str) -> str:
    extract_result = tldextract.extract(url)
    return extract_result.domain + '.' + extract_result.suffix


def epoch_to_yyymmdd(epoch: int):
    return datetime.fromtimestamp(int(epoch), tz=DEFAULT_TZINFO).strftime('%Y%m%d')


# ------- Main functions ------- #
def fetch_data(offset: int = 0, limit: int = None, overwrite_cache: bool = False,
               consumer_key: str = CONSUMER_KEY, access_token: str = ACCESS_TOKEN) -> List[Dict]:
    assert (consumer_key is not None) and (access_token is not None), 'Please set value for these environment variables'
    api = Pocket(consumer_key=consumer_key, access_token=access_token)
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


def load_cache(cache_file: str = CACHE_FILE) -> List[Dict]:
    if not os.path.isfile(cache_file):
        logging.error("Missing cache file, please run 'python -m pocket_stats fetch-data --overwrite_cache'")
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT),
                                cache_file)
    with open(cache_file, 'r') as fi:
        return json.load(fi)


# filter format: [key, operation, expected_value]
def should_pass_filter(filter: List, record: Dict):
    key, op, expected = filter
    expected = str(expected) if expected is not None else None
    value = record.get(key, None)
    value = str(value) if value is not None else None
    if op == '=':
        return value == expected
    elif op == '!=':
        return value != expected
    else:
        raise NotImplementedError


def should_pass_filters(filters: List[List], record: Dict) -> bool:
    for f in filters:
        if not should_pass_filter(f, record):
            return False
    return True


def count_words_in_title(data: List[Dict]) -> Dict[str, int]:
    words = []
    for record in data:
        title = record['given_title']
        words.extend(x.strip().lower() for x in title.split(' ') if is_valid_word(x.strip().lower()))
    return Counter(words)


def get_word_counts(data: List[Dict], filters: List[List] = []) -> List[int]:
    return [int(record.get('word_count', -99999))
            for record in data
            if should_pass_filters(filters, record)]


def get_reading_time(data: List[Dict],
                     reading_speed: int = DEFAULT_READING_SPEED,
                     filters: List[List] = []) -> List[float]:
    # because some records in data don't have the 'time_to_read' field
    word_counts = get_word_counts(data, filters=filters)
    return [wc / reading_speed for wc in word_counts if wc > 0]


def get_added_time_series(data: List[Dict]) -> pd.DataFrame:
    added_date_counts = Counter(epoch_to_yyymmdd(record['time_added']) for record in data)
    df = pd.DataFrame.from_dict({datetime.strptime(d, '%Y%m%d'): cnt for d, cnt in added_date_counts.items()},
                                orient='index', columns=['All articles'])
    df.index = df.index.tz_localize('UTC')
    return df


def get_archived_time_series(data: List[Dict]) -> pd.DataFrame:
    archived_date_counts = Counter(
        epoch_to_yyymmdd(record['time_added']) for record in data
        if int(record['status']) == 1
    )
    df = pd.DataFrame.from_dict({datetime.strptime(d, '%Y%m%d'): cnt for d, cnt in archived_date_counts.items()},
                                orient='index', columns=['Archived articles'])
    df.index = df.index.tz_localize('UTC')
    return df


def get_average_readed_word(data: List[Dict], n_last_days: int) -> float:
    # find the ones that are archived, time_updated >= min_date
    min_date = datetime.now() - timedelta(days=n_last_days)
    records = [
        record for record in data
        if (int(record['status']) == 1) and (datetime.fromtimestamp(int(record['time_updated'])) >= min_date)
    ]
    word_counts = get_word_counts(records)
    return 0 if len(word_counts) == 0 else sum(word_counts) / len(word_counts)


def get_domain_counts(data: List[Dict], filters: List[List] = []) -> Dict[str, int]:
    return Counter(get_domain_from_url(record['resolved_url'])
                   for record in data
                   if should_pass_filters(filters, record))


def get_language_counts(data: List[Dict]) -> Dict[str, int]:
    return Counter(normalize_language_name(record['lang']) for record in data)


def get_favorite_count(data: List[Dict]) -> Dict[str, int]:
    total = len(data)
    cnt = sum(1 for record in data if int(record['favorite']) == 1)
    return {
        'count': cnt,
        'percent': 1.0 * cnt / total if total > 0 else 0,
    }


def get_unread_count(data: List[Dict]) -> int:
    df = pd.DataFrame.from_dict(data)
    return df.query("status == '0'").status.count()
