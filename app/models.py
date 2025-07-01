from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin):
    def __init__(self, id, username, name, password_hash=None):
        self.id = id
        self.username = username
        self.name = name
        self.password_hash = password_hash
    
    def set_password(self, password):
        """Genera y almacena el hash de la contraseña"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica si la contraseña proporcionada coincide con el hash almacenado"""
        return check_password_hash(self.password_hash, password)
    
    @staticmethod
    def hash_password(password):
        """Método estático para generar hash de contraseña"""
        return generate_password_hash(password)
