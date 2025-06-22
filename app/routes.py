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
    
from flask import Blueprint, render_template, redirect, request, session, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user

from .helpers import guardar_usuario, obtener_usuario_por_nombre_usuario

from .models import User
from .solver import resolver_problema_lp, extraer_coeficientes



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
    numeroVariables = int(data.get("numeroVariables"))
    restricciones = data.get("restricciones", [])

    resultado = resolver_problema_lp(tipoOperacion, funcionObjetivo, restricciones, numeroVariables)

    return jsonify({"resultado": resultado})




# @main.route("/resolver_simplex_pasos", methods=["POST"])
# def resolver_simplex_pasos():
#     data = request.get_json()

#     tipoOperacion = data.get("tipoOperacion")
#     funcionObjetivo = data.get("funcionObjetivo")
#     numeroVariables = int(data.get("numeroVariables"))
#     restricciones = data.get("restricciones", [])

#     if tipoOperacion.lower() != "maximizar":
#         return jsonify({"status": "error", "mensaje": "Solo maximizar permitido en este método."})

#     c = extraer_coeficientes(funcionObjetivo, numeroVariables)

#     coef_restricciones = []
#     for r in restricciones:
#         if r["op"] != "≤":
#             return jsonify({"status": "error", "mensaje": "Solo restricciones ≤ permitidas en este método."})
#         fila = extraer_coeficientes(r["expr"], numeroVariables)
#         coef_restricciones.append({
#             "coeficientes": fila,
#             "constante": float(r["val"])
#         })

#     resultado = simplex_clasico_paso_a_paso(c, coef_restricciones, numeroVariables)
#     return jsonify(resultado)

from .simplex_utils import procesar_restriccion, simplex_paso_a_paso

# Endpoint modificado
@main.route("/resolver_simplex_pasos", methods=["POST"])
def resolver_simplex_pasos():
    try:
        data = request.get_json()
        
        # Validar datos
        required_fields = ["tipoOperacion", "funcionObjetivo", "numeroVariables", "restricciones"]
        for field in required_fields:
            if field not in data:
                return jsonify({"status": "error", "mensaje": f"Campo faltante: {field}"}), 400
        
        tipo = data["tipoOperacion"].lower()
        funcion = data["funcionObjetivo"]
        n_vars = int(data["numeroVariables"])
        restricciones = data["restricciones"]
        
        if tipo not in ["maximizar", "minimizar"]:
            return jsonify({
                "status": "error",
                "mensaje": "Tipo de operación inválido. Use 'Maximizar' o 'Minimizar'"
            }), 400
        
        # Procesar función objetivo
        coefs_obj, const_obj = extraer_coeficientes(funcion, n_vars)
        
        # Para minimización, invertir signos
        if tipo == "minimizar":
            coefs_obj = [-c for c in coefs_obj]
        
        # Procesar restricciones
        A_ub, b_ub = [], []
        A_eq, b_eq = [], []
        
        for r in restricciones:
            expr = r.get("expr", "")
            op = r.get("op", "")
            val = r.get("val", "")
            
            if not expr or not op or not val:
                return jsonify({
                    "status": "error",
                    "mensaje": "Restricción incompleta"
                }), 400
            
            if op not in ["≤", "≥", "="]:
                return jsonify({
                    "status": "error",
                    "mensaje": f"Operador no válido: {op}. Use '≤', '≥' o '='"
                }), 400
            
            try:
                coefs, rhs, tipo_res = procesar_restriccion(expr, op, val, n_vars)
                
                if tipo_res == "ub":
                    A_ub.append(coefs)
                    b_ub.append(rhs)
                elif tipo_res == "eq":
                    A_eq.append(coefs)
                    b_eq.append(rhs)
                    
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "mensaje": f"Error procesando restricción: {str(e)}"
                }), 400
        
        # Ejecutar simplex paso a paso
        pasos = simplex_paso_a_paso(
            c=coefs_obj,
            A_ub=A_ub,
            b_ub=b_ub,
            A_eq=A_eq,
            b_eq=b_eq,
            n_vars=n_vars
        )
        
        return jsonify({
            "status": "ok",
            "pasos": pasos
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "mensaje": f"Error interno: {str(e)}"
        }), 500
    

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
    



# @main.route("/resolver-simplex-general", methods=["POST"])
# def simplex_general():
#     data = request.get_json()

#     try:
#         resultado = resolver_simplex_general(data)
#         return jsonify({"resultado": resultado})
#     except Exception as e:
#         print(f"Error al resolver con Simplex General: {e}")
#         return jsonify({"error": "No se pudo resolver el problema con Simplex General."}), 400

# from .simplex_m import resolver_simplex_gran_m
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)


# @main.route("/resolver-simplex-general", methods=["POST"])
# def simplex_general():
#     """
#     Endpoint para resolver problemas de programación lineal usando Simplex con Gran M.
#     Maneja cualquier tipo de problema (maximización/minimización) con cualquier tipo de restricción.
#     """
#     try:
#         data = request.get_json()
        
