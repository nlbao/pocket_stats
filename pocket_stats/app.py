# gunicorn --workers 4 'pocket_stats.app:server' -b :8080
import flask
from visualization import create_app


server = flask.Flask(__name__)  # define flask app.server
app = create_app(server=server)  # call flask server


if __name__ == '__main__':
    app.run_server(debug=True)
