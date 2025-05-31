from flask import Blueprint, render_template

main = Blueprint("main", __name__)

@main.route("/")
def hello_world():
    data = {
        1: "avla que xopa",
        2: "yeah xopa"
    }
    return render_template("index.html", data=data)
