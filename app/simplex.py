
#implmemtacion metodo simplex paso a paso




import numpy as np

def simplex_clasico_paso_a_paso(funcion_objetivo, restricciones, n_vars):
    n_rest = len(restricciones)

    tabla = np.zeros((n_rest + 1, n_vars + n_rest + 1))

    for i, restriccion in enumerate(restricciones):
        tabla[i, :n_vars] = restriccion['coeficientes']
        tabla[i, n_vars + i] = 1  # holgura
        tabla[i, -1] = restriccion['constante']

    tabla[-1, :n_vars] = -np.array(funcion_objetivo)

    pasos = []
    iteracion = 0

    while True:
        iteracion += 1
        paso = {
            "iteracion": iteracion,
            "tabla": tabla.tolist(),
            "pivote_col": None,
            "pivote_fila": None
        }
        col_pivote = np.argmin(tabla[-1, :-1])
        if tabla[-1, col_pivote] >= 0:
            paso["optimo"] = tabla[-1, -1]
            pasos.append(paso)
            break

        ratios = []
        for i in range(n_rest):
            if tabla[i, col_pivote] > 0:
                ratios.append(tabla[i, -1] / tabla[i, col_pivote])
            else:
                ratios.append(np.inf)

        fila_pivote = np.argmin(ratios)
        if ratios[fila_pivote] == np.inf:
            paso["error"] = "Problema no acotado"
            pasos.append(paso)
            break

        paso["pivote_col"] = col_pivote
        paso["pivote_fila"] = fila_pivote
        pasos.append(paso)

        pivote = tabla[fila_pivote, col_pivote]
        tabla[fila_pivote, :] /= pivote
        for i in range(n_rest + 1):
            if i != fila_pivote:
                tabla[i, :] -= tabla[i, col_pivote] * tabla[fila_pivote, :]

    return {"pasos": pasos, "status": "ok"}



