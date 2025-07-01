from flask import Blueprint, render_template, redirect, request, session, url_for, flash, jsonify, get_flashed_messages
from flask_login import login_user, logout_user, login_required, current_user

from .helpers import guardar_usuario, obtener_usuario_por_nombre_usuario

from .models import User
from .solver import resolver_problema_lp



main = Blueprint("main", __name__)

@main.route("/")
@login_required
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

        # Guardar el nuevo usuario
        guardar_usuario(new_user, "./data/usuarios.json")
        
        # Obtener el usuario recién creado con su ID asignado
        created_user = obtener_usuario_por_nombre_usuario(username, "./data/usuarios.json")
        
        # Crear objeto User e iniciar sesión automáticamente
        user_obj = User(created_user["id"], created_user["username"], created_user["name"], created_user["password"])
        login_user(user_obj)
        
        flash("¡Cuenta creada exitosamente! Bienvenido/a a OptimizeFlow.", "success")
        # En lugar de redirigir al login, renderizar register.html con flag para ir al index
        return render_template("register.html", register_success=True)
    else:
        # Limpiar mensajes flash antiguos cuando se accede a register por GET
        get_flashed_messages()

    return render_template("register.html")



@main.route("/perfil")
@login_required
def perfil():
    try:
        import json
        import os
        from datetime import datetime
        
        def get_historial_filename(user_id):
            return f"./data/{user_id}_historial.json"
        
        def cargar_historial(user_id):
            filename = get_historial_filename(user_id)
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {"user_id": user_id, "problemas": []}
        
        # Cargar historial del usuario
        historial_usuario = cargar_historial(current_user.id)
        
        # Obtener parámetros de paginación
        page = request.args.get('page', 1, type=int)
        per_page = 6  # Problemas por página
        
        # Validar que la página sea válida
        if page < 1:
            page = 1
        
        # Ordenar por fecha (más recientes primero) y aplicar paginación
        problemas_recientes = []
        total_problemas = len(historial_usuario["problemas"])
        total_pages = (total_problemas + per_page - 1) // per_page if total_problemas > 0 else 0
        
        # Validar que la página no exceda el total de páginas
        if page > total_pages and total_pages > 0:
            page = total_pages
        
        if historial_usuario["problemas"]:
            problemas_ordenados = sorted(historial_usuario["problemas"], key=lambda x: x["fecha"], reverse=True)
            
            # Calcular índices para la paginación
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            
            # Obtener problemas para la página actual
            problemas_recientes = problemas_ordenados[start_idx:end_idx]
        
        # Pasar la información del usuario actual y su historial al template
        user_info = {
            'id': current_user.id,
            'username': current_user.username,
            'name': current_user.name
        }
        
        # Información de paginación
        pagination_info = {
            'current_page': page,
            'total_pages': total_pages,
            'per_page': per_page,
            'total_items': total_problemas,
            'has_prev': page > 1,
            'has_next': page < total_pages,
            'prev_page': page - 1 if page > 1 else None,
            'next_page': page + 1 if page < total_pages else None
        }
        
        return render_template("perfil.html", 
                             user=user_info, 
                             problemas_recientes=problemas_recientes,
                             total_problemas=total_problemas,
                             pagination=pagination_info)
                             
    except Exception as e:
        print(f"Error al cargar perfil: {e}")
        # En caso de error, mostrar perfil sin historial
        user_info = {
            'id': current_user.id,
            'username': current_user.username,
            'name': current_user.name
        }
        return render_template("perfil.html", 
                             user=user_info, 
                             problemas_recientes=[],
                             total_problemas=0,
                             pagination={'current_page': 1, 'total_pages': 0, 'has_prev': False, 'has_next': False})


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
def cambiar_idioma(lang_code):
    """Endpoint para cambiar el idioma de la aplicación"""
    # Validar que el idioma sea soportado
    if lang_code not in ["en", "es"]:
        lang_code = "es"  # Por defecto español
    
    # Guardar el idioma en la sesión
    session["lang"] = lang_code
    
    # Redireccionar de vuelta a la página anterior o al inicio
    next_page = request.args.get('next')
    if next_page:
        return redirect(next_page)
    return redirect(request.referrer or url_for("main.index"))


@main.route("/resolver", methods=["POST"])
@login_required
def resolver():
    data = request.get_json()
    
    # Normalizar payload para garantizar compatibilidad con diferentes idiomas
    from .extensions import normalize_payload_backend
    normalized_data = normalize_payload_backend(data)

    tipoOperacion = normalized_data.get("tipoOperacion")
    funcionObjetivo = normalized_data.get("funcionObjetivo")
    restricciones = normalized_data.get("restricciones", [])
    
    # El número de variables ahora es opcional
    numeroVariables = normalized_data.get("numeroVariables")
    if numeroVariables is not None:
        numeroVariables = int(numeroVariables)

    resultado = resolver_problema_lp(tipoOperacion, funcionObjetivo, restricciones, numeroVariables)

    return jsonify({"resultado": resultado})





