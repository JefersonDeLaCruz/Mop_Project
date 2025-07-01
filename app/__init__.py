
from flask import Flask
from flask_babel import get_locale
from app.extensions import babel, get_local_lang, login_manager
from .helpers import cargar_usuarios
from .models import User
# app = Flask(__name__)

def create_app():

    app = Flask(__name__)
    app.secret_key = "777"

    babel.init_app(app, locale_selector=get_local_lang)
    login_manager.init_app(app)
    login_manager.login_view = "main.login" #para redirigir a login si no esta autenticado
    
    # Hacer get_locale disponible globalmente en todos los templates
    @app.context_processor
    def inject_conf_vars():
        return {
            'get_locale': get_locale
        }

    from .routes import main
    app.register_blueprint(main)

    return app


@login_manager.user_loader
def load_user(user_id):
    usuarios = cargar_usuarios("./data/usuarios.json")
    for user_data in usuarios:
        if str(user_data["id"]) == str(user_id):
            return User(user_data["id"], user_data["username"], user_data["name"], user_data["password"])
    return None

