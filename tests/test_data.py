import os
import pytest
from typing import List, Dict
from collections import Counter
import pandas as pd
from unittest.mock import patch
from freezegun import freeze_time

from pocket_stats.data import fetch_data, load_cache, is_valid_word, normalize_language_name, get_domain_from_url
from pocket_stats.data import should_pass_filters, count_words_in_title, get_word_counts, get_favorite_count
from pocket_stats.data import get_reading_time, get_added_time_series, get_archived_time_series
from pocket_stats.data import get_average_readed_word, get_domain_counts, get_language_counts, download_ntlk
from pocket_stats.data import get_unread_count


CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))


@pytest.fixture
def record():
    return {
        "item_id": "615710633",
        "resolved_id": "615710633",
        "given_url": "http://www.brendangregg.com/blog/2014-05-11/strace-wow-much-syscall.html",
        "given_title": "strace Wow Much Syscall",
        "favorite": "0",
        "status": "0",
        "time_added": "1593853557",
        "time_updated": "1593853557",
        "time_read": "0",
        "time_favorited": "0",
        "sort_id": 0,
        "resolved_title": "strace Wow Much Syscall",
        "resolved_url": "http://www.brendangregg.com/blog/2014-05-11/strace-wow-much-syscall.html",
        "excerpt": "I wouldn't dare run strace(1) in production without seriously considering the consequences",
        "is_article": "1",
        "is_index": "0",
        "has_video": "0",
        "has_image": "1",
        "word_count": "2207",
        "lang": "en",
        "time_to_read": 10,
        "listen_duration_estimate": 854
    }


@pytest.fixture
def data():
    return load_cache(cache_file=os.path.join(CURRENT_DIR, 'test_cache_data.json'))


def test_load_cache(data: List[Dict]):
    with pytest.raises(FileNotFoundError):
        load_cache('/this/path/is/invalid.cache')
    # no need to test with valid cached, because the fixture data already run load_cache(cache_file)


@patch('json.dump')
@patch('pocket_stats.data.open')
@patch('pocket.Pocket.retrieve')
def test_fetch_data_ok(mocked_pocket_retrieve, mocked_open, mocked_json_dump):
    mocked_pocket_retrieve.return_value = {'list': {1: 2, 2: 3}}
    fetch_data(offset=10, limit=100, consumer_key='invalid', access_token='none')


def test_fetch_data_failed():
    with pytest.raises(Exception):
        fetch_data(consumer_key='invalid', access_token='none')


def raise_lookup_err_side_effect(*args, **kwargs):
    raise LookupError


@patch('nltk.download')
@patch('nltk.data.find')
def test_download_ntlk(mocked_nltk_data_find, mocked_ntlk_download):
    mocked_nltk_data_find.side_effect = raise_lookup_err_side_effect
    download_ntlk()


def test_is_valid_word():
    assert is_valid_word("") is False
    assert is_valid_word("is") is False  # stopword in English
    assert is_valid_word("USA") is True


def test_normalize_language_name():
    assert normalize_language_name('  ') == 'unknown'
    assert normalize_language_name('en ') == 'en'
    assert normalize_language_name('  VN') == 'VN'


def test_get_domain_from_url():
    assert get_domain_from_url('https://www.google.com/search/?q=hello') == 'google.com'
    assert get_domain_from_url('http://medium.com/abcdyxyz-?%34345/') == 'medium.com'
    assert get_domain_from_url('m.facebook.com/profile') == 'facebook.com'


def test_should_pass_filters(record: Dict):
    assert should_pass_filters([['favorite', '=', 0]], record) is True
    assert should_pass_filters([['favorite', '=', '0']], record) is True
    assert should_pass_filters([['status', '!=', 1]], record) is True
    assert should_pass_filters([['word_count', '=', 2207], ['status', '=', 1]], record) is False
    with pytest.raises(NotImplementedError):
        for invalid_op in ['and', 'or', 'not', 'is not', '>', '<', '==']:
            should_pass_filters([["favorite", invalid_op, 0]], record)


def test_count_words_in_title(data: List[Dict]):
    assert count_words_in_title(data) == Counter({
        'strace': 1, 'wow': 1, 'much': 1, 'syscall': 1, 'martin': 1, 'heinz': 1, '-': 1, 'personal': 1, 'website': 1,
        '&': 1, 'blog': 1, 'call': 1, 'programmer,': 1, 'career': 1, 'advice': 1, '|': 1, 'kalzumeus': 1, 'softw': 1
    })


def test_get_word_counts(data: List[Dict]):
    assert get_word_counts(data) == [2207, 0, 5449, 4721, 3245, 805, 1849]


def test_get_reading_time(data: List[Dict]):
    assert get_reading_time(data) == [9.80888888888889, 24.217777777777776,
                                      20.982222222222223, 14.422222222222222, 3.577777777777778, 8.217777777777778]


def test_get_added_time_series(data: List[Dict]):
    assert get_added_time_series(data).to_dict() == {'All articles': {
        pd.Timestamp('2020-07-03 00:00:00+0000', tz='UTC'): 5,
        pd.Timestamp('2020-07-04 00:00:00+0000', tz='UTC'): 2,
    }}


def test_get_archived_time_series(data: List[Dict]):
    assert get_archived_time_series(data).to_dict() == {'Archived articles': {
        pd.Timestamp('2020-07-03 00:00:00+0000', tz='UTC'): 1,
        pd.Timestamp('2020-07-04 00:00:00+0000', tz='UTC'): 1,
    }}


@freeze_time("2020-07-01")
def test_get_average_readed_word(data: List[Dict]):
    assert get_average_readed_word(data, 30) == 2724.5


def test_get_domain_counts(data: List[Dict]):
    assert get_domain_counts(data) == Counter({'kalzumeus.com': 3, 'brendangregg.com': 1, 'martinheinz.dev': 1,
                                               'awealthofcommonsense.com': 1, 'jlcollinsnh.com': 1})


def test_get_language_counts(data: List[Dict]):
    assert get_language_counts(data) == Counter({'en': 6, 'unknown': 1})


def test_get_favorite_count(data: List[Dict]):
    assert get_favorite_count(data) == {'count': 2, 'percent': 0.2857142857142857}


def test_get_unread_count(data: List[Dict]):
    assert get_unread_count(data) == 5