from .simplex_solver import resolver_simplex_clasico
@main.route("/resolver-simplex", methods=["POST"])
@login_required
def resolver_simplex():
    data = request.get_json()
    
    # Normalizar payload para garantizar compatibilidad con diferentes idiomas
    from .extensions import normalize_payload_backend
    normalized_data = normalize_payload_backend(data)
    
    try:
        resultado = resolver_simplex_clasico(normalized_data)
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
@login_required
def resolver_gran_m():
    # 1. Recibir el payload
    data = request.get_json()
    
    # Normalizar payload para garantizar compatibilidad con diferentes idiomas
    from .extensions import normalize_payload_backend
    normalized_data = normalize_payload_backend(data)

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
        if "numeroVariables" in normalized_data and normalized_data["numeroVariables"]:
            n = int(normalized_data["numeroVariables"])
        else:
            # Crear lista de todas las expresiones para analizarlas
            expresiones = [normalized_data["funcionObjetivo"]] + [r["expr"] for r in normalized_data["restricciones"]]
            n = extraer_numero_variables(expresiones)
            
            if n == 0:
                return jsonify({"error": "No se pudieron detectar variables en la función objetivo o restricciones"}), 400

        # 6. Parsear datos
        funcion_objetivo = parse_funcion_objetivo(normalized_data["funcionObjetivo"], n)
        restricciones, tipos = parse_restricciones(normalized_data["restricciones"], n)
        minimizar = normalized_data["tipoOperacion"].lower().startswith("min")
        print("valor de minimizar", minimizar)
        print(f"Número de variables detectadas automáticamente: {n}")
        
        # 7. Resolver
        solver = GranMSimplexExtended()
        html = solver.solve(funcion_objetivo, restricciones, tipos, minimize=minimizar)
        
        # 8. Devolver HTML en JSON
        return jsonify({"html": html})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@main.route("/guardar_historial", methods=["POST"])
@login_required
def guardar_historial():
    """Endpoint para guardar un problema resuelto en el historial del usuario"""
    try:
        data = request.get_json()
        
        # Importar aquí para evitar dependencias circulares
        import json
        import os
        from datetime import datetime
        from .solver import extraer_numero_variables
        
        def get_historial_filename(user_id):
            return f"./data/{user_id}_historial.json"
        
        def cargar_historial(user_id):
            filename = get_historial_filename(user_id)
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {"user_id": user_id, "problemas": []}
        
        # Extraer datos del payload para el resumen
        payload = data.get("payload", {})
        metodo = data.get("metodo", "Desconocido")
        html_detallado = data.get("html_detallado", "")
        
        # Calcular número de variables automáticamente
        expresiones = [payload.get("funcionObjetivo", "")] + [r.get("expr", "") for r in payload.get("restricciones", [])]
        num_variables = extraer_numero_variables(expresiones)
        
        # Generar resumen del problema
        resumen = {
            "tipo": payload.get("tipoOperacion", "No especificado"),
            "funcion_objetivo": payload.get("funcionObjetivo", ""),
            "num_restricciones": len(payload.get("restricciones", [])),
            "num_variables": num_variables,
            "metodo": metodo
        }
        
        # Cargar historial existente
        historial = cargar_historial(current_user.id)
        
        # Crear nueva entrada
        problema_id = len(historial["problemas"]) + 1
        nuevo_problema = {
            "id": problema_id,
            "fecha": datetime.now().isoformat(),
            "resumen": resumen,
            "payload_original": payload,
            "html_detallado": html_detallado,
            "metodo_usado": metodo
        }
        
        # Agregar al historial (mantener solo los últimos 50)
        historial["problemas"].append(nuevo_problema)
        if len(historial["problemas"]) > 50:
            historial["problemas"] = historial["problemas"][-50:]
        
        # Crear directorio si no existe
        filename = get_historial_filename(current_user.id)
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Guardar archivo
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(historial, f, ensure_ascii=False, indent=2)
        
        return jsonify({
            "status": "success",
            "mensaje": "Problema guardado en historial",
            "problema_id": problema_id
        })
        
    except Exception as e:
        print(f"Error al guardar historial: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "mensaje": f"Error al guardar en historial: {str(e)}"
        }), 500

