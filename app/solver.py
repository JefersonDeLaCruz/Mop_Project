from scipy.optimize import linprog
import re

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

def resolver_problema_lp(tipo, funcion, restricciones, n_vars=None):
    # Extraer número de variables automáticamente si no se proporciona
    if n_vars is None:
        # Crear lista de todas las expresiones para analizarlas
        expresiones = [funcion] + [r["expr"] for r in restricciones]
        n_vars = extraer_numero_variables(expresiones)
        
        if n_vars == 0:
            return {
                "status": "error",
                "mensaje": "No se pudieron detectar variables en la función objetivo o restricciones"
            }
    
    c = procesar_funcion_objetivo(funcion, tipo, n_vars)
    A_ub, b_ub, A_eq, b_eq = armar_matrices(restricciones, n_vars)
    bounds = [(0, None)] * n_vars

    res = linprog(c=c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")

    

    if res.success:
        resultado =  {
            "valores": res.x.tolist(),
            "optimo": res.fun * (-1 if tipo.lower() == "maximizar" else 1),
            "status": "ok"
        }

        if n_vars == 2:
            resultado["graficable"] = True
            resultado["funcion_objetivo"] = {
                "coeficientes": c,
                "optimo": resultado["optimo"],
                "punto": res.x.tolist()
            }
            resultado['restricciones'] = {
                "A_ub": A_ub or [],
                "b_ub": b_ub or [],
                "A_eq": A_eq or [],
                "b_eq": b_eq or []
            }
        
        return resultado
    


    else:
        return {
            "status": "error",
            "mensaje": res.message
        }
