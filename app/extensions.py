from flask_babel import Babel
from flask import request, session

babel = Babel()

def get_local_lang():

    #recuperar el lang de la session
    

    # funcion para obtener el lenguaje que mejor conicide con la config del user commo la del browser por ejemplo
    lang = request.accept_languages.best_match(["en", "es"])
    print("Lenguaje seleccionado", lang)
    return lang



