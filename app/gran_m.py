import logging
from fractions import Fraction
import re

# Configuración básica de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

class MixedValue:
    """Clase para manejar valores de la forma a + bM"""
    def __init__(self, coefficient=0, M_coefficient=0):
        self.coefficient = Fraction(coefficient).limit_denominator()
        self.M_coefficient = Fraction(M_coefficient).limit_denominator()
    
    def __add__(self, other):
        if isinstance(other, MixedValue):
            return MixedValue(
                self.coefficient + other.coefficient,
                self.M_coefficient + other.M_coefficient
            )
        else:
            return MixedValue(
                self.coefficient + Fraction(other).limit_denominator(),
                self.M_coefficient
            )
    
    def __sub__(self, other):
        if isinstance(other, MixedValue):
            return MixedValue(
                self.coefficient - other.coefficient,
                self.M_coefficient - other.M_coefficient
            )
        else:
            return MixedValue(
                self.coefficient - Fraction(other).limit_denominator(),
                self.M_coefficient
            )
    
    def __mul__(self, other):
        if isinstance(other, MixedValue):
            return MixedValue(
                self.coefficient * other.coefficient,
                self.coefficient * other.M_coefficient + self.M_coefficient * other.coefficient
            )
        else:
            other_frac = Fraction(other).limit_denominator()
            return MixedValue(
                self.coefficient * other_frac,
                self.M_coefficient * other_frac
            )
    
    def __truediv__(self, other):
        if isinstance(other, MixedValue):
            if other.M_coefficient == 0:
                return MixedValue(
                    self.coefficient / other.coefficient,
                    self.M_coefficient / other.coefficient
                )
            else:
                raise ValueError("División por expresión con M no soportada")
        else:
            other_frac = Fraction(other).limit_denominator()
            return MixedValue(
                self.coefficient / other_frac,
                self.M_coefficient / other_frac
            )
    
    def __neg__(self):
        return MixedValue(-self.coefficient, -self.M_coefficient)
    
    def is_negative(self):
        if self.M_coefficient < 0:
            return True
        elif self.M_coefficient > 0:
            return False
        else:
            return self.coefficient < 0
    
    def to_float(self):
        """Convierte el valor a float (para resultados finales)"""
        return float(self.coefficient) + float(self.M_coefficient) * 1e12

