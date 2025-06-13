from flask import Blueprint, render_template, redirect, request, session, url_for

main = Blueprint("main", __name__)

@main.route("/")
def index():

    username = session.get('username')
    data = {
        1: "avla que xopa",
        2: "yeah xopa",
        3: username
    }
    return render_template("index.html", data=data)

@main.route("/login", methods=["GET", "POST"])
def login():

    if request.method == 'POST':
        username = request.form['username']
        session['username'] = username
        return redirect(url_for("main.index"))

    return render_template("login.html")



#ruta para el cambio de idioma
@main.route("/idioma/<lang_code>")
def idioma(lang_code):
    if lang_code not in ["en", "es"]:
        lang_code = "es"
    session["lang"] = lang_code

    return redirect(url_for("main.index"))
    