#         # Validar datos de entrada
#         if not data:
#             return jsonify({
#                 "error": "No se recibieron datos",
#                 "status": "error"
#             }), 400
        
#         # Validar campos requeridos
#         campos_requeridos = ["tipoOperacion", "funcionObjetivo", "numeroVariables", "restricciones"]
#         for campo in campos_requeridos:
#             if campo not in data:
#                 return jsonify({
#                     "error": f"Campo requerido faltante: {campo}",
#                     "status": "error"
#                 }), 400
        
#         # Validar que haya al menos una restricción
#         if not data["restricciones"] or len(data["restricciones"]) == 0:
#             return jsonify({
#                 "error": "Debe haber al menos una restricción",
#                 "status": "error"
#             }), 400
        
#         # Validar número de variables
#         num_vars = data["numeroVariables"]
#         if not isinstance(num_vars, int) or num_vars < 1 or num_vars > 20:
#             return jsonify({
#                 "error": "El número de variables debe ser un entero entre 1 y 20",
#                 "status": "error"
#             }), 400
        
#         # Validar tipo de operación
#         tipo_op = data["tipoOperacion"].lower()
#         if tipo_op not in ["max", "maximizar", "min", "minimizar"]:
#             return jsonify({
#                 "error": "Tipo de operación debe ser 'max', 'maximizar', 'min' o 'minimizar'",
#                 "status": "error"
#             }), 400
        
#         # Validar restricciones
#         for i, restriccion in enumerate(data["restricciones"]):
#             if not isinstance(restriccion, dict):
#                 return jsonify({
#                     "error": f"La restricción {i+1} debe ser un objeto",
#                     "status": "error"
#                 }), 400
            
#             if "expr" not in restriccion or "op" not in restriccion or "val" not in restriccion:
#                 return jsonify({
#                     "error": f"La restricción {i+1} debe tener campos 'expr', 'op' y 'val'",
#                     "status": "error"
#                 }), 400
            
#             # Validar operador
#             if restriccion["op"] not in ["≤", "≥", "="]:
#                 return jsonify({
#                     "error": f"Operador inválido en restricción {i+1}: {restriccion['op']}",
#                     "status": "error"
#                 }), 400
            
#             # Validar que val sea convertible a float
#             try:
#                 float(restriccion["val"])
#             except (ValueError, TypeError):
#                 return jsonify({
#                     "error": f"El valor de la restricción {i+1} debe ser un número",
#                     "status": "error"
#                 }), 400
        
#         # Validar función objetivo
#         if not data["funcionObjetivo"] or not isinstance(data["funcionObjetivo"], str):
#             return jsonify({
#                 "error": "La función objetivo debe ser una cadena no vacía",
#                 "status": "error"
#             }), 400
        
#         logging.info(f"Resolviendo problema con Simplex Gran M: {data}")
        
#         # Resolver el problema
#         resultado = resolver_simplex_gran_m(data)
        
#         # Formatear respuesta
#         respuesta = {
#             "status": "success",
#             "resultado": resultado,
#             "mensaje": "Problema resuelto exitosamente con Simplex Gran M"
#         }
        
#         # Si el problema es infactible
#         if resultado.get("status") == "infactible":
#             respuesta["status"] = "warning"
#             respuesta["mensaje"] = resultado.get("mensaje", "Problema infactible")
        
#         logging.info(f"Problema resuelto exitosamente. Valor óptimo: {resultado.get('optimo')}")
        
#         return jsonify(respuesta)
        
#     except ValueError as e:
#         logging.error(f"Error de validación: {str(e)}")
#         return jsonify({
#             "error": f"Error en los datos de entrada: {str(e)}",
#             "status": "error"
#         }), 400
        
#     except Exception as e:
#         logging.error(f"Error al resolver con Simplex Gran M: {str(e)}")
        
#         # Determinar el tipo de error
#         error_msg = str(e)
#         if "no acotada" in error_msg.lower():
#             return jsonify({
#                 "error": "El problema tiene solución no acotada",
#                 "status": "error",
#                 "tipo": "no_acotada"
#             }), 400
#         elif "infactible" in error_msg.lower():
#             return jsonify({
#                 "error": "El problema no tiene solución factible",
#                 "status": "error", 
#                 "tipo": "infactible"
#             }), 400
#         else:
#             return jsonify({
#                 "error": "Error interno al resolver el problema",
#                 "status": "error",
#                 "detalles": error_msg
#             }), 500


from .gran_m import resolver_simplex_gran_m

