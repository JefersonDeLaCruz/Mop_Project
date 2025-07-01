import json
import os
from werkzeug.security import generate_password_hash

def guardar_usuario(user, RUTA_ARCHIVO):

    os.makedirs(os.path.dirname(RUTA_ARCHIVO), exist_ok=True)
    # Intentamos cargar usuarios existentes
    if os.path.exists(RUTA_ARCHIVO):
        with open(RUTA_ARCHIVO, "r", encoding="utf-8") as archivo:
            try:
                users = json.load(archivo)
            except Exception as e:
                print("Error al parsear el JSON: ", e)
                users = []
    else:
        users = []

    # Asignamos un ID automático al nuevo usuario
    user["id"] = users[-1]["id"] + 1 if users else 1
    
    # Si la contraseña no está hasheada, la hasheamos
    if "password" in user and not user.get("password_hash"):
        user["password_hash"] = generate_password_hash(user["password"])
        # Eliminamos la contraseña en texto plano por seguridad
        if "password" in user:  # Verificamos nuevamente antes de eliminar
            del user["password"]

    # Agregamos el nuevo usuario
    users.append(user)

    # Guardamos la lista completa de usuarios nuevamente
    with open(RUTA_ARCHIVO, "w", encoding="utf-8") as archivo:
        json.dump(users, archivo, ensure_ascii=False, indent=4)

def cargar_usuarios(RUTA_ARCHIVO):
    if os.path.exists(RUTA_ARCHIVO):
        with open(RUTA_ARCHIVO, "r", encoding="utf-8") as archivo:
            try:
                return json.load(archivo)
            except Exception as e:
                print("Error al parsear el JSON: ", e)
                return []
    return []

def obtener_usuario_por_nombre_usuario(username, RUTA_ARCHIVO):
    usuarios = cargar_usuarios(RUTA_ARCHIVO)
    for user in usuarios:
        if user["username"] == username:
            return user
    return None

def migrar_contraseñas_a_hash(RUTA_ARCHIVO):
    """Migra contraseñas en texto plano a hash para usuarios existentes"""
    usuarios = cargar_usuarios(RUTA_ARCHIVO)
    usuarios_modificados = False
    
    for user in usuarios:
        # Si tiene contraseña en texto plano y no tiene hash
        if "password" in user and "password_hash" not in user:
            user["password_hash"] = generate_password_hash(user["password"])
            if "password" in user:  # Verificar antes de eliminar
                del user["password"]  # Eliminar contraseña en texto plano
            usuarios_modificados = True
            print(f"Migrado usuario: {user.get('username', 'Usuario sin nombre')}")
    
    # Guardar cambios si se hicieron modificaciones
    if usuarios_modificados:
        with open(RUTA_ARCHIVO, "w", encoding="utf-8") as archivo:
            json.dump(usuarios, archivo, ensure_ascii=False, indent=4)
        print("Migración de contraseñas completada.")
    else:
        print("No se encontraron contraseñas que migrar.")
