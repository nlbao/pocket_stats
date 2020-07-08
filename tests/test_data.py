from pocket_stats.data import is_valid_word, should_pass_filter


def test_is_valid_word():
    assert is_valid_word("") is False
    assert is_valid_word("is") is False  # stopword in English
    assert is_valid_word("USA") is True


def test_should_pass_filter():
    record = {
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
    assert should_pass_filter(["has_image", "=", 1], record)
    assert should_pass_filter(["favorite", "=", 1], record) is False
