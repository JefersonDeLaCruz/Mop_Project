import logging

# Configuración básica de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def resolver_simplex_gran_m(data):
    """
    Resuelve un problema de programación lineal usando el método simplex con Gran M.
    Maneja problemas de maximización y minimización con cualquier tipo de restricción.

    Parámetros:
        data (dict): Diccionario con la siguiente estructura:
            - tipoOperacion: "max", "maximizar", "min", "minimizar"
            - funcionObjetivo: str, por ejemplo "3x1 + 2x2"
            - numeroVariables: int, número de variables de decisión
            - restricciones: lista de dicts, cada uno con:
                - expr: str, expresión de la restricción, ej. "2x1 + 3x2"
                - op: str, operador "≤", "≥", "="
                - val: valor del lado derecho de la restricción (float o str convertible a float)

    Retorna:
        dict: Contiene el planteamiento, el modelo estándar y el resultado del simplex
    """
    tipo = data["tipoOperacion"]
    funcion = data["funcionObjetivo"]
    num_vars = data["numeroVariables"]
    restricciones = data["restricciones"]

    # Determinar si es maximización o minimización
    es_maximizacion = tipo.lower() in ["max", "maximizar"]

    # Parsear la función objetivo a una lista de coeficientes
    c = _parse_funcion(funcion, num_vars)
    
    # Si es minimización, convertir a maximización multiplicando por -1
    if not es_maximizacion:
        c = [-coef for coef in c]

    # Parsear las restricciones y aplicar transformaciones
    A, b, operadores = _procesar_restricciones(restricciones, num_vars)
    
    # Preparar el modelo estándar con variables artificiales y de holgura
    resultado_transformacion = _transformar_modelo_estandar(A, b, operadores, c, num_vars)
    
    # Resumen del planteamiento original
    planteamiento = {
        "tipo": tipo,
        "funcion_objetivo": funcion,
        "restricciones": restricciones
    }

    # Modelo estándar
    modelo_estandar = _generar_modelo_estandar_display(
        resultado_transformacion, num_vars, es_maximizacion  # <-- Quitado c_original
    )

    # Ejecutar el algoritmo simplex con Gran M
    resultado_simplex = _simplex_gran_m(resultado_transformacion, es_maximizacion)

    # Combinar todo en un solo diccionario de resultados
    return {
        "planteamiento": planteamiento,
        "modelo_estandar": modelo_estandar,
        **resultado_simplex
    }

def _procesar_restricciones(restricciones, num_vars):
    """Procesa las restricciones y las convierte a formato estándar"""
    A = []
    b = []
    operadores = []
    
    for r in restricciones:
        coeficientes = _parse_funcion(r["expr"], num_vars)
        valor_b = float(r["val"])
        operador = r["op"]
        
        # Si el valor del lado derecho es negativo, multiplicar toda la restricción por -1
        if valor_b < 0:
            coeficientes = [-c for c in coeficientes]
            valor_b = -valor_b
            # Cambiar el operador
            if operador == "≤":
                operador = "≥"
            elif operador == "≥":
                operador = "≤"
        
        A.append(coeficientes)
        b.append(valor_b)
        operadores.append(operador)
    
    return A, b, operadores

