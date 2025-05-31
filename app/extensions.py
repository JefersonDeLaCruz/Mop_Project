from flask_babel import Babel
from flask import request


# funcion para obtener el lenguaje que mejor conicide con la config del user commo la del browser por ejemplo

def get_local_lang():
    lang = request.accept_languages.best_match(["en", "es"])
    print("Lenguaje seleccionado", lang)
    return lang


babel = Babel()

