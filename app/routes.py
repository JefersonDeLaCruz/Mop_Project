
    
from flask import Blueprint, render_template, redirect, request, session, url_for, flash, jsonify
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

# @main.route("/login", methods=["GET", "POST"])
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