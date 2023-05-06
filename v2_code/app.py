# Flash Card Application
# Tushar Supe : 21f1003637

# --------------------  Imports  --------------------

import os, json, time, requests, jwt #bcrypt
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, request, jsonify, make_response
from flask_restful import Api
from application.config import *
from application.database import db
from application.models import Users


# --------------------  Initialization  --------------------


app = None
api = None

root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# celery is implemented separately

def create_app():
    app = Flask(__name__, template_folder="templates")
    app.config.from_object(LocalDevelopmentConfig)
    db.init_app(app)
    api = Api(app)
    app.app_context().push()
    return app, api


app, api = create_app()

# Import all controllers
from application.controllers import *
from application.api import DeckAPI, CardAPI, SignupAPI, LoginAPI

# --------------------  Add Resource  --------------------
api.add_resource(LoginAPI, '/login')
api.add_resource(SignupAPI, '/signup')

api.add_resource(DeckAPI, '/api/deck', '/api/deck/<int:deckid>', '/api/deck/<string:deckname>')
api.add_resource(CardAPI, "/api/deck/<int:deckid>/card", "/api/deck/<int:deckid>/card/<int:cardid>")

# --------------------  Main  --------------------
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)  # local

# --------------------  End  --------------------