import logging
from copy import deepcopy
import numpy as np

# Configuración básica de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def resolver_simplex_clasico(data):
    """
    Resuelve un problema de programación lineal de maximización usando el método simplex clásico.

    Parámetros:
        data (dict): Diccionario con la siguiente estructura:
            - tipoOperacion: "max" o "maximizar"
            - funcionObjetivo: str, por ejemplo "3x1 + 2x2"
            - numeroVariables: int, número de variables de decisión
            - restricciones: lista de dicts, cada uno con:
                - expr: str, expresión de la restricción, ej. "2x1 + 3x2"
                - val: valor del lado derecho de la restricción (float o str convertible a float)

    Retorna:
        dict: Contiene el planteamiento, el modelo estándar y el resultado del simplex (óptimo, valores, iteraciones, etc.)
    """
    tipo = data["tipoOperacion"]
    funcion = data["funcionObjetivo"]
    num_vars = data["numeroVariables"]
    restricciones = data["restricciones"]

    # Solo se permite maximización
    if tipo.lower() not in ["max", "maximizar"]:
        raise ValueError("Solo se permite maximización")

    # Parsear la función objetivo a una lista de coeficientes
    c = _parse_funcion(funcion, num_vars)

    # Parsear las restricciones a matrices A (coeficientes) y b (términos independientes)
    A = []
    b = []
    for r in restricciones:
        A.append(_parse_funcion(r["expr"], num_vars))
        b.append(float(r["val"]))

    # Resumen del planteamiento original
    planteamiento = {
        "tipo": tipo,
        "funcion_objetivo": funcion,
        "restricciones": restricciones
    }

    # Modelo estándar (con variables de holgura)
    modelo_estandar = {
        "funcion_objetivo": _formatear_funcion_objetivo_estandar(c),
        "restricciones": [
            " + ".join([f"{A[i][j]}x{j+1}" for j in range(num_vars)]) + f" + s{i+1} = {b[i]}"
            for i in range(len(A))
        ],
        "variables": [f"x{i+1} ≥ 0" for i in range(num_vars)] + [f"s{i+1} ≥ 0" for i in range(len(A))]
    }

    # Ejecutar el algoritmo simplex
    resultado_simplex = _simplex(c, A, b)

    # Combinar todo en un solo diccionario de resultados
    return {
        "planteamiento": planteamiento,
        "modelo_estandar": modelo_estandar,
        **resultado_simplex
    }

def _formatear_funcion_objetivo_estandar(c):
    """
    Formatea la función objetivo en notación estándar para mostrarla como string.

    Parámetros:
        c (list): Lista de coeficientes de la función objetivo.

    Retorna:
        str: Representación en string de la función objetivo estándar.
    """
    partes = []
    for i, coef in enumerate(c):
        if coef != 0:
            signo = "-" if coef > 0 else "+"
            partes.append(f"{signo} {abs(coef)}x{i+1}")
    return "Z " + " ".join(partes) + " = 0"

def _parse_funcion(expr, num_vars):
    """
    Parsea una expresión lineal (ej: "3x1 + 2x2") y la convierte en una lista de coeficientes.

    Parámetros:
        expr (str): Expresión de la función o restricción.
        num_vars (int): Número de variables de decisión.

    Retorna:
        list: Lista de coeficientes (floats) de longitud num_vars.
    """
    import re
    coef = [0.0] * num_vars
    expr = expr.replace("-", "+-")  # Para separar bien los términos negativos
    partes = expr.split("+")
    for parte in partes:
        parte = parte.strip()
        if not parte:
            continue
        # Busca patrones tipo "3x1", "-2x2", "x3", etc.
        match = re.match(r"(-?\d*\.?\d*)\s*x(\d+)", parte)
        if match:
            # Si el coeficiente es vacío o "-", se asume 1 o -1
            coef_val = float(match.group(1)) if match.group(1) not in ["", "-"] else float(match.group(1) + "1")
            var_idx = int(match.group(2)) - 1
            coef[var_idx] = coef_val
    return coef

