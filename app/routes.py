# from flask import Blueprint, render_template, redirect, request, session, url_for

# from .helpers import guardar_usuario

# main = Blueprint("main", __name__)

# @main.route("/")
# def index():

#     username = session.get('username')
#     data = {
#         1: "avla que xopa",
#         2: "yeah xopa",
#         3: username
#     }
#     return render_template("index.html", data=data)

# @main.route("/login", methods=["GET", "POST"])
# def login():
#     if request.method == 'POST':
#         print("dentro del metodo post")
#         email = request.form['email'] #estos 'parametros' hacen referencia al atributo name de los inputs del form
#         session['email'] = email
#         print("email recibido: ", email)
#         return redirect(url_for("main.index"))

#     return render_template("login.html")

# # @main.route("/login")
# # def login():

# @main.route("/register", methods=["GET", "POST"])
# def register():
#     if request.method == "POST":
#         username = request.form["username"];
#         email = request.form["email"];
#         password = request.form["password"];

#         new_user = {

#             "username": username,
#             "email":email,
#             "password":password
#         }

#         guardar_usuario(new_user, "./data/usuarios.json")

#         return(redirect(url_for("main.index")))

#     return render_template("register.html")



# #ruta para el cambio de idioma
# @main.route("/idioma/<lang_code>")
# def idioma(lang_code):
#     if lang_code not in ["en", "es"]:
#         lang_code = "es"
#     session["lang"] = lang_code

#     return redirect(url_for("main.index"))
    
from flask import Blueprint, render_template, redirect, request, session, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

from .helpers import guardar_usuario, obtener_usuario_por_nombre_usuario

from .models import User

main = Blueprint("main", __name__)

@main.route("/")
def index():
    username = current_user.username if current_user.is_authenticated else None
    data = {
        1: "avla que xopa",
        2: "yeah xopa",
        3: username
    }
    return render_template("index.html", data=data)

@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        password = request.form["password"]

        user_data = obtener_usuario_por_nombre_usuario(user, "./data/usuarios.json")
        if user_data and user_data["password"] == password:
            user = User(user_data["id"], user_data["username"], user_data["name"], user_data["password"])
            login_user(user)
            flash("¡Inicio de sesión exitoso!", "success")
            return redirect(url_for("main.index"))
        else:
            flash("Credenciales incorrectas. Inténtalo de nuevo.", "error")
            # return redirect(url_for("main.login"))

    return render_template("login.html")

@main.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for("main.login"))

@main.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        name = request.form["name"]
        password = request.form["password"]

        if obtener_usuario_por_nombre_usuario(username, "./data/usuarios.json"):
            flash("El nombre de usuario ya está registrado.", "warning")
            return redirect(url_for("main.register"))

        new_user = {
            "username": username,
            "name": name,
            "password": password
        }

        guardar_usuario(new_user, "./data/usuarios.json")
        flash("Registro exitoso. Ahora inicia sesión.", "success")
        return redirect(url_for("main.login"))

    return render_template("register.html")



@main.route("/perfil")
def perfil():

    return render_template("perfil.html")


@main.route("/idioma/<lang_code>")
def idioma(lang_code):
    if lang_code not in ["en", "es"]:
        lang_code = "es"
    session["lang"] = lang_code
    return redirect(url_for("main.index"))
