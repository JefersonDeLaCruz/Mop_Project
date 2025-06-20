from copy import deepcopy
import numpy as np


def resolver_simplex_clasico(data):
    tipo = data["tipoOperacion"]
    funcion = data["funcionObjetivo"]
    num_vars = data["numeroVariables"]
    restricciones = data["restricciones"]

    if tipo.lower() not in ["max", "maximizar"]:
        raise ValueError("Solo se permite maximización")

    # Parse función objetivo
    c = _parse_funcion(funcion, num_vars)

    # Parse restricciones
    A = []
    b = []
    for r in restricciones:
        A.append(_parse_funcion(r["expr"], num_vars))
        b.append(float(r["val"]))

    # Armar tabla inicial del método Simplex
    resultado = _simplex(c, A, b)

    return resultado


def _parse_funcion(expr, num_vars):
    import re
    coef = [0.0] * num_vars
    expr = expr.replace("-", "+-")  # para separar bien los términos negativos
    partes = expr.split("+")
    for parte in partes:
        parte = parte.strip()
        if not parte:
            continue
        match = re.match(r"(-?\d*\.?\d*)\s*x(\d+)", parte)
        if match:
            coef_val = float(match.group(1)) if match.group(1) not in ["", "-"] else float(match.group(1) + "1")
            var_idx = int(match.group(2)) - 1
            coef[var_idx] = coef_val
    return coef


def _simplex(c, A, b):
    num_vars = len(c)
    num_rest = len(A)

    tableau = []
    iteraciones = []
    vb = [f"s{i+1}" for i in range(num_rest)]  # Variables básicas iniciales

    # Crear matriz aumentada con variables de holgura
    for i in range(num_rest):
        fila = A[i] + [0.0] * num_rest + [b[i]]
        fila[num_vars + i] = 1.0  # variable de holgura
        tableau.append(fila)

    # Fila de función objetivo (Z)
    z_fila = [-ci for ci in c] + [0.0] * num_rest + [0.0]
    tableau.append(z_fila)

    # Iterar
    while True:
        encabezados = ["VB"] + [f"x{i+1}" for i in range(num_vars)] + [f"s{i+1}" for i in range(num_rest)] + ["RHS"]
        filas_str = []
        for i in range(len(tableau)):
            if i < len(vb):
                fila = [vb[i]] + [round(c, 2) for c in tableau[i]]
            else:
                fila = ["Z"] + [round(c, 2) for c in tableau[i]]
            filas_str.append(fila)

        iteraciones.append({
            "encabezados": encabezados,
            "filas": filas_str,
            "variables_basicas": vb.copy(),
            "detalles": None  # Se rellena luego si hay pivoteo
        })

        # Buscar columna pivote
        z_row = tableau[-1][:-1]
        if all(v >= 0 for v in z_row):
            break  # solución óptima encontrada

        col = z_row.index(min(z_row))
        razones = []
        for i in range(num_rest):
            if tableau[i][col] > 0:
                razones.append(tableau[i][-1] / tableau[i][col])
            else:
                razones.append(float("inf"))

        if all(r == float("inf") for r in razones):
            raise Exception("Solución no acotada")

        fila_pivote = razones.index(min(razones))
        pivote = tableau[fila_pivote][col]

        fila_antigua = tableau[fila_pivote][:]
        tableau[fila_pivote] = [v / pivote for v in tableau[fila_pivote]]
        fila_nueva = tableau[fila_pivote][:]

        detalles = {
            "columna_pivote": encabezados[col + 1],
            "fila_pivote": fila_pivote + 1,
            "pivote": round(pivote, 4),
            "fila_pivote_normalizada": [round(x, 4) for x in fila_nueva],
            "transformaciones": []
        }

        for i in range(len(tableau)):
            if i != fila_pivote:
                factor = tableau[i][col]
                fila_original = tableau[i][:]
                tableau[i] = [a - factor * b for a, b in zip(tableau[i], tableau[fila_pivote])]
                detalles["transformaciones"].append({
                    "fila": i + 1,
                    "factor": round(factor, 4),
                    "original": [round(x, 4) for x in fila_original],
                    "resultado": [round(x, 4) for x in tableau[i]]
                })

        vb[fila_pivote] = encabezados[col + 1]
        iteraciones[-1]["detalles"] = detalles

    # Resultado
    solucion = [0.0] * num_vars
    for i in range(num_rest):
        for j in range(num_vars):
            col_data = [fila[j] for fila in tableau]
            if col_data.count(1) == 1 and all(c == 0 for k, c in enumerate(col_data) if k != i):
                solucion[j] = tableau[i][-1]

    return {
        "optimo": tableau[-1][-1],
        "valores": solucion,
        "status": "ok",
        "iteraciones": iteraciones
    }
