from flask_babel import Babel
from flask import request, session
from flask_login import LoginManager

babel = Babel()
login_manager = LoginManager()

def get_local_lang():

    #recuperar el lang de la session
    
    lang = session.get("lang")  # primero revisa si ya existe en session
    if not lang:
        lang = request.accept_languages.best_match(["en", "es"])
        print("Lenguaje seleccionado", lang)
    return lang
    # funcion para obtener el lenguaje que mejor conicide con la config del user commo la del browser por ejemplo
    # lang = request.accept_languages.best_match(["en", "es"])
    # print("Lenguaje seleccionado", lang)
    # return lang



