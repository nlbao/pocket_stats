from click.testing import CliRunner
from unittest.mock import patch
import subprocess

from pocket_stats.__main__ import fetch_data, webapp


runner = CliRunner()


def test_fetch_data():
    runner.invoke(fetch_data, ['offset', '7', 'limit', '100'])


@patch('pocket_stats.__main__._fetch_data')
def test_fetch_data_mocked(mocked_fetch_data):
    mocked_fetch_data.return_value = [1, 2]
    runner.invoke(fetch_data, [])


@patch('dash.Dash.run_server')
def test_webapp(mocked_dash_run_sever):
    runner.invoke(webapp, [])


def test_main():
    subprocess.check_output('python3 pocket_stats', shell=True)
