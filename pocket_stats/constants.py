import sys
import logging
import os
import pytz
import string


DEFAULT_TZINFO = pytz.utc
CONSUMER_KEY = os.environ.get('POCKET_STATS_CONSUMER_KEY', None)
ACCESS_TOKEN = os.environ.get('POCKET_STATS_ACCESS_TOKEN', None)
GTAG_ID = os.environ.get('GTAG_ID', '')
DEFAULT_READING_SPEED = 225  # words per minute
MAX_LRU_CACHE_SIZE = 128
MAX_NUMBER_OF_RECORDS = 1000

# custom index string for Dash app
DASH_APP_INDEX_STRING = string.Template('''
<!DOCTYPE html>
<html>
    <head>
        <!-- Global site tag (gtag.js) - Google Analytics -->
        <script async src="https://www.googletagmanager.com/gtag/js?id=${gtag_id}"></script>
        <script>
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());

            gtag('config', ${gtag_id});
        </script>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        <div>
            <h1>Pocket Stats</h1>
        </div>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
        <div></div>
    </body>
</html>
''').substitute({
    'gtag_id': GTAG_ID,
})

# logging
root = logging.getLogger()
root.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(name)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)