def resolver_simplex_gran_m(data):
    """
    Resuelve un problema de programación lineal usando el método simplex con Gran M.
    Versión adaptada de la lógica de mop.py pero manteniendo estructura de salida.
    """
    tipo = data["tipoOperacion"]
    funcion = data["funcionObjetivo"]
    num_vars = data["numeroVariables"]
    restricciones = data["restricciones"]

    # Determinar si es maximización o minimización
    es_maximizacion = tipo.lower() in ["max", "maximizar"]
    es_minimizacion = not es_maximizacion

    # Parsear la función objetivo
    c = _parse_funcion(funcion, num_vars)
    
    # Parsear restricciones
    A, b, operadores = _procesar_restricciones(restricciones, num_vars)
    
    # Configurar el problema usando la lógica de mop.py
    matrix, all_var_names, basis_vars = setup_problem(
        c, A, b, operadores, es_minimizacion
    )
    
    # Eliminar variables artificiales de la fila Z
    matrix = eliminate_artificial_from_z(matrix, basis_vars, all_var_names, es_minimizacion)
    
    # Realizar iteraciones simplex
    iteraciones = []
    max_iterations = 50
    iter_count = 0
    
    while iter_count < max_iterations:
        # Crear tabla actual para la iteración
        tableau = []
        for i in range(len(matrix)):
            row = []
            for j in range(len(matrix[i])):
                if isinstance(matrix[i][j], MixedValue):
                    row.append(matrix[i][j].to_float())
                else:
                    row.append(float(matrix[i][j]))
            tableau.append(row)
        
        # Obtener encabezados
        encabezados = all_var_names + ["RHS"]
        
        # Variables básicas para mostrar
        vb_show = basis_vars[:]
        if len(vb_show) < len(tableau):
            vb_show += ["Z"] * (len(tableau) - len(vb_show))
        
        # Filas para mostrar
        filas_str = []
        for i in range(len(tableau)):
            fila = [vb_show[i]] + [round(val, 4) for val in tableau[i]]
            filas_str.append(fila)
        
        # Añadir iteración
        iteracion = {
            "encabezados": encabezados,
            "filas": filas_str,
            "variables_basicas": basis_vars[:],
            "detalles": None  # Podemos añadir detalles si es necesario
        }
        iteraciones.append(iteracion)
        
        # Encontrar pivote
        pivot_row, pivot_col = find_pivot(matrix, es_minimizacion)
        
        if pivot_row == -1:
            break  # Solución óptima encontrada
        
        # Realizar operación de pivote
        matrix, basis_vars = pivot_operation(matrix, pivot_row, pivot_col, basis_vars, all_var_names)
        iter_count += 1
    
    # Extraer solución
    solucion = [0.0] * num_vars
    
    for i, var in enumerate(basis_vars):
        if var.startswith('x'):
            try:
                var_num = int(var[1:]) - 1
                if 0 <= var_num < num_vars:
                    solucion[var_num] = matrix[i][-1].to_float()
            except:
                continue
    
    # Valor óptimo (Z)
    valor_z = matrix[-1][-1].to_float()
    if es_minimizacion:
        valor_z = -valor_z
    
    # Verificar factibilidad
    artificiales_positivas = False
    for i, var in enumerate(basis_vars):
        if var.startswith('a') and matrix[i][-1].to_float() > 1e-6:
            artificiales_positivas = True
            break
    
    # Construir respuesta final
    planteamiento = {
        "tipo": tipo,
        "funcion_objetivo": funcion,
        "restricciones": restricciones
    }
    
    modelo_estandar = _generar_modelo_estandar_display(
        A, b, operadores, c, num_vars, es_maximizacion
    )
    
    if artificiales_positivas:
        return {
            "planteamiento": planteamiento,
            "modelo_estandar": modelo_estandar,
            "optimo": None,
            "valores": None,
            "status": "infactible",
            "iteraciones": iteraciones,
            "mensaje": "El problema no tiene solución factible"
        }
    
    return {
        "planteamiento": planteamiento,
        "modelo_estandar": modelo_estandar,
        "optimo": valor_z,
        "valores": solucion,
        "status": "ok",
        "iteraciones": iteraciones
    }

def setup_problem(objective, constraints, rhs, constraint_types, minimize):
    """Configura el problema inicial usando fracciones (adaptado de mop.py)"""
    num_vars = len(objective)
    num_constraints = len(constraints)
    
    # Contar variables auxiliares
    slack_needed = sum(1 for ct in constraint_types if ct in ['<=', '<'])
    surplus_needed = sum(1 for ct in constraint_types if ct in ['>=', '>'])
    artificial_needed = sum(1 for ct in constraint_types if ct in ['>=', '>', '='])
    
    total_aux_vars = slack_needed + surplus_needed + artificial_needed
    total_vars = num_vars + total_aux_vars
    
    # Nombres de variables
    original_vars = [f"x{i+1}" for i in range(num_vars)]
    slack_vars = [f"s{i+1}" for i in range(slack_needed)]
    surplus_vars = [f"H{i+1}" for i in range(surplus_needed)]
    artificial_vars = [f"a{i+1}" for i in range(artificial_needed)]
    all_var_names = original_vars + slack_vars + surplus_vars + artificial_vars
    
    # Matriz extendida con MixedValue
    extended_matrix = []
    basis_vars = []
    
    # Contadores
    slack_count = 0
    surplus_count = 0
    artificial_count = 0
    
    # Procesar restricciones
    for i, (constraint, constraint_type, b_val) in enumerate(zip(constraints, constraint_types, rhs)):
        row = [MixedValue(0, 0) for _ in range(total_vars + 1)]
        
        # Variables originales
        for j in range(num_vars):
            row[j] = MixedValue(Fraction(constraint[j]).limit_denominator(), 0)
        
        # RHS
        row[-1] = MixedValue(Fraction(b_val).limit_denominator(), 0)
        
        if constraint_type in ['<=', '<']:
            slack_pos = num_vars + slack_count
            row[slack_pos] = MixedValue(1, 0)
            basis_vars.append(f"s{slack_count+1}")
            slack_count += 1
            
        elif constraint_type in ['>=', '>']:
            surplus_pos = num_vars + slack_needed + surplus_count
            artificial_pos = num_vars + slack_needed + surplus_needed + artificial_count
            
            row[surplus_pos] = MixedValue(-1, 0)
            row[artificial_pos] = MixedValue(1, 0)
            basis_vars.append(f"a{artificial_count+1}")
            
            surplus_count += 1
            artificial_count += 1
            
        elif constraint_type == '=':
            artificial_pos = num_vars + slack_needed + surplus_needed + artificial_count
            row[artificial_pos] = MixedValue(1, 0)
            basis_vars.append(f"a{artificial_count+1}")
            artificial_count += 1
        
        extended_matrix.append(row)
    
    # Fila de función objetivo
    z_row = [MixedValue(0, 0) for _ in range(total_vars + 1)]
    
    # Coeficientes de variables originales
    for i, coef in enumerate(objective):
        coef_frac = Fraction(coef).limit_denominator()
        z_row[i] = MixedValue(coef_frac, 0)
    
    # Penalización para variables artificiales
    artificial_start_idx = num_vars + slack_needed + surplus_needed
    for i in range(artificial_needed):
        # +M para minimización, -M para maximización
        M_coef = 1 if minimize else -1
        z_row[artificial_start_idx + i] = MixedValue(0, M_coef)
    
    extended_matrix.append(z_row)
    
    return extended_matrix, all_var_names, basis_vars

