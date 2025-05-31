# from flask import Flask

# app = Flask(__name__)



# @app.route('/')
# def index():
#     return "hello avla"


# if app.name == "__main__":
#     app.run(debug=True, port=7000)



from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=7000)




