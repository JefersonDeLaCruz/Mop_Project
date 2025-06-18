import re
import numpy as np
from fractions import Fraction

def extraer_coeficientes(expr, n_vars):
    """
    Versión mejorada que maneja:
    - Coeficientes implícitos (x1 en lugar de 1x1)
    - Términos constantes
    - Variables fuera de orden
    """
    expr = expr.replace(" ", "").lower()
    coeficientes = [0.0] * n_vars
    constante = 0.0
    
    # Manejar términos constantes
    if expr.isdigit() or (expr.startswith('-') and expr[1:].isdigit()):
        constante = float(expr)
        return coeficientes, constante
    
    # Encontrar todos los términos (coeficiente + variable)
    patron = r'([+-]?)(\d*\.?\d*)([a-z])(\d+)'
    matches = re.findall(patron, expr)
    
    for signo, num, var, idx in matches:
        try:
            idx = int(idx) - 1
            if idx >= n_vars or idx < 0:
                continue
        except:
            continue
        
        # Determinar coeficiente
        if num == '' or num == '.':
            coef = 1.0
        else:
            coef = float(num) if '.' in num else int(num or '1')
        
        if signo == '-':
            coef = -coef
        
        coeficientes[idx] = coef
    
    # Manejar término constante separado
    constant_match = re.search(r'([+-]\d+\.?\d*)$', expr.split('=')[0])
    if constant_match:
        constante = float(constant_match.group(1))
    
    return coeficientes, constante

def procesar_restriccion(expr, operador, valor, n_vars):
    """
    Devuelve coeficientes, constante y tipo de restricción
    """
    coeficientes, constante = extraer_coeficientes(expr, n_vars)
    valor = float(valor) - constante
    
    if operador == "≤":
        return coeficientes, valor, "ub"
    elif operador == "≥":
        return [-c for c in coeficientes], -valor, "ub"
    elif operador == "=":
        return coeficientes, valor, "eq"
    else:
        raise ValueError(f"Operador no válido: {operador}")

def construir_tableau_simplex(c, A_ub, b_ub, A_eq, b_eq, n_vars):
    """
    Construye el tableau inicial para simplex
    """
    # Convertir todo a fracciones para precisión
    c = [Fraction(x).limit_denominator() for x in c]
    
    # Número de restricciones
    n_ub = len(b_ub) if A_ub else 0
    n_eq = len(b_eq) if A_eq else 0
    n_total_rest = n_ub + n_eq
    
    # Crear matriz tableau
    tableau = np.zeros((n_total_rest + 1, n_vars + n_total_rest + 1), dtype=Fraction)
    
    # Función objetivo (fila 0)
    for j in range(n_vars):
        tableau[0, j] = -c[j]  # Negativo porque estamos maximizando
    
    # Restricciones de desigualdad (≤)
    for i in range(n_ub):
        for j in range(n_vars):
            tableau[i+1, j] = Fraction(A_ub[i][j]).limit_denominator()
        # Variable de holgura
        tableau[i+1, n_vars + i] = Fraction(1)
        # Lado derecho
        tableau[i+1, -1] = Fraction(b_ub[i]).limit_denominator()
    
    # Restricciones de igualdad (=)
    for i in range(n_eq):
        row_idx = n_ub + i + 1
        for j in range(n_vars):
            tableau[row_idx, j] = Fraction(A_eq[i][j]).limit_denominator()
        # Variable artificial (para método de 2 fases)
        tableau[row_idx, n_vars + n_ub + i] = Fraction(1)
        # Lado derecho
        tableau[row_idx, -1] = Fraction(b_eq[i]).limit_denominator()
    
    return tableau.tolist()

def simplex_paso_a_paso(c, A_ub, b_ub, A_eq, b_eq, n_vars):
    """
    Implementación básica de simplex paso a paso
    Devuelve cada iteración del tableau
    """
    tableau = construir_tableau_simplex(c, A_ub, b_ub, A_eq, b_eq, n_vars)
    pasos = [{"iteracion": 0, "tabla": tableau}]
    
    n_filas = len(tableau)
    n_columnas = len(tableau[0])
    
    iteracion = 0
    max_iter = 100  # Prevenir bucles infinitos
    
    while iteracion < max_iter:
        iteracion += 1
        
        # Encontrar columna pivote (más negativo en fila 0)
        col_pivote = -1
        min_val = 0
        for j in range(n_columnas - 1):
            if tableau[0][j] < min_val:
                min_val = tableau[0][j]
                col_pivote = j
        
        # Si no hay negativos, solución óptima
        if col_pivote == -1:
            break
        
        # Encontrar fila pivote (mínima razón positiva)
        fila_pivote = -1
        min_ratio = float('inf')
        for i in range(1, n_filas):
            if tableau[i][col_pivote] > 0:
                ratio = tableau[i][-1] / tableau[i][col_pivote]
                if ratio < min_ratio:
                    min_ratio = ratio
                    fila_pivote = i
        
        # Si no se encuentra fila pivote, problema no acotado
        if fila_pivote == -1:
            break
        
        # Operaciones de fila para el pivote
        pivot_val = tableau[fila_pivote][col_pivote]
        
        # Normalizar fila pivote
        for j in range(n_columnas):
            tableau[fila_pivote][j] /= pivot_val
        
        # Hacer ceros en otras filas
        for i in range(n_filas):
            if i == fila_pivote:
                continue
            factor = tableau[i][col_pivote]
            for j in range(n_columnas):
                tableau[i][j] -= factor * tableau[fila_pivote][j]
        
        # Guardar estado actual
        pasos.append({
            "iteracion": iteracion,
            "tabla": [row[:] for row in tableau],
            "pivote_col": col_pivote,
            "pivote_fila": fila_pivote
        })
    
    return pasos