@main.route("/historial")
@login_required
def historial():
    """Muestra el historial de problemas del usuario"""
    try:
        import json
        import os
        
        def get_historial_filename(user_id):
            return f"./data/{user_id}_historial.json"
        
        def cargar_historial(user_id):
            filename = get_historial_filename(user_id)
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {"user_id": user_id, "problemas": []}
        
        historial_usuario = cargar_historial(current_user.id)
        
        # Ordenar por fecha (más recientes primero)
        if historial_usuario["problemas"]:
            historial_usuario["problemas"].sort(key=lambda x: x["fecha"], reverse=True)
        
        return render_template("historial.html", historial=historial_usuario)
        
    except Exception as e:
        flash(f"Error al cargar el historial: {str(e)}", "error")
        return redirect(url_for("main.perfil"))

@main.route("/problema/<int:problema_id>")
@login_required
def ver_problema_detalle(problema_id):
    """Muestra el detalle completo de un problema específico"""
    try:
        import json
        import os
        
        def get_historial_filename(user_id):
            return f"./data/{user_id}_historial.json"
        
        def cargar_historial(user_id):
            filename = get_historial_filename(user_id)
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {"user_id": user_id, "problemas": []}
        
        historial = cargar_historial(current_user.id)
        
        # Buscar el problema específico
        problema = None
        for p in historial["problemas"]:
            if p["id"] == problema_id:
                problema = p
                break
        
        if not problema:
            flash("Problema no encontrado.", "error")
            return redirect(url_for("main.historial"))
        
        return render_template("problema_detalle.html", problema=problema)
        
    except Exception as e:
        flash(f"Error al cargar el problema: {str(e)}", "error")
        return redirect(url_for("main.historial"))

@main.route("/api/problema/<int:problema_id>/datos", methods=["GET"])
@login_required
def obtener_datos_problema(problema_id):
    """API endpoint para obtener los datos de un problema para editar"""
    try:
        import json
        import os
        
        def get_historial_filename(user_id):
            return f"./data/{user_id}_historial.json"
        
        def cargar_historial(user_id):
            filename = get_historial_filename(user_id)
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {"user_id": user_id, "problemas": []}
        
        historial = cargar_historial(current_user.id)
        
        # Buscar el problema específico
        problema = None
        for p in historial["problemas"]:
            if p["id"] == problema_id:
                problema = p
                break
        
        if not problema:
            return jsonify({"error": "Problema no encontrado"}), 404
        
        # Extraer solo los datos necesarios para poblar el formulario
        payload = problema.get("payload_original", {})
        
        return jsonify({
            "tipoOperacion": payload.get("tipoOperacion", "Maximizar"),
            "funcionObjetivo": payload.get("funcionObjetivo", ""),
            "restricciones": payload.get("restricciones", []),
            "metodo": problema.get("metodo_usado", "SciPy")
        })
        
    except Exception as e:
        return jsonify({"error": f"Error al cargar datos: {str(e)}"}), 500


@main.route("/ejemplos")
@login_required
def ejemplos():
    """Vista para mostrar ejemplos de problemas de programación lineal"""
    ejemplos_data = [
        {
            "id": 1,
            "titulo": "Problema de Producción Industrial",
            "descripcion": "Una fábrica de muebles produce dos tipos de productos: mesas (Producto A) y sillas (Producto B). La empresa cuenta con recursos limitados de madera y tiempo de producción. Cada mesa genera una ganancia de $3 y cada silla $2. La empresa necesita determinar cuántas unidades de cada producto fabricar para maximizar sus ganancias, considerando que tiene disponibles 18 unidades de madera y 12 horas de tiempo de producción diarias.",
            "tipo": "Maximización",
            "variables": ["x1 (Mesas producidas)", "x2 (Sillas producidas)"],
            "funcion_objetivo": "3x1 + 2x2",
            "restricciones": [
                "2x1 + x2 ≤ 18 (Limitación de madera: cada mesa usa 2 unidades, cada silla 1)",
                "x1 + 3x2 ≤ 12 (Limitación de tiempo: cada mesa toma 1 hora, cada silla 3 horas)"
            ],
            "solucion_optima": "x1 = 8.40, x2 = 1.20, Z = 27.60",
            "categoria": "Producción"
        },
        {
            "id": 2,
            "titulo": "Problema de Planificación Nutricional",
            "descripcion": "Un nutricionista necesita diseñar una dieta económica que cumpla con los requerimientos mínimos de nutrientes para un hospital. Dispone de dos tipos de alimentos: Alimento 1 (cuesta $4 por unidad) y Alimento 2 (cuesta $3 por unidad). La dieta debe garantizar al menos 10 unidades de proteína, 8 unidades de vitaminas y 12 unidades de minerales. El objetivo es minimizar el costo total de la dieta mientras se satisfacen todos los requerimientos nutricionales.",
            "tipo": "Minimización", 
            "variables": ["x1 (Unidades de Alimento 1)", "x2 (Unidades de Alimento 2)"],
            "funcion_objetivo": "4x1 + 3x2",
            "restricciones": [
                "2x1 + x2 ≥ 10 (Requerimiento mínimo de proteína)",
                "x1 + x2 ≥ 8 (Requerimiento mínimo de vitaminas)",
                "x1 + 3x2 ≥ 12 (Requerimiento mínimo de minerales)"
            ],
            "solucion_optima": "x1 = 2, x2 = 6, Z = 26",
            "categoria": "Dieta"
        },
        {
            "id": 3,
            "titulo": "Problema de Optimización Logística",
            "descripcion": "Una empresa distribuidora debe transportar productos desde dos almacenes hacia dos tiendas para minimizar los costos de transporte. Cuenta con tres rutas posibles: Ruta 1 (costo $8 por unidad), Ruta 2 (costo $6 por unidad) y Ruta 3 (costo $10 por unidad). El almacén 1 puede enviar máximo 15 unidades por las rutas 1 y 2, el almacén 2 puede enviar máximo 25 unidades por la ruta 3. La tienda 1 necesita al menos 5 unidades y la tienda 2 necesita al menos 15 unidades. ¿Cómo distribuir el transporte para minimizar costos?",
            "tipo": "Minimización",
            "variables": ["x1 (Unidades por Ruta 1)", "x2 (Unidades por Ruta 2)", "x3 (Unidades por Ruta 3)"],
            "funcion_objetivo": "8x1 + 6x2 + 10x3",
            "restricciones": [
                "x1 + x2 ≤ 15 (Capacidad máxima del almacén 1)",
                "x3 ≤ 25 (Capacidad máxima del almacén 2)",
                "x1 + x3 ≥ 5 (Demanda mínima de la tienda 1)",
                "x2 + x3 ≥ 15 (Demanda mínima de la tienda 2)"
            ],
            "solucion_optima": "x1 = 0, x2 = 10, x3 = 5, Z = 110",
            "categoria": "Transporte"
        }
    ]
    
    return render_template("ejemplos.html", ejemplos=ejemplos_data)


