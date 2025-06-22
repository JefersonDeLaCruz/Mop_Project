from typing import List, Tuple, Dict
import pandas as pd
import numpy as np
from fractions import Fraction

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
    
    def __str__(self):
        if self.coefficient == 0 and self.M_coefficient == 0:
            return "0"
        elif self.M_coefficient == 0:
            return str(self.coefficient)
        elif self.coefficient == 0:
            if self.M_coefficient == 1:
                return "M"
            elif self.M_coefficient == -1:
                return "-M"
            else:
                return f"{self.M_coefficient}M"
        else:
            m_part = ""
            if self.M_coefficient == 1:
                m_part = "M"
            elif self.M_coefficient == -1:
                m_part = "-M"
            elif self.M_coefficient != 0:
                m_part = f"{self.M_coefficient}M"
            
            if m_part:
                if self.M_coefficient > 0:
                    return f"{self.coefficient} + {m_part}"
                else:
                    return f"{self.coefficient} {m_part}"
            else:
                return str(self.coefficient)

class GranMSimplexExtended:
    def __init__(self):
        self.M = "M"
        self.iteration = 0
        self.html_output = ""
        self.is_minimization = True
        
    def fraction_to_html(self, frac):
        """Convierte una fracción a HTML legible"""
        if isinstance(frac, str):
            return frac
        
        if isinstance(frac, MixedValue):
            return self.mixed_value_to_html(frac)
        
        if isinstance(frac, (int, float)):
            frac = Fraction(frac).limit_denominator()
        
        if frac.denominator == 1:
            return str(frac.numerator)
        else:
            return f"<sup>{frac.numerator}</sup>&frasl;<sub>{frac.denominator}</sub>"
    
    def mixed_value_to_html(self, value, is_z_row=False):
        """Convierte MixedValue a HTML"""
        if value.coefficient == 0 and value.M_coefficient == 0:
            return "0"
        elif value.M_coefficient == 0:
            coef_to_show = -value.coefficient if is_z_row else value.coefficient
            return self.fraction_to_html(coef_to_show)
        elif value.coefficient == 0:
            m_coef_to_show = -value.M_coefficient if is_z_row else value.M_coefficient
            if m_coef_to_show == 1:
                return "M"
            elif m_coef_to_show == -1:
                return "-M"
            else:
                return f"{self.fraction_to_html(m_coef_to_show)}M"
        else:
            coef_to_show = -value.coefficient if is_z_row else value.coefficient
            m_coef_to_show = -value.M_coefficient if is_z_row else value.M_coefficient
            
            coef_str = self.fraction_to_html(coef_to_show)
            if m_coef_to_show == 1:
                m_str = "M"
            elif m_coef_to_show == -1:
                m_str = "-M"
            else:
                m_str = f"{self.fraction_to_html(m_coef_to_show)}M"
            
            if m_coef_to_show > 0:
                return f"{coef_str} + {m_str}"
            else:
                return f"{coef_str} {m_str}"

    def generate_extended_model(self, objective: List[float], constraints: List[List[float]], 
                              constraint_types: List[str], minimize: bool = True) -> str:
        """Genera el modelo extendido con variables auxiliares"""
        num_vars = len(objective)
        
        # Contadores para variables auxiliares
        slack_count = 0
        surplus_count = 0
        artificial_count = 0
        
        # Listas para almacenar información de variables
        slack_vars = []
        surplus_vars = []
        artificial_vars = []
        
        html = '<div class="extended-model">'
        html += '<h2>Modelo Extendido con Variables de Holgura y Artificiales</h2>'
        
        # Analizar cada restricción
        html += '<h3>Análisis de Restricciones:</h3><ul>'
        for i, (constraint, constraint_type) in enumerate(zip(constraints, constraint_types)):
            html += f'<li><strong>Restricción {i+1}:</strong> '
            
            # Mostrar restricción original
            constraint_str = ""
            for j, coef in enumerate(constraint[:-1]):
                frac = Fraction(coef).limit_denominator()
                if j > 0 and frac >= 0:
                    constraint_str += " + "
                elif frac < 0:
                    constraint_str += " - " if j > 0 else "-"
                    frac = abs(frac)
                
                if frac.denominator == 1:
                    constraint_str += f"{frac.numerator}x<sub>{j+1}</sub>"
                else:
                    constraint_str += f"({frac.numerator}/{frac.denominator})x<sub>{j+1}</sub>"
            
            rhs_frac = Fraction(constraint[-1]).limit_denominator()
            if rhs_frac.denominator == 1:
                constraint_str += f" {constraint_type} {rhs_frac.numerator}"
            else:
                constraint_str += f" {constraint_type} {rhs_frac.numerator}/{rhs_frac.denominator}"
            
            html += constraint_str
            
            # Explicar qué variables se agregan
            if constraint_type in ['<=', '<']:
                slack_count += 1
                slack_var = f"s{slack_count}"
                slack_vars.append(slack_var)
                html += f'<br>&nbsp;&nbsp;&nbsp;&nbsp;→ Se agrega variable de holgura <strong>{slack_var}</strong> ≥ 0'
                
            elif constraint_type in ['>=', '>']:
                surplus_count += 1
                artificial_count += 1
                surplus_var = f"H{surplus_count}"
                artificial_var = f"a{artificial_count}"
                surplus_vars.append(surplus_var)
                artificial_vars.append(artificial_var)
                html += f'<br>&nbsp;&nbsp;&nbsp;&nbsp;→ Se agrega variable de exceso <strong>{surplus_var}</strong> ≥ 0'
                html += f'<br>&nbsp;&nbsp;&nbsp;&nbsp;→ Se agrega variable artificial <strong>{artificial_var}</strong> ≥ 0'
                
            elif constraint_type == '=':
                artificial_count += 1
                artificial_var = f"a{artificial_count}"
                artificial_vars.append(artificial_var)
                html += f'<br>&nbsp;&nbsp;&nbsp;&nbsp;→ Se agrega variable artificial <strong>{artificial_var}</strong> ≥ 0'
            
            html += '</li>'
        
        html += '</ul>'
        
        # Modelo extendido completo
        html += '<h3>Modelo Extendido Completo:</h3>'
        
        # Función objetivo extendida
        obj_str = "Minimizar " if minimize else "Maximizar "
        obj_str += "Z = "
        
        # Variables originales
        for i, coef in enumerate(objective):
            frac = Fraction(coef).limit_denominator()
            if i > 0 and frac >= 0:
                obj_str += " + "
            elif frac < 0:
                obj_str += " - " if i > 0 else "-"
                frac = abs(frac)
            
            if frac.denominator == 1:
                obj_str += f"{frac.numerator}x<sub>{i+1}</sub>"
            else:
                obj_str += f"({frac.numerator}/{frac.denominator})x<sub>{i+1}</sub>"
        
        # Variables de holgura (coeficiente 0)
        for slack_var in slack_vars:
            obj_str += f" + 0{slack_var}"
        
        # Variables de exceso (coeficiente 0)
        for surplus_var in surplus_vars:
            obj_str += f" + 0{surplus_var}"
        
        # Variables artificiales (coeficiente M)
        for artificial_var in artificial_vars:
            if minimize:
                obj_str += f" + M{artificial_var}"
            else:
                obj_str += f" - M{artificial_var}"
        
        html += f'<p><strong>{obj_str}</strong></p>'
        
        # Restricciones extendidas
        html += '<p><strong>Sujeto a:</strong></p><ul>'
        
        slack_idx = 0
        surplus_idx = 0
        artificial_idx = 0
        
        for i, (constraint, constraint_type) in enumerate(zip(constraints, constraint_types)):
            constraint_str = ""
            
            # Variables originales
            for j, coef in enumerate(constraint[:-1]):
                frac = Fraction(coef).limit_denominator()
                if j > 0 and frac >= 0:
                    constraint_str += " + "
                elif frac < 0:
                    constraint_str += " - " if j > 0 else "-"
                    frac = abs(frac)
                
                if frac.denominator == 1:
                    constraint_str += f"{frac.numerator}x<sub>{j+1}</sub>"
                else:
                    constraint_str += f"({frac.numerator}/{frac.denominator})x<sub>{j+1}</sub>"
            
            # Variables auxiliares
            if constraint_type in ['<=', '<']:
                slack_idx += 1
                constraint_str += f" + s<sub>{slack_idx}</sub>"
                
            elif constraint_type in ['>=', '>']:
                surplus_idx += 1
                artificial_idx += 1
                constraint_str += f" - H<sub>{surplus_idx}</sub> + a<sub>{artificial_idx}</sub>"
                
            elif constraint_type == '=':
                artificial_idx += 1
                constraint_str += f" + a<sub>{artificial_idx}</sub>"
            
            # RHS
            rhs_frac = Fraction(constraint[-1]).limit_denominator()
            if rhs_frac.denominator == 1:
                constraint_str += f" = {rhs_frac.numerator}"
            else:
                constraint_str += f" = {rhs_frac.numerator}/{rhs_frac.denominator}"
            
            html += f'<li>{constraint_str}</li>'
        
        # Restricciones de no negatividad
        all_vars = [f"x<sub>{i+1}</sub>" for i in range(num_vars)]
        all_vars.extend([f"s<sub>{i+1}</sub>" for i in range(len(slack_vars))])
        all_vars.extend([f"H<sub>{i+1}</sub>" for i in range(len(surplus_vars))])
        all_vars.extend([f"a<sub>{i+1}</sub>" for i in range(len(artificial_vars))])
        
        html += f'<li>{", ".join(all_vars)} ≥ 0</li>'
        html += '</ul></div>'
        
        return html

    def generate_initial_table_steps(self, objective: List[float], constraints: List[List[float]], 
                                   constraint_types: List[str], minimize: bool = True) -> str:
        """Genera los pasos detallados para construir la tabla inicial"""
        html = '<div class="initial-steps">'
        html += '<h2>Pasos para Construir la Tabla Inicial (Iteración 0)</h2>'
        
        num_vars = len(objective)
        num_constraints = len(constraints)
        
        # Paso 1: Identificar variables
        html += '<h3>Paso 1: Identificación de Variables</h3>'
        html += f'<p>Variables originales: x<sub>1</sub>, x<sub>2</sub>, ..., x<sub>{num_vars}</sub></p>'
        
        slack_count = sum(1 for ct in constraint_types if ct in ['<=', '<'])
        surplus_count = sum(1 for ct in constraint_types if ct in ['>=', '>'])
        artificial_count = sum(1 for ct in constraint_types if ct in ['>=', '>', '='])
        
        if slack_count > 0:
            html += f'<p>Variables de holgura: s<sub>1</sub>, s<sub>2</sub>, ..., s<sub>{slack_count}</sub></p>'
        if surplus_count > 0:
            html += f'<p>Variables de exceso: H<sub>1</sub>, H<sub>2</sub>, ..., H<sub>{surplus_count}</sub></p>'
        if artificial_count > 0:
            html += f'<p>Variables artificiales: a<sub>1</sub>, a<sub>2</sub>, ..., a<sub>{artificial_count}</sub></p>'
        
        total_vars = num_vars + slack_count + surplus_count + artificial_count
        html += f'<p><strong>Total de variables: {total_vars}</strong></p>'
        
        # Paso 2: Matriz de coeficientes
        html += '<h3>Paso 2: Construcción de la Matriz de Coeficientes</h3>'
        html += '<p>La matriz se construye columna por columna:</p><ul>'
        
        # Variables originales
        html += '<li><strong>Variables originales (x<sub>1</sub>, x<sub>2</sub>, ...):</strong> Se copian directamente los coeficientes de las restricciones</li>'
        
        # Variables de holgura
        if slack_count > 0:
            html += '<li><strong>Variables de holgura (s<sub>i</sub>):</strong> Coeficiente +1 en su restricción correspondiente, 0 en las demás</li>'
        
        # Variables de exceso
        if surplus_count > 0:
            html += '<li><strong>Variables de exceso (H<sub>i</sub>):</strong> Coeficiente -1 en su restricción correspondiente, 0 en las demás</li>'
        
        # Variables artificiales
        if artificial_count > 0:
            html += '<li><strong>Variables artificiales (a<sub>i</sub>):</strong> Coeficiente +1 en su restricción correspondiente, 0 en las demás</li>'
        
        html += '</ul>'
        
        # Paso 3: Base inicial
        html += '<h3>Paso 3: Identificación de la Base Inicial</h3>'
        html += '<p>La base inicial está formada por las variables que tienen coeficiente 1 en exactamente una restricción y 0 en las demás:</p><ul>'
        
        basis_vars = []
        slack_idx = 0
        surplus_idx = 0
        artificial_idx = 0
        
        for i, constraint_type in enumerate(constraint_types):
            if constraint_type in ['<=', '<']:
                slack_idx += 1
                basis_vars.append(f"s<sub>{slack_idx}</sub>")
                html += f'<li>Restricción {i+1}: Variable básica s<sub>{slack_idx}</sub></li>'
            elif constraint_type in ['>=', '>']:
                artificial_idx += 1
                basis_vars.append(f"a<sub>{artificial_idx}</sub>")
                html += f'<li>Restricción {i+1}: Variable básica a<sub>{artificial_idx}</sub></li>'
            elif constraint_type == '=':
                artificial_idx += 1
                basis_vars.append(f"a<sub>{artificial_idx}</sub>")
                html += f'<li>Restricción {i+1}: Variable básica a<sub>{artificial_idx}</sub></li>'
        
        html += '</ul>'
        html += f'<p><strong>Base inicial: {{{", ".join(basis_vars)}}}</strong></p>'
        
        # Paso 4: Fila Z
        html += '<h3>Paso 4: Construcción de la Fila Z</h3>'
        html += '<p>La fila Z se construye de la siguiente manera:</p><ol>'
        html += '<li><strong>Variables originales:</strong> Se copian los coeficientes de la función objetivo</li>'
        html += '<li><strong>Variables de holgura y exceso:</strong> Coeficiente 0</li>'
        html += '<li><strong>Variables artificiales:</strong> Coeficiente M (para minimización) o -M (para maximización)</li>'
        html += '<li><strong>Término independiente:</strong> Inicialmente 0</li>'
        html += '</ol>'
        
        # Paso 5: Eliminación de variables artificiales
        if artificial_count > 0:
            html += '<h3>Paso 5: Eliminación de Variables Artificiales de la Fila Z</h3>'
            html += '<p>Como las variables artificiales están en la base inicial con coeficiente M ≠ 0 en la fila Z, '
            html += 'debemos eliminarlas usando operaciones elementales:</p>'
            html += '<p><strong>Para cada variable artificial a<sub>i</sub> en la base:</strong></p><ol>'
            html += '<li>Identificar la fila donde a<sub>i</sub> es variable básica (coeficiente = 1)</li>'
            html += '<li>Multiplicar esa fila por -M (o +M según el caso)</li>'
            html += '<li>Sumar el resultado a la fila Z</li>'
            html += '</ol>'
            html += '<p>Esto garantiza que las variables artificiales tengan coeficiente 0 en la fila Z.</p>'
        
        html += '</div>'
        return html

    def setup_problem(self, objective: List[float], constraints: List[List[float]], 
                     constraint_types: List[str], minimize: bool = True) -> Tuple[List[List], List[str], List[str]]:
        """Configura el problema inicial usando fracciones"""
        self.is_minimization = minimize
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
        slack_vars = []
        surplus_vars = []
        artificial_vars = []
        
        # Contadores
        slack_count = 0
        surplus_count = 0
        artificial_count = 0
        
        # Matriz extendida con MixedValue
        extended_matrix = []
        basis_vars = []
        
        # Procesar restricciones
        for i, (constraint, constraint_type) in enumerate(zip(constraints, constraint_types)):
            row = [MixedValue(0, 0) for _ in range(total_vars + 1)]
            
            # Variables originales
            for j in range(num_vars):
                row[j] = MixedValue(Fraction(constraint[j]).limit_denominator(), 0)
            
            # RHS
            row[-1] = MixedValue(Fraction(constraint[-1]).limit_denominator(), 0)
            
            if constraint_type in ['<=', '<']:
                slack_count += 1
                slack_var = f"s{slack_count}"
                slack_vars.append(slack_var)
                slack_position = num_vars + slack_count - 1
                row[slack_position] = MixedValue(1, 0)
                basis_vars.append(slack_var)
                
            elif constraint_type in ['>=', '>']:
                surplus_count += 1
                artificial_count += 1
                surplus_var = f"H{surplus_count}"
                artificial_var = f"a{artificial_count}"
                surplus_vars.append(surplus_var)
                artificial_vars.append(artificial_var)
                
                surplus_position = num_vars + slack_needed + surplus_count - 1
                artificial_position = num_vars + slack_needed + surplus_needed + artificial_count - 1
                
                row[surplus_position] = MixedValue(-1, 0)
                row[artificial_position] = MixedValue(1, 0)
                basis_vars.append(artificial_var)
                
            elif constraint_type == '=':
                artificial_count += 1
                artificial_var = f"a{artificial_count}"
                artificial_vars.append(artificial_var)
                
                artificial_position = num_vars + slack_needed + surplus_needed + artificial_count - 1
                row[artificial_position] = MixedValue(1, 0)
                basis_vars.append(artificial_var)
            
            extended_matrix.append(row)
        
        # Fila de función objetivo
        z_row = [MixedValue(0, 0) for _ in range(total_vars + 1)]
        
        # Coeficientes de variables originales
        for i, coef in enumerate(objective):
            coef_frac = Fraction(coef).limit_denominator()
            z_row[i] = MixedValue(coef_frac, 0)
        
        # Penalización para variables artificiales
        artificial_start_idx = num_vars + slack_needed + surplus_needed
        for i in range(len(artificial_vars)):
            z_row[artificial_start_idx + i] = MixedValue(0, 1)  # +M
        
        extended_matrix.append(z_row)
        
        # Nombres de variables
        all_var_names = original_vars + slack_vars + surplus_vars + artificial_vars + ["b(j)"]
        
        return extended_matrix, all_var_names, basis_vars

    def eliminate_artificial_from_z(self, matrix: List[List], basis_vars: List[str], all_var_names: List[str]) -> List[List]:
        """Elimina variables artificiales de la fila Z"""
        artificial_indices = [i for i, var in enumerate(all_var_names[:-1]) if var.startswith('a')]
        
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

    def find_pivot(self, matrix: List[List]) -> Tuple[int, int]:
        """Encuentra el elemento pivote"""
        z_row = matrix[-1][:-1]
        
        # Encontrar el más negativo
        most_negative_idx = -1
        most_negative_val = None
        
        for i, val in enumerate(z_row):
            if val.is_negative():
                if most_negative_val is None or self.is_more_negative(val, most_negative_val):
                    most_negative_val = val
                    most_negative_idx = i
        
        if most_negative_idx == -1:
            return -1, -1  # Óptimo encontrado
        
        pivot_col = most_negative_idx
        
        # Prueba de la razón
        ratios = []
        for i in range(len(matrix) - 1):
            if matrix[i][pivot_col].coefficient > 0 or matrix[i][pivot_col].M_coefficient > 0:
                # Calcular razón RHS / elemento_columna
                rhs = matrix[i][-1]
                divisor = matrix[i][pivot_col]
                
                # Solo consideramos casos donde el divisor es positivo y sin M
                if divisor.M_coefficient == 0 and divisor.coefficient > 0:
                    if rhs.M_coefficient == 0:  # RHS sin M
                        ratio = rhs.coefficient / divisor.coefficient
                        ratios.append((ratio, i))
                    else:
                        ratios.append((float('inf'), i))
                else:
                    ratios.append((float('inf'), i))
            else:
                ratios.append((float('inf'), i))
        
        valid_ratios = [(r, i) for r, i in ratios if r != float('inf')]
        if not valid_ratios:
            return -1, -1  # No acotado
        
        min_ratio, pivot_row = min(valid_ratios)
        return pivot_row, pivot_col

    def is_more_negative(self, val1, val2):
        """Compara si val1 es más negativo que val2"""
        if val1.M_coefficient < val2.M_coefficient:
            return True
        elif val1.M_coefficient > val2.M_coefficient:
            return False
        else:
            return val1.coefficient < val2.coefficient

    def pivot_operation(self, matrix: List[List], pivot_row: int, pivot_col: int, 
                       basis_vars: List[str], all_var_names: List[str]) -> List[List]:
        """Realiza operación de pivoteo con fracciones"""
        pivot_element = matrix[pivot_row][pivot_col]
        
        # HTML para pivoteo
        self.html_output += f"<p>Variable que entra: <strong>{all_var_names[pivot_col]}</strong> | "
        self.html_output += f"Variable que sale: <strong>{basis_vars[pivot_row]}</strong></p>"
        self.html_output += f"<p>Elemento pivote: <strong>{self.mixed_value_to_html(pivot_element)}</strong></p>"
        
        # Normalizar fila pivote
        self.html_output += f"<h3>Normalización de la fila pivote F{pivot_row+1}:</h3><ul>"
        for j in range(len(matrix[0])):
            old_val = matrix[pivot_row][j]
            matrix[pivot_row][j] = matrix[pivot_row][j] / pivot_element
            var_name = all_var_names[j] if j < len(all_var_names) else 'RHS'
            self.html_output += f"<li>{var_name}: {self.mixed_value_to_html(old_val)} ÷ {self.mixed_value_to_html(pivot_element)} = {self.mixed_value_to_html(matrix[pivot_row][j])}</li>"
        self.html_output += "</ul>"
        
        # Actualizar otras filas
        self.html_output += f"<h3>Actualización de las otras filas:</h3>"
        for i in range(len(matrix)):
            if i != pivot_row:
                factor = matrix[i][pivot_col]
                if factor.coefficient != 0 or factor.M_coefficient != 0:
                    self.html_output += f"<h4>F{i+1} = F{i+1} - ({self.mixed_value_to_html(factor)}) × F{pivot_row+1}</h4><ul>"
                    for j in range(len(matrix[0])):
                        old_val = matrix[i][j]
                        pivot_val = matrix[pivot_row][j]
                        matrix[i][j] = matrix[i][j] - factor * pivot_val
                        var_name = all_var_names[j] if j < len(all_var_names) else 'RHS'
                        is_z_row = (i == len(matrix) - 1)
                        self.html_output += f"<li>{var_name}: {self.mixed_value_to_html(old_val, is_z_row)} - ({self.mixed_value_to_html(factor)} × {self.mixed_value_to_html(pivot_val)}) = {self.mixed_value_to_html(matrix[i][j], is_z_row)}</li>"
                    self.html_output += "</ul>"
        
        # Actualizar base
        basis_vars[pivot_row] = all_var_names[pivot_col]
        
        return matrix

    def create_table_html(self, matrix: List[List], all_var_names: List[str], 
                         basis_vars: List[str], pivot_row: int = -1, pivot_col: int = -1) -> str:
        """Crea tabla HTML con fracciones"""
        html = f'<div class="iteration-title">Iteración {self.iteration}</div>'
        html += '<table><thead><tr><th>Base</th>'
        
        for var_name in all_var_names:
            html += f'<th>{var_name}</th>'
        html += '</tr></thead><tbody>'
        
        for i in range(len(matrix)):
            html += '<tr>'
            if i < len(basis_vars):
                html += f'<td>{basis_vars[i]}</td>'
            else:
                html += '<td>Z</td>'
            
            is_z_row = (i == len(matrix) - 1)
            
            for j in range(len(matrix[0])):
                css_class = ""
                if i == pivot_row and j == pivot_col:
                    css_class = ' class="pivot"'
                elif i == pivot_row or j == pivot_col:
                    css_class = ' class="pivot-highlight"'
                
                html += f'<td{css_class}>{self.mixed_value_to_html(matrix[i][j], is_z_row)}</td>'
            html += '</tr>'
        
        html += '</tbody></table>'
        return html

    def solve(self, objective: List[float], constraints: List[List[float]], 
              constraint_types: List[str], minimize: bool = True) -> str:
        """Resuelve usando fracciones exactas con modelo extendido y pasos detallados"""
        
        # HTML inicial
        self.html_output = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }
                h1, h2, h3 { color: #003366; }
                h1 { border-bottom: 3px solid #003366; padding-bottom: 10px; }
                h2 { border-bottom: 2px solid #666; padding-bottom: 5px; margin-top: 30px; }
                h3 { color: #0066cc; margin-top: 20px; }
                table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
                th, td { border: 1px solid #999; padding: 8px; text-align: center; }
                th { background-color: #f2f2f2; font-weight: bold; }
                .pivot { background-color: #ffcccc; font-weight: bold; }
                .pivot-highlight { background-color: #ffffcc; }
                .iteration-title { background-color: #003366; color: white; padding: 8px; margin-top: 20px; font-weight: bold; }
                .model { background-color: #f9f9f9; padding: 15px; border-left: 4px solid #003366; margin: 20px 0; }
                .extended-model { background-color: #e6f3ff; padding: 15px; border-left: 4px solid #0066cc; margin: 20px 0; }
                .initial-steps { background-color: #fff2e6; padding: 15px; border-left: 4px solid #ff9900; margin: 20px 0; }
                ul, ol { text-align: left; }
                li { margin-bottom: 5px; }
                sup { font-size: 0.8em; }
                sub { font-size: 0.8em; }
                .formula { background-color: #f0f0f0; padding: 10px; margin: 10px 0; border-radius: 5px; }
            </style>
        </head>
        <body>
            <h1>Método de la Gran M - Análisis Completo con Variables Auxiliares</h1>
        """
        
        # Modelo original
        self.html_output += '<div class="model">'
        self.html_output += '<h2>Modelo Matemático Original</h2>'
        
        obj_str = "Minimizar " if minimize else "Maximizar "
        obj_str += "Z = "
        for i, coef in enumerate(objective):
            frac = Fraction(coef).limit_denominator()
            if i > 0 and frac >= 0:
                obj_str += " + "
            elif frac < 0:
                obj_str += " - " if i > 0 else "-"
                frac = abs(frac)
            
            if frac.denominator == 1:
                obj_str += f"{frac.numerator}x<sub>{i+1}</sub>"
            else:
                obj_str += f"({frac.numerator}/{frac.denominator})x<sub>{i+1}</sub>"
        
        self.html_output += f'<p><strong>{obj_str}</strong></p>'
        
        # Restricciones
        self.html_output += '<p><strong>Sujeto a:</strong></p><ul>'
        for i, (constraint, constraint_type) in enumerate(zip(constraints, constraint_types)):
            constraint_str = ""
            for j, coef in enumerate(constraint[:-1]):
                frac = Fraction(coef).limit_denominator()
                if j > 0 and frac >= 0:
                    constraint_str += " + "
                elif frac < 0:
                    constraint_str += " - " if j > 0 else "-"
                    frac = abs(frac)
                
                if frac.denominator == 1:
                    constraint_str += f"{frac.numerator}x<sub>{j+1}</sub>"
                else:
                    constraint_str += f"({frac.numerator}/{frac.denominator})x<sub>{j+1}</sub>"
            
            rhs_frac = Fraction(constraint[-1]).limit_denominator()
            if rhs_frac.denominator == 1:
                constraint_str += f" {constraint_type} {rhs_frac.numerator}"
            else:
                constraint_str += f" {constraint_type} {rhs_frac.numerator}/{rhs_frac.denominator}"
            
            self.html_output += f'<li>{constraint_str}</li>'
        
        var_list = ", ".join([f"x<sub>{i+1}</sub>" for i in range(len(objective))])
        self.html_output += f'<li>{var_list} ≥ 0</li>'
        self.html_output += '</ul></div>'
        
        # Modelo extendido
        self.html_output += self.generate_extended_model(objective, constraints, constraint_types, minimize)
        
        # Pasos para tabla inicial
        self.html_output += self.generate_initial_table_steps(objective, constraints, constraint_types, minimize)
        
        # Configurar y resolver
        matrix, all_var_names, basis_vars = self.setup_problem(objective, constraints, constraint_types, minimize)
        
        self.html_output += '<h2>Proceso de Solución con Fracciones Exactas</h2>'
        
        # Eliminar artificiales de Z
        matrix = self.eliminate_artificial_from_z(matrix, basis_vars, all_var_names)
        
        # Iteraciones
        self.iteration = 0
        max_iterations = 50
        
        while self.iteration < max_iterations:
            pivot_row, pivot_col = self.find_pivot(matrix)
            self.html_output += self.create_table_html(matrix, all_var_names, basis_vars, pivot_row, pivot_col)
            
            if pivot_row == -1:
                self.html_output += '<p><strong>Solución óptima encontrada.</strong></p>'
                break
            
            matrix = self.pivot_operation(matrix, pivot_row, pivot_col, basis_vars, all_var_names)
            self.iteration += 1
        
        # Solución final
        self.html_output += '<h2>Solución Final</h2>'
        
        # Verificar factibilidad
        artificial_in_basis = False
        for i, var in enumerate(basis_vars):
            if var.startswith('a') and (matrix[i][-1].coefficient > 0 or matrix[i][-1].M_coefficient > 0):
                artificial_in_basis = True
                break
        
        if artificial_in_basis:
            self.html_output += '<p><strong>El problema no tiene solución factible.</strong></p>'
        else:
            # Extraer solución
            solution = {}
            for i, var in enumerate(all_var_names[:-1]):
                if var in basis_vars:
                    row_idx = basis_vars.index(var)
                    solution[var] = matrix[row_idx][-1]
                else:
                    solution[var] = MixedValue(0, 0)
            
            # Valor objetivo
            z_value = matrix[-1][-1]
            z_value_display = MixedValue(-z_value.coefficient, -z_value.M_coefficient)
            if not minimize:
                z_value_display = MixedValue(-z_value_display.coefficient, -z_value_display.M_coefficient)
            
            self.html_output += f'<p><strong>Valor {"mínimo" if minimize else "máximo"} de la función objetivo: {self.mixed_value_to_html(z_value_display)}</strong></p>'
            self.html_output += '<p><strong>Valores de las variables:</strong></p><ul>'
            
            for i in range(len(objective)):
                var_name = f"x{i+1}"
                value = solution.get(var_name, MixedValue(0, 0))
                self.html_output += f'<li>{var_name} = {self.mixed_value_to_html(value)}</li>'
            
            self.html_output += '</ul>'
        
        self.html_output += '</body></html>'
        return self.html_output

# Función de prueba
def test_extended():
    solver = GranMSimplexExtended()
    
    print("=== MÉTODO DE LA GRAN M - ANÁLISIS COMPLETO ===")
    
    # Ejemplo: Minimización con restricciones mixtas
    print("\nPROBLEMA DE MINIMIZACIÓN CON RESTRICCIONES MIXTAS:")
    print("Minimizar Z = 2x1 + 3x2")
    print("Sujeto a:")
    print("  x1 + x2 >= 4")
    print("  2x1 + x2 >= 6")
    print("  x1, x2 >= 0")
    
    objetivo = [2, 3]
    restricciones = [
        [1, 1, 4],   # x1 + x2 >= 4
        [2, 1, 6],   # 2x1 + x2 >= 6  
    ]
    tipos = ['>=', '>=']
    
    html_report = solver.solve(objetivo, restricciones, tipos, minimize=True)
    
    with open("minimizar.html", "w", encoding="utf-8") as f:
        f.write(html_report)
    
    print("✅ Reporte completo generado: gran_m_completo.html")

    html_new = solver.solve([3,2], restricciones, tipos, minimize=False)

    with open("maximizar.html", "w", encoding="utf-8") as f:
        f.write(html_new)
    
    return html_report

if __name__ == "__main__":
    test_extended()
