from flask import Blueprint, render_template, redirect, request, session, url_for

from .helpers import guardar_usuario

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
        print("dentro del metodo post")
        email = request.form['email'] #estos 'parametros' hacen referencia al atributo name de los inputs del form
        session['email'] = email
        print("email recibido: ", email)
        return redirect(url_for("main.index"))

    return render_template("login.html")

# @main.route("/login")
# def login():

@main.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"];
        email = request.form["email"];
        password = request.form["password"];

        new_user = {

            "username": username,
            "email":email,
            "password":password
        }

        guardar_usuario(new_user, "./data/usuarios.json")

    return render_template("register.html")



#ruta para el cambio de idioma
@main.route("/idioma/<lang_code>")
def idioma(lang_code):
    if lang_code not in ["en", "es"]:
        lang_code = "es"
    session["lang"] = lang_code

    return redirect(url_for("main.index"))
    
