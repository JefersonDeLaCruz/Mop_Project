def resolver_simplex_clasico(data):
    tipo = data["tipoOperacion"]
    funcion = data["funcionObjetivo"]
    num_vars = data["numeroVariables"]
    restricciones = data["restricciones"]

    if tipo.lower() not in  ["max", "maximizar"]:
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



from copy import deepcopy
import numpy as np


def _simplex(c, A, b):

    num_vars = len(c)
    num_rest = len(A)

    tableau = []
    iteraciones = []

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
        encabezados = [f"x{i+1}" for i in range(num_vars)] + [f"s{i+1}" for i in range(num_rest)] + ["RHS"]
        filas_str = [[round(c, 2) for c in fila] for fila in tableau]
        iteraciones.append({"encabezados": encabezados, "filas": filas_str})

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

        # Normalizar fila pivote
        tableau[fila_pivote] = [v / pivote for v in tableau[fila_pivote]]

        # Hacer ceros en la columna pivote
        for i in range(len(tableau)):
            if i != fila_pivote:
                factor = tableau[i][col]
                tableau[i] = [a - factor * b for a, b in zip(tableau[i], tableau[fila_pivote])]

    # Resultado
    solucion = [0.0] * num_vars
    for i in range(num_rest):
        for j in range(num_vars):
            col = [fila[j] for fila in tableau]
            if col.count(1) == 1 and all(c == 0 for k, c in enumerate(col) if k != i):
                solucion[j] = tableau[i][-1]

    return {
        "optimo": tableau[-1][-1],
        "valores": solucion,
        "status": "ok",
        "iteraciones": iteraciones
    }
