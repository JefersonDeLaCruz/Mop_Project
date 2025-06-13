from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, username, name, password):
        self.id = id
        self.username = username
        self.name = name
        self.password = password