def _transformar_modelo_estandar(A, b, operadores, c, num_vars):
    """
    Transforma el modelo a forma estándar agregando variables de holgura y artificiales
    """
    num_restricciones = len(A)
    M = 1000000  # Valor grande para el método de la Gran M

    # Contar variables adicionales necesarias
    num_holgura = 0
    num_exceso = 0
    num_artificiales = 0
    
    for op in operadores:
        if op == "≤":
            num_holgura += 1
        elif op == "≥":
            num_exceso += 1
            num_artificiales += 1
        else:  # "="
            num_artificiales += 1

    total_nuevas = num_holgura + num_exceso + num_artificiales

    # Construir c extendida
    c_extendida = list(c) + [0.0] * (num_holgura + num_exceso) + [-M] * num_artificiales

    # Matriz extendida
    A_extendida = []
    variables_basicas = []
    variables_info = {
        'holgura': [],
        'exceso': [],
        'artificiales': []
    }

    # Índices para nuevas variables
    idx_holgura = 0
    idx_exceso = 0
    idx_artificial = 0

    for i, (fila, operador) in enumerate(zip(A, operadores)):
        # Nueva fila: variables originales + ceros para nuevas variables
        fila_extendida = fila + [0.0] * total_nuevas
        
        if operador == "≤":
            # Posición de la variable de holgura
            pos_holgura = num_vars + idx_holgura
            fila_extendida[pos_holgura] = 1.0
            variables_info['holgura'].append(pos_holgura)
            variables_basicas.append(f"s{idx_holgura + 1}")
            idx_holgura += 1
            
        elif operador == "≥":
            # Posición variable de exceso
            pos_exceso = num_vars + num_holgura + idx_exceso
            fila_extendida[pos_exceso] = -1.0
            variables_info['exceso'].append(pos_exceso)
            idx_exceso += 1
            
            # Posición variable artificial
            pos_artificial = num_vars + num_holgura + num_exceso + idx_artificial
            fila_extendida[pos_artificial] = 1.0
            variables_info['artificiales'].append(pos_artificial)
            variables_basicas.append(f"a{idx_artificial + 1}")
            idx_artificial += 1
            
        else:  # "="
            # Posición variable artificial
            pos_artificial = num_vars + num_holgura + num_exceso + idx_artificial
            fila_extendida[pos_artificial] = 1.0
            variables_info['artificiales'].append(pos_artificial)
            variables_basicas.append(f"a{idx_artificial + 1}")
            idx_artificial += 1
        
        A_extendida.append(fila_extendida)

    return {
        'A': A_extendida,
        'b': b,
        'c': c_extendida,
        'variables_basicas': variables_basicas,
        'variables_info': variables_info,
        'num_vars_originales': num_vars,
        'M': M,
        'operadores': operadores
    }

def _generar_modelo_estandar_display(resultado_transformacion, num_vars, es_maximizacion):
    """Genera la representación en string del modelo estándar"""
    A = resultado_transformacion['A']
    b = resultado_transformacion['b']
    c_ext = resultado_transformacion['c']
    
    # Función objetivo
    tipo_obj = "Maximizar" if es_maximizacion else "Minimizar"
    
    partes_fo = []
    for i, coef in enumerate(c_ext):
        if coef != 0:
            if i < num_vars:
                var_name = f"x{i+1}"
            elif 's' in resultado_transformacion['variables_basicas']:
                var_name = f"s{i-num_vars+1}"  # Simplificado
            else:
                var_name = f"var{i+1}"
            
            if coef == resultado_transformacion['M']:
                coef_str = "M"
            elif coef == -resultado_transformacion['M']:
                coef_str = "-M"
            else:
                coef_str = str(coef)
            
            if coef > 0 and partes_fo:
                partes_fo.append(f"+ {coef_str}{var_name}")
            else:
                partes_fo.append(f"{coef_str}{var_name}")
    
    funcion_objetivo = f"{tipo_obj} Z = " + " ".join(partes_fo)
    
    # Restricciones
    restricciones = []
    for i, (fila, valor_b) in enumerate(zip(A, b)):
        partes = []
        for j, coef in enumerate(fila):
            if coef != 0:
                if j < num_vars:
                    var_name = f"x{j+1}"
                else:
                    var_name = f"var{j+1}"
                
                if coef > 0 and partes:
                    partes.append(f"+ {coef}{var_name}")
                else:
                    partes.append(f"{coef}{var_name}")
        
        restriccion_str = " ".join(partes) + f" = {valor_b}"
        restricciones.append(restriccion_str)
    
    # Variables no negativas
    variables = [f"x{i+1} ≥ 0" for i in range(num_vars)]
    
    return {
        "funcion_objetivo": funcion_objetivo,
        "restricciones": restricciones,
        "variables": variables
    }