@main.route("/ayuda")
def ayuda():
    """Vista para mostrar ayuda y documentación del sistema"""
    ayuda_sections = [
        {
            "id": "introduccion",
            "titulo": "Introducción a la Programación Lineal",
            "contenido": """
            <p>La <strong>programación lineal (PL)</strong> es una técnica de optimización matemática que permite resolver problemas donde se busca maximizar o minimizar una función objetivo lineal, sujeta a un conjunto de restricciones lineales.</p>
            
            <h4>¿Cuándo usar Programación Lineal?</h4>
            <ul>
                <li><strong>Optimización de recursos limitados:</strong> Cuando necesitas distribuir recursos escasos de manera óptima</li>
                <li><strong>Planificación de producción:</strong> Para determinar qué y cuánto producir</li>
                <li><strong>Problemas de transporte:</strong> Minimizar costos de envío entre ubicaciones</li>
                <li><strong>Asignación de presupuestos:</strong> Distribuir fondos para maximizar beneficios</li>
                <li><strong>Planificación de dietas:</strong> Minimizar costos cumpliendo requerimientos nutricionales</li>
            </ul>
            
            <h4>Ventajas de la Programación Lineal</h4>
            <ul>
                <li>Proporciona soluciones <strong>óptimas</strong> (no solo buenas)</li>
                <li>Permite <strong>análisis de sensibilidad</strong> para entender cambios</li>
                <li>Es <strong>eficiente computacionalmente</strong> para problemas grandes</li>
                <li>Tiene <strong>amplia aplicabilidad</strong> en diversas industrias</li>
            </ul>
            """,
            "icono": "fas fa-info-circle"
        },
        {
            "id": "teoria",
            "titulo": "Fundamentos Teóricos",
            "contenido": """
            <h4>Forma Estándar de un Problema de PL</h4>
            <p>Todo problema de programación lineal se puede expresar en la siguiente forma:</p>
            
            <div class="bg-base-200 p-4 rounded-lg my-4">
                <strong>Maximizar (o Minimizar):</strong> Z = c₁x₁ + c₂x₂ + ... + cₙxₙ<br><br>
                <strong>Sujeto a:</strong><br>
                a₁₁x₁ + a₁₂x₂ + ... + a₁ₙxₙ ≤ b₁<br>
                a₂₁x₁ + a₂₂x₂ + ... + a₂ₙxₙ ≤ b₂<br>
                ...<br>
                aₘ₁x₁ + aₘ₂x₂ + ... + aₘₙxₙ ≤ bₘ<br><br>
                <strong>Con:</strong> x₁, x₂, ..., xₙ ≥ 0
            </div>
            
            <h4>Conceptos Clave</h4>
            <ul>
                <li><strong>Región Factible:</strong> El conjunto de todas las soluciones que satisfacen las restricciones</li>
                <li><strong>Solución Óptima:</strong> El punto en la región factible que optimiza la función objetivo</li>
                <li><strong>Vértices:</strong> Los puntos donde se intersectan las restricciones (candidatos a solución óptima)</li>
                <li><strong>Degeneración:</strong> Cuando una solución básica tiene más restricciones activas que variables</li>
                <li><strong>Soluciones Múltiples:</strong> Cuando existe más de una solución óptima</li>
            </ul>
            
            <h4>Tipos de Soluciones</h4>
            <ul>
                <li><strong>Óptima Única:</strong> Existe una sola solución que optimiza la función objetivo</li>
                <li><strong>Óptimas Múltiples:</strong> Infinitas soluciones con el mismo valor óptimo</li>
                <li><strong>No Acotada:</strong> La función objetivo puede mejorar indefinidamente</li>
                <li><strong>No Factible:</strong> No existe solución que satisfaga todas las restricciones</li>
            </ul>
            """,
            "icono": "fas fa-graduation-cap"
        },
        {
            "id": "componentes",
            "titulo": "Componentes de un Problema LP",
            "contenido": """
            <h4>1. Variables de Decisión</h4>
            <p>Son las <strong>incógnitas</strong> del problema que queremos determinar. Representan las cantidades a decidir.</p>
            <ul>
                <li><strong>Ejemplo:</strong> x₁ = cantidad de producto A a fabricar, x₂ = cantidad de producto B</li>
                <li><strong>Nomenclatura:</strong> Usar nombres descriptivos (x1, x2, x3... o P_A, P_B...)</li>
                <li><strong>Unidades:</strong> Especificar claramente las unidades (toneladas, horas, pesos, etc.)</li>
            </ul>
            
            <h4>2. Función Objetivo</h4>
            <p>Es la <strong>expresión matemática</strong> que queremos optimizar (maximizar o minimizar).</p>
            <ul>
                <li><strong>Maximización:</strong> Ganancias, beneficios, producción, eficiencia</li>
                <li><strong>Minimización:</strong> Costos, tiempo, desperdicios, distancias</li>
                <li><strong>Linealidad:</strong> Debe ser una combinación lineal de las variables</li>
            </ul>
            
            <h4>3. Restricciones</h4>
            <p>Son las <strong>limitaciones o condiciones</strong> que deben cumplir las variables de decisión.</p>
            <ul>
                <li><strong>Restricciones de Recursos:</strong> Limitaciones físicas (materiales, tiempo, capacidad)</li>
                <li><strong>Restricciones de Demanda:</strong> Requerimientos mínimos o máximos</li>
                <li><strong>Restricciones de Política:</strong> Reglas del negocio o regulaciones</li>
                <li><strong>Restricciones de Balance:</strong> Ecuaciones de equilibrio</li>
            </ul>
            
            <h4>4. Condiciones de No Negatividad</h4>
            <p>Generalmente las variables deben ser <strong>≥ 0</strong>, aunque pueden existir excepciones.</p>
            """,
            "icono": "fas fa-puzzle-piece"
        },
        {
            "id": "tutorial-sistema",
            "titulo": "Tutorial Completo del Sistema",
            "contenido": """
            <h4>Paso 1: Preparación del Problema</h4>
            <ol>
                <li><strong>Identifica el objetivo:</strong> ¿Qué quieres maximizar o minimizar?</li>
                <li><strong>Define las variables:</strong> ¿Qué decisiones necesitas tomar?</li>
                <li><strong>Lista las restricciones:</strong> ¿Qué limitaciones tienes?</li>
                <li><strong>Verifica la linealidad:</strong> ¿Todas las relaciones son lineales?</li>
            </ol>
            
            <h4>Paso 2: Uso de la Calculadora</h4>
            <ol>
                <li><strong>Selecciona el tipo:</strong> Maximizar o Minimizar</li>
                <li><strong>Ingresa la función objetivo:</strong> Usa sintaxis como "3x1 + 2x2"</li>
                <li><strong>Agrega restricciones:</strong> Una por línea, especifica el operador (≤, ≥, =)</li>
                <li><strong>Elige el método:</strong> SciPy (recomendado), Simplex, o Gran M</li>
                <li><strong>Haz clic en "Resolver"</strong></li>
            </ol>
            
            <h4>Paso 3: Interpretación de Resultados</h4>
            <ul>
                <li><strong>Valores de Variables:</strong> Las cantidades óptimas de cada variable</li>
                <li><strong>Valor Objetivo:</strong> El mejor valor posible de tu función objetivo</li>
                <li><strong>Variables de Holgura:</strong> Recursos no utilizados en las restricciones</li>
                <li><strong>Análisis de Sensibilidad:</strong> Cómo afectan los cambios a la solución</li>
            </ul>
            
            <h4>Funciones Avanzadas</h4>
            <ul>
                <li><strong>Historial:</strong> Accede a problemas previamente resueltos</li>
                <li><strong>Editar Problema:</strong> Modifica problemas del historial</li>
                <li><strong>Exportar Resultados:</strong> Guarda tus soluciones</li>
                <li><strong>Ejemplos:</strong> Aprende con casos predefinidos</li>
            </ul>
            """,
            "icono": "fas fa-play-circle"
        },
        {
            "id": "sintaxis",
            "titulo": "Guía de Sintaxis Completa",
            "contenido": """
            <h4>Variables de Decisión</h4>
            <ul>
                <li><strong>Formato:</strong> x1, x2, x3, ... xn (siempre con número)</li>
                <li><strong>Válido:</strong> x1, x2, x15, x100</li>
                <li><strong>No válido:</strong> x, y, z, variable1, X1</li>
            </ul>
            
            <h4>Operadores Matemáticos</h4>
            <ul>
                <li><strong>Suma:</strong> + (ej: x1 + x2)</li>
                <li><strong>Resta:</strong> - (ej: x1 - x2)</li>
                <li><strong>Multiplicación:</strong> NO uses asterisco (*)</li>
                <li><strong>Coeficientes:</strong> Número seguido directamente de variable (ej: 2x1, 3.5x2)</li>
            </ul>
            
            <h4>Operadores de Comparación</h4>
            <ul>
                <li><strong>Menor o igual:</strong> ≤ o <= (para restricciones de límite superior)</li>
                <li><strong>Mayor o igual:</strong> ≥ o >= (para restricciones de límite inferior)</li>
                <li><strong>Igual:</strong> = (para restricciones de balance exacto)</li>
            </ul>
            
            <h4>Ejemplos de Expresiones Válidas</h4>
            <div class="space-y-3">
                <div>
                    <span class="badge badge-primary">Función Objetivo</span>
                    <div class="bg-base-200 p-3 rounded mt-1">
                        <code>3x1 + 2x2 + 5x3 - 1.5x4</code>
                    </div>
                </div>
                <div>
                    <span class="badge badge-secondary">Restricción Simple</span>
                    <div class="bg-base-200 p-3 rounded mt-1">
                        <code>2x1 + 4x2 ≤ 100</code>
                    </div>
                </div>
                <div>
                    <span class="badge badge-accent">Restricción Compleja</span>
                    <div class="bg-base-200 p-3 rounded mt-1">
                        <code>0.5x1 + 2.3x2 - x3 + 4x4 ≥ 25.7</code>
                    </div>
                </div>
            </div>
            
            <h4>Errores Comunes de Sintaxis</h4>
            <ul>
                <li><strong>❌ Incorrecto:</strong> 3*x1 (NO uses asterisco)</li>
                <li><strong>✅ Correcto:</strong> 3x1</li>
                <li><strong>❌ Incorrecto:</strong> 2 * x1 (espacios y asterisco)</li>
                <li><strong>✅ Correcto:</strong> 2x1</li>
                <li><strong>❌ Incorrecto:</strong> x + y (variables sin número)</li>
                <li><strong>✅ Correcto:</strong> x1 + x2</li>
                <li><strong>❌ Incorrecto:</strong> x1^2 (no lineal)</li>
                <li><strong>✅ Correcto:</strong> 2x1 (lineal)</li>
            </ul>
            """,
            "icono": "fas fa-code"
        },
        {
            "id": "metodos",
            "titulo": "Métodos de Solución Disponibles",
            "contenido": """
            <h4>1. SciPy (Recomendado)</h4>
            <ul>
                <li><strong>Algoritmo:</strong> Interior Point y Revised Simplex</li>
                <li><strong>Ventajas:</strong> Rápido, estable, maneja problemas grandes</li>
                <li><strong>Ideal para:</strong> Problemas de producción, casos generales</li>
                <li><strong>Limitaciones:</strong> No muestra pasos intermedios</li>
            </ul>
            
            <h4>2. Simplex Clásico</h4>
            <ul>
                <li><strong>Algoritmo:</strong> Método Simplex tradicional</li>
                <li><strong>Ventajas:</strong> Muestra tableau paso a paso, educativo</li>
                <li><strong>Ideal para:</strong> Aprendizaje, problemas pequeños a medianos</li>
                <li><strong>Limitaciones:</strong> Más lento para problemas grandes</li>
            </ul>
            
            <h4>3. Método de la Gran M</h4>
            <ul>
                <li><strong>Algoritmo:</strong> Simplex con variables artificiales</li>
                <li><strong>Ventajas:</strong> Maneja restricciones ≥ y = directamente</li>
                <li><strong>Ideal para:</strong> Problemas con restricciones de igualdad o ≥</li>
                <li><strong>Limitaciones:</strong> Más complejo, requiere parámetro M grande</li>
            </ul>
            
            <h4>¿Cuál Método Elegir?</h4>
            <div class="overflow-x-auto">
                <table class="table table-zebra w-full">
                    <thead>
                        <tr>
                            <th>Situación</th>
                            <th>Método Recomendado</th>
                            <th>Razón</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Problema de producción</td>
                            <td>SciPy</td>
                            <td>Rápido y eficiente</td>
                        </tr>
                        <tr>
                            <td>Aprendiendo PL</td>
                            <td>Simplex Clásico</td>
                            <td>Muestra pasos</td>
                        </tr>
                        <tr>
                            <td>Restricciones de igualdad</td>
                            <td>Gran M</td>
                            <td>Maneja = directamente</td>
                        </tr>
                        <tr>
                            <td>Problema grande (>10 variables)</td>
                            <td>SciPy</td>
                            <td>Mejor rendimiento</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            """,
            "icono": "fas fa-calculator"
        },
        {
            "id": "ejemplos-completos",
            "titulo": "Ejemplos Paso a Paso",
            "contenido": """
            <h4>Ejemplo 1: Problema de Producción</h4>
            <div class="bg-info/10 p-4 rounded-lg">
                <p><strong>Situación:</strong> Una empresa fabrica sillas y mesas. Cada silla da $40 de ganancia y cada mesa $30. La producción está limitada por materiales y tiempo.</p>
                
                <p><strong>Paso 1 - Definir Variables:</strong></p>
                <ul>
                    <li>x1 = número de sillas a producir</li>
                    <li>x2 = número de mesas a producir</li>
                </ul>
                
                <p><strong>Paso 2 - Función Objetivo:</strong></p>
                <code>Maximizar: 40x1 + 30x2</code>
                
                <p><strong>Paso 3 - Restricciones:</strong></p>
                <ul>
                    <li>Material: 2x1 + 3x2 ≤ 100</li>
                    <li>Tiempo: 4x1 + 2x2 ≤ 120</li>
                    <li>No negatividad: x1, x2 ≥ 0</li>
                </ul>
            </div>
            
            <h4>Ejemplo 2: Problema de Dieta</h4>
            <div class="bg-warning/10 p-4 rounded-lg">
                <p><strong>Situación:</strong> Minimizar el costo de una dieta que cumpla requerimientos nutricionales mínimos.</p>
                
                <p><strong>Variables:</strong></p>
                <ul>
                    <li>x1 = porciones de alimento A</li>
                    <li>x2 = porciones de alimento B</li>
                </ul>
                
                <p><strong>Función Objetivo:</strong></p>
                <code>Minimizar: 2x1 + 3x2</code>
                
                <p><strong>Restricciones:</strong></p>
                <ul>
                    <li>Proteína: 4x1 + 2x2 ≥ 20</li>
                    <li>Vitaminas: x1 + 3x2 ≥ 15</li>
                </ul>
            </div>
            
            <h4>Consejos para Formular Problemas</h4>
            <ol>
                <li><strong>Lee el problema completo</strong> antes de empezar</li>
                <li><strong>Identifica qué se debe decidir</strong> (variables)</li>
                <li><strong>Encuentra el objetivo principal</strong> (maximizar/minimizar qué)</li>
                <li><strong>Lista todas las limitaciones</strong> (restricciones)</li>
                <li><strong>Traduce a matemáticas</strong> usando la sintaxis correcta</li>
                <li><strong>Verifica la coherencia</strong> de unidades y signos</li>
            </ol>
            """,
            "icono": "fas fa-lightbulb"
        },
        {
            "id": "interpretacion",
            "titulo": "Interpretación de Resultados",
            "contenido": """
            <h4>Entendiendo la Solución Óptima</h4>
            <ul>
                <li><strong>Valores de Variables:</strong> Las cantidades exactas que optimizan tu objetivo</li>
                <li><strong>Valor de la Función Objetivo:</strong> El mejor resultado posible</li>
                <li><strong>Estado de Restricciones:</strong> Cuáles están activas (en el límite) y cuáles no</li>
            </ul>
            
            <h4>Variables de Holgura y Exceso</h4>
            <ul>
                <li><strong>Holgura (≤):</strong> Cantidad no utilizada del recurso</li>
                <li><strong>Exceso (≥):</strong> Cantidad que supera el mínimo requerido</li>
                <li><strong>Interpretación:</strong> Holgura = 0 indica recurso completamente utilizado</li>
            </ul>
            
            <h4>Análisis de Sensibilidad</h4>
            <ul>
                <li><strong>Precios Duales:</strong> Valor de obtener una unidad adicional del recurso</li>
                <li><strong>Rangos de Validez:</strong> Hasta dónde son válidos los precios duales</li>
                <li><strong>Análisis de Coeficientes:</strong> Cómo afectan cambios en la función objetivo</li>
            </ul>
            
            <h4>Casos Especiales</h4>
            <div class="space-y-3">
                <div class="alert alert-info">
                    <strong>Solución No Factible:</strong> Las restricciones son contradictorias. Revisa y ajusta las restricciones.
                </div>
                <div class="alert alert-warning">
                    <strong>Solución No Acotada:</strong> La función objetivo puede mejorar indefinidamente. Verifica si faltan restricciones.
                </div>
                <div class="alert alert-success">
                    <strong>Soluciones Múltiples:</strong> Existen varias soluciones óptimas. Puedes elegir cualquiera o una combinación.
                </div>
            </div>
            
            <h4>Validación de Resultados</h4>
            <ol>
                <li><strong>Verifica que las variables sean ≥ 0</strong> (si aplica)</li>
                <li><strong>Sustituye en todas las restricciones</strong> para confirmar factibilidad</li>
                <li><strong>Calcula el valor objetivo manualmente</strong> para verificar</li>
                <li><strong>Revisa si los resultados tienen sentido práctico</strong></li>
            </ol>
            """,
            "icono": "fas fa-chart-line"
        },
        {
            "id": "consejos",
            "titulo": "Mejores Prácticas y Consejos",
            "contenido": """
            <h4>Antes de Resolver</h4>
            <ul>
                <li><strong>Documenta tu problema:</strong> Escribe claramente qué representa cada variable</li>
                <li><strong>Verifica unidades:</strong> Asegúrate de que todas las unidades sean consistentes</li>
                <li><strong>Revisa la linealidad:</strong> Confirma que no hay términos cuadráticos o productos de variables</li>
                <li><strong>Valida restricciones:</strong> Asegúrate de que sean realistas y no contradictorias</li>
            </ul>
            
            <h4>Durante la Formulación</h4>
            <ul>
                <li><strong>Usa nombres descriptivos:</strong> x1_sillas es mejor que x1</li>
                <li><strong>Escribe restricciones claras:</strong> Incluye descripción de cada una</li>
                <li><strong>Revisa signos:</strong> ≤ para límites superiores, ≥ para mínimos</li>
                <li><strong>No olvides no negatividad:</strong> El sistema las agrega automáticamente</li>
            </ul>
            
            <h4>Después de Resolver</h4>
            <ul>
                <li><strong>Interpreta en contexto:</strong> ¿Qué significa la solución en tu problema real?</li>
                <li><strong>Valida la factibilidad:</strong> ¿Se cumplen todas las restricciones?</li>
                <li><strong>Analiza la sensibilidad:</strong> ¿Qué tan estable es tu solución?</li>
                <li><strong>Considera implementación:</strong> ¿Es práctica la solución encontrada?</li>
            </ul>
            
            <h4>Errores Comunes a Evitar</h4>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="card bg-error/10 border border-error/20">
                    <div class="card-body p-4">
                        <h5 class="font-semibold text-error mb-2">❌ Errores de Formulación</h5>
                        <ul class="text-sm space-y-1">
                            <li>• Confundir maximización con minimización</li>
                            <li>• Usar variables sin número (x en lugar de x1)</li>
                            <li>• Olvidar el asterisco en multiplicaciones</li>
                            <li>• Restricciones contradictorias</li>
                        </ul>
                    </div>
                </div>
                <div class="card bg-success/10 border border-success/20">
                    <div class="card-body p-4">
                        <h5 class="font-semibold text-success mb-2">✅ Buenas Prácticas</h5>
                        <ul class="text-sm space-y-1">
                            <li>• Definir claramente cada variable</li>
                            <li>• Usar sintaxis correcta: 3x1 + 2x2</li>
                            <li>• Verificar unidades de medida</li>
                            <li>• Probar con casos simples primero</li>
                        </ul>
                    </div>
                </div>
            </div>
            
            <h4>Recursos para Seguir Aprendiendo</h4>
            <ul>
                <li><strong>Practica con ejemplos:</strong> Usa la sección de ejemplos del sistema</li>
                <li><strong>Experimenta con métodos:</strong> Compara resultados entre SciPy y Simplex</li>
                <li><strong>Analiza tu historial:</strong> Revisa problemas anteriores para mejorar</li>
                <li><strong>Modifica parámetros:</strong> Observa cómo cambian las soluciones</li>
            </ul>
            """,
            "icono": "fas fa-star"
        }
    ]
    
    return render_template("ayuda.html", ayuda_sections=ayuda_sections)