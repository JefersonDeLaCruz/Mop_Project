from flask import Blueprint, render_template, redirect, request, session, url_for, flash, jsonify, get_flashed_messages
from flask_login import login_user, logout_user, login_required, current_user

from .helpers import guardar_usuario, obtener_usuario_por_nombre_usuario

from .models import User
from .solver import resolver_problema_lp



main = Blueprint("main", __name__)

@main.route("/")
def index():
    username = current_user.username if current_user.is_authenticated else None
    data = {
        1: "avla que xopa",
        2: "yeah xopa",
        3: username
    }
    resultado = {
        "status": "error" 
    }

    return render_template("index.html", data=data, resultado=resultado)

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
            # En lugar de redirigir inmediatamente, renderizar login.html con una flag
            return render_template("login.html", login_success=True)
        else:
            flash("Credenciales incorrectas. Inténtalo de nuevo.", "error")
            # return redirect(url_for("main.login"))
    else:
        # Limpiar mensajes flash antiguos cuando se accede a login por GET
        # Esto evita que se acumulen mensajes de sesiones anteriores
        get_flashed_messages()

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
        # En lugar de redirigir inmediatamente, renderizar register.html con una flag
        return render_template("register.html", register_success=True)
    else:
        # Limpiar mensajes flash antiguos cuando se accede a register por GET
        get_flashed_messages()

    return render_template("register.html")



@main.route("/perfil")
@login_required
def perfil():
    # Pasar la información del usuario actual al template
    user_info = {
        'id': current_user.id,
        'username': current_user.username,
        'name': current_user.name
    }
    return render_template("perfil.html", user=user_info)


@main.route("/actualizar_perfil", methods=["POST"])
@login_required
def actualizar_perfil():
    import json
    import os
    
    # Obtener datos del formulario
    new_name = request.form.get("name", "").strip()
    new_username = request.form.get("username", "").strip()
    current_password = request.form.get("current_password", "")
    new_password = request.form.get("new_password", "").strip()
    confirm_password = request.form.get("confirm_password", "").strip()
    
    # Validaciones básicas
    if not new_name or not new_username or not current_password:
        flash("Por favor, completa todos los campos obligatorios (nombre, usuario y contraseña actual).", "error")
        return redirect(url_for("main.perfil"))
    
    # Verificar contraseña actual
    user_data = obtener_usuario_por_nombre_usuario(current_user.username, "./data/usuarios.json")
    if not user_data or user_data["password"] != current_password:
        flash("La contraseña actual que ingresaste es incorrecta. Verifica e intenta de nuevo.", "error")
        return redirect(url_for("main.perfil"))
    
    # Verificar que el username no esté en uso por otro usuario
    if new_username != current_user.username:
        existing_user = obtener_usuario_por_nombre_usuario(new_username, "./data/usuarios.json")
        if existing_user:
            flash(f"El nombre de usuario '{new_username}' ya está en uso. Por favor, elige otro.", "warning")
            return redirect(url_for("main.perfil"))
    
    # Validar nueva contraseña si se proporciona
    if new_password:
        if len(new_password) < 4:
            flash("La nueva contraseña debe tener al menos 4 caracteres.", "error")
            return redirect(url_for("main.perfil"))
        if new_password != confirm_password:
            flash("Las contraseñas nuevas no coinciden. Verifica que hayas escrito la misma contraseña en ambos campos.", "error")
            return redirect(url_for("main.perfil"))
    
    # Actualizar en el archivo JSON
    try:
        # Cargar todos los usuarios
        if os.path.exists("./data/usuarios.json"):
            with open("./data/usuarios.json", "r", encoding="utf-8") as archivo:
                usuarios = json.load(archivo)
        else:
            flash("Error al acceder a los datos de usuarios.", "error")
            return redirect(url_for("main.perfil"))
        
        # Encontrar y actualizar el usuario actual
        for usuario in usuarios:
            if usuario["id"] == current_user.id:
                usuario["name"] = new_name
                usuario["username"] = new_username
                if new_password:  # Solo actualizar si se proporciona nueva contraseña
                    usuario["password"] = new_password
                break
        
        # Guardar cambios
        with open("./data/usuarios.json", "w", encoding="utf-8") as archivo:
            json.dump(usuarios, archivo, ensure_ascii=False, indent=4)
        
        # Actualizar el objeto current_user para la sesión actual
        current_user.name = new_name
        current_user.username = new_username
        
        # Mensaje de éxito más detallado
        success_msg = f"¡Perfil actualizado correctamente! "
        if new_password:
            success_msg += "Tu contraseña también ha sido cambiada."
        else:
            success_msg += "Tus datos personales han sido actualizados."
        
        flash(success_msg, "success")
        
    except Exception as e:
        flash("Ocurrió un error inesperado al actualizar tu perfil. Por favor, inténtalo de nuevo.", "error")
        print(f"Error al actualizar perfil: {e}")
    
    return redirect(url_for("main.perfil"))