@main.route("/resolver-simplex-general", methods=["POST"])
def simplex_general():
    """
    Endpoint para resolver problemas de programación lineal usando Simplex con Gran M.
    Versión adaptada que usa el algoritmo robusto con MixedValue.
    """
    try:
        data = request.get_json()
        
        # Validar datos de entrada
        if not data:
            return jsonify({
                "error": "No se recibieron datos",
                "status": "error"
            }), 400
        
        # Validar campos requeridos
        campos_requeridos = ["tipoOperacion", "funcionObjetivo", "numeroVariables", "restricciones"]
        for campo in campos_requeridos:
            if campo not in data:
                return jsonify({
                    "error": f"Campo requerido faltante: {campo}",
                    "status": "error"
                }), 400
        
        # Validar que haya al menos una restricción
        if not data["restricciones"] or len(data["restricciones"]) == 0:
            return jsonify({
                "error": "Debe haber al menos una restricción",
                "status": "error"
            }), 400
        
        # Validar número de variables
        num_vars = data["numeroVariables"]
        if not isinstance(num_vars, int) or num_vars < 1 or num_vars > 20:
            return jsonify({
                "error": "El número de variables debe ser un entero entre 1 y 20",
                "status": "error"
            }), 400
        
        # Validar tipo de operación
        tipo_op = data["tipoOperacion"].lower()
        if tipo_op not in ["max", "maximizar", "min", "minimizar"]:
            return jsonify({
                "error": "Tipo de operación debe ser 'max', 'maximizar', 'min' o 'minimizar'",
                "status": "error"
            }), 400
        
        # Validar restricciones
        for i, restriccion in enumerate(data["restricciones"]):
            if not isinstance(restriccion, dict):
                return jsonify({
                    "error": f"La restricción {i+1} debe ser un objeto",
                    "status": "error"
                }), 400
            
            if "expr" not in restriccion or "op" not in restriccion or "val" not in restriccion:
                return jsonify({
                    "error": f"La restricción {i+1} debe tener campos 'expr', 'op' y 'val'",
                    "status": "error"
                }), 400
            
            # Validar operadores
            if restriccion["op"] not in ["≤", "≥", "="]:
                return jsonify({
                    "error": f"Operador inválido en restricción {i+1}: {restriccion['op']}",
                    "status": "error"
                }), 400
            
            # Validar que val sea convertible a float
            try:
                float(restriccion["val"])
            except (ValueError, TypeError):
                return jsonify({
                    "error": f"El valor de la restricción {i+1} debe ser un número",
                    "status": "error"
                }), 400
        
        # Validar función objetivo
        if not data["funcionObjetivo"] or not isinstance(data["funcionObjetivo"], str):
            return jsonify({
                "error": "La función objetivo debe ser una cadena no vacía",
                "status": "error"
            }), 400
        
        logging.info(f"Resolviendo problema con Simplex Gran M: {data}")
        
        # Resolver el problema con el nuevo algoritmo robusto
        resultado = resolver_simplex_gran_m(data)
        
        # Formatear respuesta
        respuesta = {
            "status": "success",
            "resultado": resultado,
            "mensaje": "Problema resuelto exitosamente con Simplex Gran M"
        }
        
        # Manejar estados especiales
        if resultado.get("status") == "infactible":
            respuesta["status"] = "warning"
            respuesta["mensaje"] = resultado.get("mensaje", "Problema infactible")
        elif resultado.get("status") == "no_acotada":
            respuesta["status"] = "error"
            respuesta["mensaje"] = resultado.get("mensaje", "Problema no acotado")
        
        logging.info(f"Resultado del problema: {resultado.get('status')}")
        
        return jsonify(respuesta)
        
    except ValueError as e:
        logging.error(f"Error de validación: {str(e)}")
        return jsonify({
            "error": f"Error en los datos de entrada: {str(e)}",
            "status": "error"
        }), 400
        
    except Exception as e:
        logging.error(f"Error al resolver con Simplex Gran M: {str(e)}", exc_info=True)
        return jsonify({
            "error": "Error interno al resolver el problema",
            "status": "error",
            "detalles": str(e)
        }), 500
   


from .test import GranMSimplexExtended
@main.route("/resolver_gran_m", methods=["POST"])
def resolver_gran_m():
    # 1. Recibir el payload
    data = request.get_json()

    # 2. Extraer y convertir la función objetivo a coeficientes numéricos
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

    # 3. Extraer restricciones
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
        # 4. Parsear datos
        n = int(data["numeroVariables"])
        funcion_objetivo = parse_funcion_objetivo(data["funcionObjetivo"], n)
        restricciones, tipos = parse_restricciones(data["restricciones"], n)
        minimizar = data["tipoOperacion"].lower().startswith("min")
        print("valor de minimizar", minimizar)
        
        # 5. Resolver
        solver = GranMSimplexExtended()
        html = solver.solve(funcion_objetivo, restricciones, tipos, minimize=minimizar)
        
        # 6. Devolver HTML en JSON
        return jsonify({"html": html})
    except Exception as e:
        return jsonify({"error": str(e)}), 400