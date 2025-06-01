
from flask import Flask
from app.extensions import babel, get_local_lang

# app = Flask(__name__)

def create_app():

    app = Flask(__name__)
    app.secret_key = "777"
    babel.init_app(app, locale_selector=get_local_lang)

    from .routes import main
    app.register_blueprint(main)

    return app