def eliminate_artificial_from_z(matrix, basis_vars, all_var_names, minimize):
    """Elimina variables artificiales de la fila Z (adaptado de mop.py)"""
    artificial_indices = [i for i, var in enumerate(all_var_names) if var.startswith('a')]
    
    for art_idx in artificial_indices:
        if matrix[-1][art_idx].M_coefficient != 0 or matrix[-1][art_idx].coefficient != 0:
            # Encontrar fila donde está la variable artificial
            for i, basis_var in enumerate(basis_vars):
                if basis_var == all_var_names[art_idx] and i < len(matrix) - 1:
                    multiplier = matrix[-1][art_idx]
                    for j in range(len(matrix[0])):
                        matrix[-1][j] = matrix[-1][j] - multiplier * matrix[i][j]
                    break
    return matrix

def find_pivot(matrix, minimize):
    """Encuentra el elemento pivote (adaptado de mop.py)"""
    z_row = matrix[-1][:-1]
    
    # Para minimización: buscar coeficiente positivo más grande en Z
    if minimize:
        most_positive_idx = -1
        most_positive_val = None
        
        for i, val in enumerate(z_row):
            if val.M_coefficient > 0 or (val.M_coefficient == 0 and val.coefficient > 0):
                if most_positive_val is None or val.M_coefficient > most_positive_val.M_coefficient or \
                   (val.M_coefficient == most_positive_val.M_coefficient and val.coefficient > most_positive_val.coefficient):
                    most_positive_val = val
                    most_positive_idx = i
        
        if most_positive_idx == -1:
            return -1, -1  # Óptimo encontrado
        pivot_col = most_positive_idx
    
    # Para maximización: buscar coeficiente negativo más pequeño en Z
    else:
        most_negative_idx = -1
        most_negative_val = None
        
        for i, val in enumerate(z_row):
            if val.is_negative():
                if most_negative_val is None or val.M_coefficient < most_negative_val.M_coefficient or \
                   (val.M_coefficient == most_negative_val.M_coefficient and val.coefficient < most_negative_val.coefficient):
                    most_negative_val = val
                    most_negative_idx = i
        
        if most_negative_idx == -1:
            return -1, -1  # Óptimo encontrado
        pivot_col = most_negative_idx
    
    # Prueba de la razón
    ratios = []
    for i in range(len(matrix) - 1):
        if matrix[i][pivot_col].coefficient > 0 or matrix[i][pivot_col].M_coefficient > 0:
            rhs = matrix[i][-1]
            divisor = matrix[i][pivot_col]
            
            # Solo consideramos divisores positivos
            if divisor.M_coefficient > 0 or (divisor.M_coefficient == 0 and divisor.coefficient > 0):
                # Calcular razón como valor numérico
                ratio_val = rhs.to_float() / divisor.to_float()
                ratios.append((ratio_val, i))
            else:
                ratios.append((float('inf'), i))
        else:
            ratios.append((float('inf'), i))
    
    valid_ratios = [(r, i) for r, i in ratios if r != float('inf')]
    if not valid_ratios:
        return -1, -1  # No acotado
    
    min_ratio, pivot_row = min(valid_ratios, key=lambda x: x[0])
    return pivot_row, pivot_col

