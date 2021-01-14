# gunicorn --workers 4 'pocket_stats.app:server' -b :8080
import os
import flask
from flask_wtf.csrf import CSRFProtect
from visualization import create_app


server = flask.Flask(__name__)  # define flask app.server
csrf = CSRFProtect(server)
server.config['SECRET_KEY'] = os.urandom(32)  # for csrf
csrf._exempt_views.add('dash.dash.dispatch')
app = create_app(server=server)  # call flask server

if __name__ == '__main__':
    app.run_server(debug=True)
