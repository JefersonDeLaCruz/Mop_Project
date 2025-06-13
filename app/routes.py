from flask import Blueprint, render_template, redirect, request, session, url_for

main = Blueprint("main", __name__)

@main.route("/")
def index():
<<<<<<< Updated upstream

    username = session.get('username')
=======
>>>>>>> Stashed changes
    data = {
        1: "avla que xopa",
        2: "yeah xopa",
        3: username
    }
    return render_template("index.html", data=data)

<<<<<<< Updated upstream
@main.route("/login", methods=["GET", "POST"])
def login():

    if request.method == 'POST':
        username = request.form['username']
        session['username'] = username
        return redirect(url_for("main.index"))

=======
@main.route("/login")
def login():

>>>>>>> Stashed changes
    return render_template("login.html")


@main.route("/idioma/<lang_code>")
def idioma(lang_code):
    if lang_code not in ["en", "es"]:
        lang_code = "es"
    session["lang"] = lang_code

    return redirect(url_for("main.index"))
    
