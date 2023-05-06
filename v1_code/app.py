# Final Project - Flash Card Application
# Tushar Supe : 21f1003637
# This is Main application file

# --------------------  Imports  --------------------


from flask import Flask
from application.config import *
from application.database import db
from flask_restful import Api
from flask_login import LoginManager

# --------------------  Initialization  --------------------


app = None
api = None


def create_app():
    app = Flask(__name__, template_folder="templates")
    app.config.from_object(LocalDevelopmentConfig)
    db.init_app(app)
    api = Api(app)

    login_manager = LoginManager()
    login_manager.login_view = '/login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(userid):
        return Users.query.get(int(userid))

    app.app_context().push()
    return app, api


app, api = create_app()

# Import all controllers
from application.controllers import *
from application.api import DeckAPI, CardAPI

# --------------------  Add Resource  --------------------
api.add_resource(DeckAPI, '/api/deck', '/api/deck/<int:deckid>', '/api/deck/<string:deckname>')
api.add_resource(CardAPI, "/api/deck/<int:deckid>/card", "/api/deck/<int:deckid>/card/<int:cardid>")

# --------------------  Main  --------------------
if __name__ == '__main__':
	# app.run(host='127.0.0.1', port=5000, debug=True) #local
    app.run(host='0.0.0.0', port=8080, debug=True) #replit

# --------------------  End  --------------------