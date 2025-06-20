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
        fila[num_vars + i] = 1.0
        tableau.append(fila)

    z_fila = [-ci for ci in c] + [0.0] * num_rest + [0.0]
    tableau.append(z_fila)

    while True:
        encabezados = ["VB"] + [f"x{i+1}" for i in range(num_vars)] + [f"s{i+1}" for i in range(num_rest)] + ["RHS"]
        filas_str = []
        for i in range(len(tableau)):
            if i < len(vb):
                fila = [vb[i]] + [round(c, 2) for c in tableau[i]]
            else:
                fila = ["Z"] + [round(c, 2) for c in tableau[i]]
            filas_str.append(fila)

        iteracion = {
            "encabezados": encabezados,
            "filas": filas_str,
            "variables_basicas": vb.copy(),
            "detalles": None
        }

        z_row = tableau[-1][:-1]
        if all(v >= 0 for v in z_row):
            iteraciones.append(iteracion)
            break

        col = z_row.index(min(z_row))
        var_pivote = encabezados[col + 1]
        valor_col = z_row[col]

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
                "fila": i + 1,
                "rhs": round(rhs, 4),
                "coef_pivote": round(coef, 4),
                "razon": round(razon, 4) if razon != float("inf") else "infinito"
            })

        if all(r == float("inf") for r in razones):
            raise Exception("Solución no acotada")

        fila_pivote = razones.index(min(razones))
        pivote = tableau[fila_pivote][col]

        fila_antigua = tableau[fila_pivote][:]
        fila_normalizada = [v / pivote for v in fila_antigua]
        tableau[fila_pivote] = fila_normalizada

        transformaciones = []
        for i in range(len(tableau)):
            if i != fila_pivote:
                factor = tableau[i][col]
                original = tableau[i][:]
                resultado = [a - factor * b for a, b in zip(original, fila_normalizada)]
                tableau[i] = resultado
                transformaciones.append({
                    "fila": i + 1,
                    "factor": round(factor, 4),
                    "original": [round(x, 4) for x in original],
                    "explicacion": f"Fila nueva = Fila original - ({factor} × fila pivote normalizada)",
                    "resultado": [round(x, 4) for x in resultado]
                })

        vb[fila_pivote] = var_pivote

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
