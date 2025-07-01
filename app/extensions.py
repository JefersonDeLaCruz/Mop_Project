from flask_babel import Babel
from flask import request, session
from flask_login import LoginManager

babel = Babel()
login_manager = LoginManager()

def get_local_lang():
    """
    Función para obtener el idioma preferido del usuario.
    Prioridad: 1) Idioma guardado en sesión, 2) Idioma del navegador, 3) Español por defecto
    """
    # Primero revisar si ya existe en la sesión
    lang = session.get("lang")
    if lang and lang in ["en", "es"]:
        return lang
    
    # Si no hay idioma en sesión, usar el idioma preferido del navegador
    lang = request.accept_languages.best_match(["en", "es"])
    if lang:
        print(f"Idioma detectado del navegador: {lang}")
        return lang
    
    # Por defecto español si no se puede determinar
    print("Usando idioma por defecto: es")
    return "es"



