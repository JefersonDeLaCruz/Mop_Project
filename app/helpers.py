import json
import os

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
