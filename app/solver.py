from scipy.optimize import linprog
import re

def extraer_coeficientes(expr, n_vars):
    expr = expr.replace(" ", "")
    coeficientes = [0] * n_vars
    patrones = re.findall(r'([+-]?\d*?)([a-zA-Z])(\d+)', expr)
    for coef, var, idx in patrones:
        idx = int(idx) - 1
        if coef in ("", "+"):
            coef = 1
        elif coef == "-":
            coef = -1
        else:
            coef = int(coef)
        coeficientes[idx] = coef
    return coeficientes

def procesar_funcion_objetivo(expr, tipo, n_vars):
    coefs = extraer_coeficientes(expr, n_vars)
    if tipo.lower() == "maximizar":
        coefs = [-c for c in coefs]
    return coefs

def procesar_restriccion(expr, operador, valor, n_vars):
    fila = extraer_coeficientes(expr, n_vars)
    if operador == "≤":
        return fila, float(valor), "ub"
    elif operador == "≥":
        fila = [-x for x in fila]
        return fila, -float(valor), "ub"
    elif operador == "=":
        return fila, float(valor), "eq"
    else:
        raise ValueError(f"Operador no válido: {operador}")

def armar_matrices(restricciones, n_vars):
    A_ub, b_ub = [], []
    A_eq, b_eq = [], []
    for r in restricciones:
        fila, b, tipo = procesar_restriccion(r["expr"], r["op"], r["val"], n_vars)
        if tipo == "ub":
            A_ub.append(fila)
            b_ub.append(b)
        elif tipo == "eq":
            A_eq.append(fila)
            b_eq.append(b)
    return A_ub or None, b_ub or None, A_eq or None, b_eq or None

def resolver_problema_lp(tipo, funcion, restricciones, n_vars):
    c = procesar_funcion_objetivo(funcion, tipo, n_vars)
    A_ub, b_ub, A_eq, b_eq = armar_matrices(restricciones, n_vars)
    bounds = [(0, None)] * n_vars

    res = linprog(c=c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")

    if res.success:
        return {
            "valores": res.x.tolist(),
            "optimo": res.fun * (-1 if tipo.lower() == "maximizar" else 1),
            "status": "ok"
        }
    else:
        return {
            "status": "error",
            "mensaje": res.message
        }