def _simplex(c, A, b):
    """
    Ejecuta el método simplex clásico para maximización con restricciones de tipo <=.

    Parámetros:
        c (list): Coeficientes de la función objetivo.
        A (list of lists): Matriz de coeficientes de las restricciones.
        b (list): Lado derecho de las restricciones.

    Retorna:
        dict: Contiene el valor óptimo, los valores de las variables, el estado y el detalle de las iteraciones.
    """
    num_vars = len(c)
    num_rest = len(A)

    tableau = []        # Tabla simplex (matriz aumentada)
    iteraciones = []    # Lista de iteraciones para mostrar el proceso paso a paso
    vb = [f"s{i+1}" for i in range(num_rest)]  # Variables básicas iniciales (holguras)

    # Construir el tableau inicial (agregando variables de holgura)
    for i in range(num_rest):
        fila = A[i] + [0.0] * num_rest + [b[i]]  # Coeficientes + holguras + RHS
        fila[num_vars + i] = 1.0                 # La holgura correspondiente es 1
        tableau.append(fila)

    # Fila Z (función objetivo, negativa para maximización)
    z_fila = [-ci for ci in c] + [0.0] * num_rest + [0.0]
    tableau.append(z_fila)

    # Bucle principal del método simplex
    while True:
        # Encabezados para mostrar la tabla
        encabezados = ["VB"] + [f"x{i+1}" for i in range(num_vars)] + [f"s{i+1}" for i in range(num_rest)] + ["RHS"]
        filas_str = []
        for i in range(len(tableau)):
            if i < len(vb):
                fila = [vb[i]] + [round(c, 2) for c in tableau[i]]
            else:
                fila = ["Z"] + [round(c, 2) for c in tableau[i]]
            filas_str.append(fila)

        # Guardar la iteración actual (para mostrar el paso a paso)
        iteracion = {
            "encabezados": encabezados,
            "filas": filas_str,
            "variables_basicas": vb.copy(),
            "detalles": None
        }

        # Comprobar si la solución es óptima (todos los coeficientes de Z >= 0)
        z_row = tableau[-1][:-1]
        if all(v >= 0 for v in z_row):
            iteraciones.append(iteracion)
            break

        # Seleccionar columna pivote (la más negativa en Z)
        col = z_row.index(min(z_row))
        var_pivote = encabezados[col + 1]
        valor_col = z_row[col]

        # Calcular razones para seleccionar la fila pivote
        razones = []
        razon_just = []
        for i in range(num_rest):
            coef = tableau[i][col]
            rhs = tableau[i][-1]
            if coef > 0:
                razon = rhs / coef
                razones.append(razon)
            else:
                razon = float("inf")
                razones.append(razon)
            razon_just.append({
                "fila": int(i + 1),
                "rhs": float(round(rhs, 4)),
                "coef_pivote": float(round(coef, 4)),
                "razon": float(round(razon, 4)) if razon != float("inf") else "infinito"
            })

        # Si todas las razones son infinitas, la solución es no acotada
        if all(r == float("inf") for r in razones):
            raise Exception("Solución no acotada")

        # Seleccionar la fila pivote (mínima razón positiva)
        fila_pivote = razones.index(min(razones))
        pivote = tableau[fila_pivote][col]

        # Normalizar la fila pivote (dividir por el pivote)
        fila_antigua = tableau[fila_pivote][:]
        fila_normalizada = [v / pivote for v in fila_antigua]
        tableau[fila_pivote] = fila_normalizada

        # Actualizar las demás filas para hacer ceros en la columna pivote
        transformaciones = []
        for i in range(len(tableau)):
            if i != fila_pivote:
                factor = tableau[i][col]
                original = tableau[i][:]
                resultado = [a - factor * b for a, b in zip(original, fila_normalizada)]
                tableau[i] = resultado
                transformaciones.append({
                    "fila": int(i + 1),
                    "factor": float(round(factor, 4)),
                    "original": [float(round(x, 4)) for x in original],
                    "explicacion": f"Fila nueva = Fila original - ({float(round(factor,4))} × fila pivote normalizada)",
                    "resultado": [float(round(x, 4)) for x in resultado]
                })

        # Actualizar la variable básica de la fila pivote
        vb[fila_pivote] = var_pivote

        # Guardar detalles de la iteración para explicación paso a paso
        detalles = {
            "columna_pivote": {
                "variable": var_pivote,
                "explicacion": f"Se selecciona la columna pivote '{var_pivote}' porque tiene el valor más negativo en la fila Z ({round(valor_col, 4)}), lo cual indica la mayor mejora posible en la función objetivo."
            },
            "fila_pivote": {
                "indice": fila_pivote + 1,
                "razones": razon_just,
                "explicacion": f"Se elige la fila {fila_pivote + 1} porque tiene la razón mínima entre RHS y el coeficiente pivote."
            },
            "normalizacion": {
                "original": [round(x, 4) for x in fila_antigua],
                "pivote": round(pivote, 4),
                "resultado": [round(x, 4) for x in fila_normalizada],
                "explicacion": f"Se divide cada elemento de la fila pivote entre el valor del pivote ({round(pivote, 4)})."
            },
            "transformaciones": transformaciones
        }

        iteracion["detalles"] = detalles
        iteraciones.append(iteracion)

    # Extraer la solución óptima (valores de las variables originales)
    solucion = [0.0] * num_vars
    for i in range(num_rest):
        for j in range(num_vars):
            col_data = [fila[j] for fila in tableau]
            # Si la columna es canónica (un 1 y el resto 0), la variable está en la base
            if col_data.count(1) == 1 and all(c == 0 for k, c in enumerate(col_data) if k != i):
                solucion[j] = tableau[i][-1]

    return {
        "optimo": tableau[-1][-1],   # Valor óptimo de la función objetivo
        "valores": solucion,         # Valores de las variables originales
        "status": "ok",
        "iteraciones": iteraciones   # Detalle paso a paso de cada iteración
    }




