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
    """
    Extrae coeficientes de una expresión matemática de forma más robusta.
    Maneja casos como: '6x1+4x2+2x3', '6x1+2x2+6x3', '6x1+4x2', '2x1-2x2'
    """
    # Limpiar espacios y normalizar la expresión
    expr = expr.replace(" ", "").replace("−", "-")
    
    # Inicializar coeficientes en cero
    coeficientes = [0.0] * n_vars
    
    # Agregar '+' al inicio si no empieza con '+' o '-'
    if not expr.startswith(('+', '-')):
        expr = '+' + expr
    
    # Dividir por términos usando regex más robusta
    # Esta regex captura: signo opcional + número opcional + variable + índice
    pattern = r'([+-]?)(\d*\.?\d*)x(\d+)'
    matches = re.findall(pattern, expr)
    
    print(f"Expresión: {expr}")
    print(f"Matches encontrados: {matches}")
    
    for signo, coef_str, idx_str in matches:
        idx = int(idx_str) - 1  # Convertir a índice base 0
        
        if idx >= n_vars:
            print(f"Advertencia: Variable x{idx_str} excede el número de variables ({n_vars})")
            continue
            
        # Determinar el coeficiente
        if coef_str == "":
            # Casos como 'x1', '+x1', '-x1'
            coef = 1.0
        else:
            coef = float(coef_str)
        
        # Aplicar el signo
        if signo == '-':
            coef = -coef
        elif signo == '' and coef_str == "":
            # Caso especial: primer término sin signo explícito
            coef = 1.0
            
        coeficientes[idx] = coef
        print(f"Variable x{idx_str}: coeficiente = {coef}")
    
    print(f"Coeficientes finales: {coeficientes}")
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
    """
    Resuelve un problema de programación lineal usando SciPy.
    Mejorado para manejar mejor las restricciones de igualdad.
    """
    print(f"\n=== RESOLVIENDO PROBLEMA LP ===")
    print(f"Tipo: {tipo}")
    print(f"Función objetivo: {funcion}")
    print(f"Restricciones: {restricciones}")
    
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
    
    print(f"Número de variables: {n_vars}")
    
    # Procesar función objetivo
    c = procesar_funcion_objetivo(funcion, tipo, n_vars)
    print(f"Coeficientes función objetivo: {c}")
    
    # Procesar restricciones
    A_ub, b_ub, A_eq, b_eq = armar_matrices(restricciones, n_vars)
    
    print(f"Restricciones ≤ (A_ub): {A_ub}")
    print(f"Valores ≤ (b_ub): {b_ub}")
    print(f"Restricciones = (A_eq): {A_eq}")
    print(f"Valores = (b_eq): {b_eq}")
    
    # Definir bounds (variables no negativas)
    bounds = [(0, None)] * n_vars
    print(f"Bounds: {bounds}")

    try:
        # Intentar primero con el método 'highs-ds' que puede ser más preciso para problemas con igualdades
        res = linprog(
            c=c, 
            A_ub=A_ub, 
            b_ub=b_ub, 
            A_eq=A_eq, 
            b_eq=b_eq, 
            bounds=bounds, 
            method="highs-ds",
            options={'disp': True, 'presolve': True}  # Mostrar información de debugging
        )
        
        # Si no funciona, intentar con método clásico
        if not res.success:
            print("Intentando con método interior-point...")
            res = linprog(
                c=c, 
                A_ub=A_ub, 
                b_ub=b_ub, 
                A_eq=A_eq, 
                b_eq=b_eq, 
                bounds=bounds, 
                method="interior-point",
                options={'disp': True}
            )
        
        print(f"Resultado SciPy: {res}")
        print(f"Status: {res.success}")
        print(f"Message: {res.message}")
        
        if hasattr(res, 'x') and res.x is not None:
            print(f"Solución: {res.x}")
            print(f"Valor objetivo: {res.fun}")

        if res.success:
            # Calcular el valor objetivo correcto según el tipo de problema
            valor_objetivo = res.fun
            if tipo.lower() == "maximizar":
                valor_objetivo = -res.fun  # SciPy resuelve minimización, así que invertimos
            
            # Redondear valores para evitar errores numéricos pequeños
            valores_redondeados = [round(float(x), 8) for x in res.x]
            valor_objetivo_redondeado = round(float(valor_objetivo), 8)
            
            # Verificar que la solución satisface las restricciones de igualdad
            if A_eq is not None and b_eq is not None:
                import numpy as np
                residuos_eq = np.dot(A_eq, valores_redondeados) - b_eq
                max_residuo = max(abs(r) for r in residuos_eq) if residuos_eq.size > 0 else 0
                print(f"Máximo residuo en restricciones de igualdad: {max_residuo}")
                
                # Si hay residuos grandes, intentar ajustar la solución
                if max_residuo > 1e-6:
                    print("Advertencia: Residuos grandes en restricciones de igualdad")
            
            resultado = {
                "valores": valores_redondeados,
                "optimo": valor_objetivo_redondeado,
                "status": "ok"
            }

            # Información adicional para problemas con 2 variables (graficables)
            if n_vars == 2:
                resultado["graficable"] = True
                resultado["funcion_objetivo"] = {
                    "coeficientes": c,
                    "optimo": resultado["optimo"],
                    "punto": resultado["valores"]
                }
                resultado['restricciones'] = {
                    "A_ub": A_ub or [],
                    "b_ub": b_ub or [],
                    "A_eq": A_eq or [],
                    "b_eq": b_eq or []
                }
            
            print(f"Resultado final: {resultado}")
            return resultado

        else:
            error_msg = f"SciPy no pudo resolver el problema: {res.message}"
            print(f"Error: {error_msg}")
            return {
                "status": "error",
                "mensaje": error_msg
            }
            
    except Exception as e:
        error_msg = f"Error durante la optimización: {str(e)}"
        print(f"Excepción: {error_msg}")
        return {
            "status": "error",
            "mensaje": error_msg
        }

def test_ejemplo_problematico():
    """
    Función de prueba para el ejemplo que estaba fallando:
    Minimizar: 6x1+4x2+2x3
    Restricciones:
    - 6x1+2x2+6x3 ≥ 6
    - 6x1+4x2 = 12  
    - 2x1-2x2 ≤ 2
    """
    print("\n=== PROBANDO EJEMPLO PROBLEMÁTICO ===")
    
    funcion = "6x1+4x2+2x3"
    restricciones = [
        {"expr": "6x1+2x2+6x3", "op": "≥", "val": "6"},
        {"expr": "6x1+4x2", "op": "=", "val": "12"},
        {"expr": "2x1-2x2", "op": "≤", "val": "2"}
    ]
    tipo = "Minimizar"
    
    resultado = resolver_problema_lp(tipo, funcion, restricciones)
    print(f"Resultado final del test: {resultado}")
    return resultado

# Descomenta la siguiente línea para ejecutar el test
# test_ejemplo_problematico()