def _simplex_gran_m(datos, es_maximizacion):
    """
    Ejecuta el método simplex con Gran M - VERSIÓN CORREGIDA
    """
    A = datos['A']
    b = datos['b']
    c = datos['c']
    variables_basicas = datos['variables_basicas'][:]
    M = datos['M']
    num_vars_originales = datos['num_vars_originales']
    
    # Construir tableau inicial
    tableau = []
    for i, fila in enumerate(A):
        tableau.append(fila + [b[i]])
    
    # Fila Z inicial CORREGIDA
    z_fila = [-ci for ci in c] + [0.0]
    
    # CORRECCIÓN: Eliminación correcta de variables artificiales
    for i, var in enumerate(variables_basicas):
        if var.startswith('a'):  # Variable artificial
            # Encontrar la columna de esta variable artificial
            col_artificial = None
            for j in range(len(z_fila) - 1):
                if abs(tableau[i][j] - 1.0) < 1e-6:  # Tolerancia para floats
                    col_artificial = j
                    break
            
            if col_artificial is not None:
                # CORRECCIÓN: Restar M veces la fila en lugar de sumar
                factor = M if es_maximizacion else -M
                for j in range(len(z_fila)):
                    z_fila[j] -= factor * tableau[i][j]
    
    tableau.append(z_fila)
    
    iteraciones = []
    max_iter = 100  # Prevenir bucles infinitos
    iter_count = 0
    
    # Algoritmo simplex
    while iter_count < max_iter:
        iter_count += 1
        
        # Preparar información de la iteración
        num_vars_tableau = len(tableau[0]) - 1
        encabezados = ["VB"] + [f"x{i+1}" for i in range(num_vars_originales)]
        
        # Agregar encabezados para variables adicionales
        contador_s = 1
        contador_e = 1
        contador_a = 1
        
        for i in range(num_vars_originales, num_vars_tableau):
            var_type = None
            # Determinar tipo de variable basándose en el nombre básico
            for vb in variables_basicas:
                if f"s{contador_s}" == vb:
                    encabezados.append(f"s{contador_s}")
                    contador_s += 1
                    var_type = 's'
                    break
                elif f"e{contador_e}" == vb:
                    encabezados.append(f"e{contador_e}")
                    contador_e += 1
                    var_type = 'e'
                    break
                elif f"a{contador_a}" == vb:
                    encabezados.append(f"a{contador_a}")
                    contador_a += 1
                    var_type = 'a'
                    break
            
            if not var_type:
                encabezados.append(f"var{i+1}")
        
        encabezados.append("RHS")
        
        # Crear filas para mostrar
        filas_str = []
        for i in range(len(tableau)):
            if i < len(variables_basicas):
                fila = [variables_basicas[i]] + [round(c, 4) for c in tableau[i]]
            else:
                fila = ["Z"] + [round(c, 4) for c in tableau[i]]
            filas_str.append(fila)
        
        # Información de la iteración
        iteracion = {
            "encabezados": encabezados,
            "filas": filas_str,
            "variables_basicas": variables_basicas[:],
            "detalles": None
        }
        
        # Verificar optimalidad - CORRECCIÓN PARA MINIMIZACIÓN
        z_row = tableau[-1][:-1]
        optimal = False
        
        if es_maximizacion:
            optimal = all(v >= -1e-6 for v in z_row)  # Tolerancia para maximización
        else:
            optimal = all(v <= 1e-6 for v in z_row)  # Tolerancia para minimización
        
        if optimal:
            iteraciones.append(iteracion)
            break
        
        # Seleccionar columna pivote - CORRECCIÓN PARA MINIMIZACIÓN
        if es_maximizacion:
            # Para maximización: columna con coeficiente más negativo
            col_pivote = min(range(len(z_row)), key=lambda i: z_row[i])
            valor_col = z_row[col_pivote]
            if valor_col >= -1e-6:  # Ya es óptimo
                break
        else:
            # Para minimización: columna con coeficiente más positivo
            col_pivote = max(range(len(z_row)), key=lambda i: z_row[i])
            valor_col = z_row[col_pivote]
            if valor_col <= 1e-6:  # Ya es óptimo
                break
        
        var_pivote = encabezados[col_pivote + 1]
        
        # Calcular razones
        razones = []
        razon_justificaciones = []
        
        for i in range(len(variables_basicas)):
            coef = tableau[i][col_pivote]
            rhs = tableau[i][-1]
            
            if coef > 1e-6:  # Positivo con tolerancia
                razon = rhs / coef
                razones.append(razon)
            else:
                razon = float("inf")
                razones.append(razon)
            
            razon_justificaciones.append({
                "fila": i + 1,
                "rhs": round(rhs, 4),
                "coef_pivote": round(coef, 4),
                "razon": round(razon, 4) if razon != float("inf") else "infinito"
            })
        
        # Verificar si es no acotada
        if all(r == float("inf") for r in razones):
            return {
                "optimo": None,
                "valores": None,
                "status": "no_acotada",
                "iteraciones": iteraciones,
                "mensaje": "El problema no está acotado"
            }
        
        # Seleccionar fila pivote
        fila_pivote = min(range(len(razones)), key=lambda i: razones[i])
        pivote = tableau[fila_pivote][col_pivote]
        
        # Evitar división por cero
        if abs(pivote) < 1e-10:
            return {
                "optimo": None,
                "valores": None,
                "status": "error",
                "iteraciones": iteraciones,
                "mensaje": "Pivote cero, no se puede continuar"
            }
        
        # Operaciones pivote
        fila_antigua = tableau[fila_pivote][:]
        fila_normalizada = [v / pivote for v in fila_antigua]
        tableau[fila_pivote] = fila_normalizada
        
        # Transformaciones
        transformaciones = []
        for i in range(len(tableau)):
            if i != fila_pivote:
                factor = tableau[i][col_pivote]
                original = tableau[i][:]
                resultado = [a - factor * b for a, b in zip(original, fila_normalizada)]
                tableau[i] = resultado
                
                transformaciones.append({
                    "fila": i + 1 if i < len(variables_basicas) else "Z",
                    "factor": round(factor, 4),
                    "original": [round(x, 4) for x in original],
                    "explicacion": f"Fila nueva = Fila original - ({round(factor, 4)} × fila pivote normalizada)",
                    "resultado": [round(x, 4) for x in resultado]
                })
        
        # Actualizar variable básica
        variables_basicas[fila_pivote] = var_pivote
        
        # Detalles de la iteración
        detalles = {
            "columna_pivote": {
                "variable": var_pivote,
                "explicacion": f"Se selecciona '{var_pivote}' por tener el coeficiente más {'negativo' if es_maximizacion else 'positivo'} en Z ({round(valor_col, 4)})"
            },
            "fila_pivote": {
                "indice": fila_pivote + 1,
                "razones": razon_justificaciones,
                "explicacion": f"Se elige la fila {fila_pivote + 1} por tener la razón mínima"
            },
            "normalizacion": {
                "original": [round(x, 4) for x in fila_antigua],
                "pivote": round(pivote, 4),
                "resultado": [round(x, 4) for x in fila_normalizada],
                "explicacion": f"Dividir fila pivote entre {round(pivote, 4)}"
            },
            "transformaciones": transformaciones
        }
        
        iteracion["detalles"] = detalles
        iteraciones.append(iteracion)
    
    if iter_count >= max_iter:
        return {
            "optimo": None,
            "valores": None,
            "status": "error",
            "iteraciones": iteraciones,
            "mensaje": "Número máximo de iteraciones alcanzado"
        }
    
    # Extraer solución
    solucion = [0.0] * num_vars_originales
    
    for i, var in enumerate(variables_basicas):
        if var.startswith('x'):
            try:
                var_num = int(var[1:]) - 1
                if 0 <= var_num < num_vars_originales:
                    solucion[var_num] = tableau[i][-1]
            except:
                continue
    
    # Valor óptimo
    valor_z = tableau[-1][-1]
    
    # CORRECCIÓN: Ajuste final para minimización
    if not es_maximizacion:
        valor_z = -valor_z

    # Verificar factibilidad (variables artificiales deben ser 0)
    artificiales_positivas = []
    for i, var in enumerate(variables_basicas):
        if var.startswith('a') and abs(tableau[i][-1]) > 1e-6:
            artificiales_positivas.append((var, tableau[i][-1]))
    
    if artificiales_positivas:
        return {
            "optimo": None,
            "valores": None,
            "status": "infactible",
            "iteraciones": iteraciones,
            "mensaje": f"Variables artificiales en la base: {', '.join([f'{var}={val:.4f}' for var, val in artificiales_positivas])}"
        }
    
    return {
        "optimo": valor_z,
        "valores": solucion,
        "status": "ok",
        "iteraciones": iteraciones
    }

def _parse_funcion(expr, num_vars):
    """
    Parsea una expresión lineal y la convierte en una lista de coeficientes.
    Maneja coeficientes negativos correctamente.
    """
    import re
    coef = [0.0] * num_vars
    
    # Limpiar la expresión
    expr = expr.replace(" ", "").replace("−", "-")
    
    # Agregar + al inicio si no empieza con - o +
    if not expr.startswith(('+', '-')):
        expr = '+' + expr
    
    # Encontrar todos los términos
    pattern = r'([+-]?)(\d*\.?\d*)\s*x(\d+)'
    matches = re.findall(pattern, expr)
    
    for signo, coef_str, var_num in matches:
        # Determinar el coeficiente
        if coef_str == "":
            coef_val = 1.0
        else:
            coef_val = float(coef_str)
        
        # Aplicar el signo
        if signo == "-":
            coef_val = -coef_val
        
        # Asignar al índice correcto
        var_idx = int(var_num) - 1
        if 0 <= var_idx < num_vars:
            coef[var_idx] = coef_val
    
    return coef