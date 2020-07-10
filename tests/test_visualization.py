import os
import pytest
import dash_html_components as html
import plotly.graph_objs as go
from pocket_stats.data import load_cache
from pocket_stats.visualization import create_app, get_reading_time_chart, get_reading_time_needed


CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))


@pytest.fixture
def data():
    return load_cache(cache_file=os.path.join(CURRENT_DIR, 'test_cache_data.json'))


def test_get_reading_time_chart():
    output = get_reading_time_chart(data=[], reading_speed=200)
    assert isinstance(output, go.Figure)


def test_get_reading_time_needed():
    output = get_reading_time_needed(data=[{'word_count': 567890, 'status': 0}],
                                     reading_speed=60, reading_minutes_daily=77)
    assert isinstance(output, html.Div)


def test_create_app(data):
    create_app(data)  # won't load cache
