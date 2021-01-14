# download nltk data
python3 -c "import nltk ; nltk.download('stopwords')"

# start the webserver
gunicorn --workers 4 'pocket_stats.app:server' -b :$PORT