@main.route("/idioma/<lang_code>")
def idioma(lang_code):
    if lang_code not in ["en", "es"]:
        lang_code = "es"
    session["lang"] = lang_code
    return redirect(url_for("main.index"))


@main.route("/resolver", methods=["POST"])
def resolver():
    data = request.get_json()

    tipoOperacion = data.get("tipoOperacion")
    funcionObjetivo = data.get("funcionObjetivo")
    restricciones = data.get("restricciones", [])
    
    # El número de variables ahora es opcional
    numeroVariables = data.get("numeroVariables")
    if numeroVariables is not None:
        numeroVariables = int(numeroVariables)

    resultado = resolver_problema_lp(tipoOperacion, funcionObjetivo, restricciones, numeroVariables)

    return jsonify({"resultado": resultado})





from .simplex_solver import resolver_simplex_clasico
@main.route("/resolver-simplex", methods=["POST"])
def resolver_simplex():
    data = request.get_json()
    
    try:
        resultado = resolver_simplex_clasico(data)
        return jsonify({"resultado": resultado})
    except Exception as e:
        print(f"Error al resolver con Simplex: {e}")
        return jsonify({"error": "No se pudo resolver el problema con Simplex."}), 400
    




import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)





import re
from .test import GranMSimplexExtended

@main.route("/resolver_gran_m", methods=["POST"])
def resolver_gran_m():
    # 1. Recibir el payload
    data = request.get_json()

    # 2. Función para extraer automáticamente el número de variables
    def extraer_numero_variables(expresiones):
        """
        Extrae automáticamente el número de variables de decisión analizando las expresiones.
        
        Parámetros:
            expresiones (list): Lista de expresiones (función objetivo + restricciones)
        
        Retorna:
            int: Número máximo de variables encontradas
        """
        max_var = 0
        
        for expr in expresiones:
            # Buscar todos los patrones de variables (x1, x2, x3, etc.)
            matches = re.findall(r'x(\d+)', expr)
            if matches:
                # Convertir a enteros y encontrar el máximo
                variables_en_expr = [int(m) for m in matches]
                max_var = max(max_var, max(variables_en_expr))
        
        return max_var

    # 3. Extraer y convertir la función objetivo a coeficientes numéricos
    def parse_funcion_objetivo(expr, n):
        # expr: "7x1 + 2x2", n: 2
        coefs = [0]*n
        expr = expr.replace("-", "+-")
        for term in expr.split("+"):
            term = term.strip()
            if not term:
                continue
            if "x" in term:
                num, var = term.split("x")
                idx = int(var) - 1
                coefs[idx] = float(num.strip()) if num.strip() not in ["", "+", "-"] else (1.0 if num.strip() in ["", "+"] else -1.0)
            else:
                pass  # No es necesario en Simplex estándar
        return coefs

    # 4. Extraer restricciones
    def parse_restricciones(restricciones, n):
        coefs = []
        tipos = []
        for restric in restricciones:
            expr = restric["expr"].replace("-", "+-")
            fila = [0]*n
            for term in expr.split("+"):
                term = term.strip()
                if not term:
                    continue
                if "x" in term:
                    num, var = term.split("x")
                    idx = int(var) - 1
                    fila[idx] = float(num.strip()) if num.strip() not in ["", "+", "-"] else (1.0 if num.strip() in ["", "+"] else -1.0)
                else:
                    pass
            # El lado derecho
            fila.append(float(restric["val"]))
            coefs.append(fila)
            tipos.append(restric["op"].replace("≥", ">=").replace("≤", "<="))
        return coefs, tipos

    try:
        # 5. Extraer número de variables automáticamente si no se proporciona
        if "numeroVariables" in data and data["numeroVariables"]:
            n = int(data["numeroVariables"])
        else:
            # Crear lista de todas las expresiones para analizarlas
            expresiones = [data["funcionObjetivo"]] + [r["expr"] for r in data["restricciones"]]
            n = extraer_numero_variables(expresiones)
            
            if n == 0:
                return jsonify({"error": "No se pudieron detectar variables en la función objetivo o restricciones"}), 400

        # 6. Parsear datos
        funcion_objetivo = parse_funcion_objetivo(data["funcionObjetivo"], n)
        restricciones, tipos = parse_restricciones(data["restricciones"], n)
        minimizar = data["tipoOperacion"].lower().startswith("min")
        print("valor de minimizar", minimizar)
        print(f"Número de variables detectadas automáticamente: {n}")
        
        # 7. Resolver
        solver = GranMSimplexExtended()
        html = solver.solve(funcion_objetivo, restricciones, tipos, minimize=minimizar)
        
        # 8. Devolver HTML en JSON
        return jsonify({"html": html})
    except Exception as e:
        return jsonify({"error": str(e)}), 400