def pivot_operation(matrix, pivot_row, pivot_col, basis_vars, all_var_names):
    """Realiza operación de pivoteo (adaptado de mop.py)"""
    pivot_element = matrix[pivot_row][pivot_col]
    
    # Normalizar fila pivote
    for j in range(len(matrix[0])):
        matrix[pivot_row][j] = matrix[pivot_row][j] / pivot_element
    
    # Actualizar otras filas
    for i in range(len(matrix)):
        if i != pivot_row:
            factor = matrix[i][pivot_col]
            for j in range(len(matrix[0])):
                matrix[i][j] = matrix[i][j] - factor * matrix[pivot_row][j]
    
    # Actualizar base - CORRECCIÓN: Usar nombres reales de variables
    if pivot_row < len(basis_vars):
        basis_vars[pivot_row] = all_var_names[pivot_col]
    
    return matrix, basis_vars

def _parse_funcion(expr, num_vars):
    """
    Parsea una expresión lineal
    """
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

def _procesar_restricciones(restricciones, num_vars):
    """Procesa las restricciones"""
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

def _generar_modelo_estandar_display(A, b, operadores, c, num_vars, es_maximizacion):
    """Genera la representación del modelo estándar"""
    # Contar variables adicionales
    num_holgura = sum(1 for op in operadores if op == "≤")
    num_exceso = sum(1 for op in operadores if op == "≥")
    num_artificiales = sum(1 for op in operadores if op in ["≥", "="])
    
    # Función objetivo
    tipo_obj = "Maximizar" if es_maximizacion else "Minimizar"
    partes_fo = []
    
    # Variables originales
    for i, coef in enumerate(c):
        if coef != 0:
            sign = "+" if coef > 0 and i > 0 else ""
            if i > 0 and coef < 0:
                sign = "-"
            coef_abs = abs(coef)
            partes_fo.append(f"{sign}{coef_abs}x{i+1}")
    
    # Variables de holgura
    for i in range(num_holgura):
        partes_fo.append(f"+0s{i+1}")
    
    # Variables de exceso
    for i in range(num_exceso):
        partes_fo.append(f"+0H{i+1}")
    
    # Variables artificiales
    for i in range(num_artificiales):
        if es_maximizacion:
            partes_fo.append(f"-Ma{i+1}")
        else:
            partes_fo.append(f"+Ma{i+1}")
    
    funcion_objetivo = f"{tipo_obj} Z = " + " ".join(partes_fo).replace("+ -", "-")
    
    # Restricciones
    restricciones = []
    slack_count = 0
    excess_count = 0
    artificial_count = 0
    
    for i, (fila, valor_b, op) in enumerate(zip(A, b, operadores)):
        partes = []
        
        # Variables originales
        for j, coef in enumerate(fila):
            if coef != 0:
                sign = "+" if coef > 0 and j > 0 else ""
                if j > 0 and coef < 0:
                    sign = "-"
                coef_abs = abs(coef)
                partes.append(f"{sign}{coef_abs}x{j+1}")
        
        # Variables auxiliares
        if op == "≤":
            slack_count += 1
            partes.append(f"+s{slack_count}")
        elif op == "≥":
            excess_count += 1
            artificial_count += 1
            partes.append(f"-H{excess_count}")
            partes.append(f"+a{artificial_count}")
        elif op == "=":
            artificial_count += 1
            partes.append(f"+a{artificial_count}")
        
        restriccion_str = " ".join(partes) + f" = {valor_b}"
        restricciones.append(restriccion_str.replace("+ -", "-"))
    
    # Variables no negativas
    variables = [f"x{i+1} ≥ 0" for i in range(num_vars)]
    variables += [f"s{i+1} ≥ 0" for i in range(num_holgura)]
    variables += [f"H{i+1} ≥ 0" for i in range(num_exceso)]
    variables += [f"a{i+1} ≥ 0" for i in range(num_artificiales)]
    
    return {
        "funcion_objetivo": funcion_objetivo,
        "restricciones": restricciones,
        "variables": variables
    }