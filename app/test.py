from typing import List, Tuple, Dict
import pandas as pd
import numpy as np
from fractions import Fraction

class TranslationHelper:
    """Helper class to handle translations for step-by-step solutions"""
    def __init__(self, translations_dict=None):
        self.translations = translations_dict or {}
    
    def _(self, text):
        """Translate text using the provided translations dictionary"""
        return self.translations.get(text, text)

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
    def __init__(self, translation_helper: TranslationHelper = None):
        self.M = "M"
        self.iteration = 0
        self.html_output = ""
        self.is_minimization = True
        self.translation_helper = translation_helper or TranslationHelper()
        
    def _(self, text):
        """Translation helper method"""
        return self.translation_helper._(text)
    
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
        """Genera la transformación del problema a forma estándar con variables auxiliares"""
        num_vars = len(objective)
        
        # Contadores para variables auxiliares
        slack_count = 0
        surplus_count = 0
        artificial_count = 0
        
        # Listas para almacenar información de variables
        slack_vars = []
        surplus_vars = []
        artificial_vars = []
        
        html = '<div class="mb-6 p-4 rounded bg-base-100 border border-primary/20">'
        html += f'<h2 class="font-bold text-lg mb-4 text-primary">{self._("Transformación a Forma Estándar para el Algoritmo Simplex")}</h2>'
        
        # Analizar cada restricción
        html += f'<h3 class="font-bold text-base mb-3 text-secondary">{self._("Conversión de Desigualdades")}:</h3><ul class="list-disc pl-5">'
        for i, (constraint, constraint_type) in enumerate(zip(constraints, constraint_types)):
            html += f'<li class="mb-2"><strong>{self._("Ecuación")} {i+1}:</strong> '
            
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
            
            html += f'<span class="font-mono bg-base-200 px-2 py-1 rounded text-sm">{constraint_str}</span>'
            
            # Explicar qué variables se agregan
            if constraint_type in ['<=', '<']:
                slack_count += 1
                slack_var = f"s{slack_count}"
                slack_vars.append(slack_var)
                html += f'<br>→ <span class="text-info font-medium">{self._("Introducir variable de holgura")} <strong>{slack_var}</strong> ≥ 0 {self._("para convertir a igualdad")}</span>'
                
            elif constraint_type in ['>=', '>']:
                surplus_count += 1
                artificial_count += 1
                surplus_var = f"H{surplus_count}"
                artificial_var = f"a{artificial_count}"
                surplus_vars.append(surplus_var)
                artificial_vars.append(artificial_var)
                html += f'<br>→ <span class="text-warning font-medium">{self._("Introducir variable de exceso")} <strong>{surplus_var}</strong> ≥ 0</span>'
                html += f'<br>→ <span class="text-error font-medium">{self._("Requerir variable artificial")} <strong>{artificial_var}</strong> ≥ 0 {self._("para solución básica inicial")}</span>'
                
            elif constraint_type == '=':
                artificial_count += 1
                artificial_var = f"a{artificial_count}"
                artificial_vars.append(artificial_var)
                html += f'<br>→ <span class="text-error font-medium">{self._("Introducir variable artificial")} <strong>{artificial_var}</strong> ≥ 0 {self._("para obtener base factible")}</span>'
            
            html += '</li>'
        
        html += '</ul>'
        
        # Problema transformado
        html += f'<h3 class="font-bold text-base mb-3 text-secondary mt-6">{self._("Problema en Forma Estándar")}:</h3>'
        
        # Función objetivo modificada
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
        
        # Variables artificiales (penalizadas con M)
        for artificial_var in artificial_vars:
            if minimize:
                obj_str += f" + M{artificial_var}"
            else:
                obj_str += f" - M{artificial_var}"
        
        html += f'<p class="mb-4 font-mono bg-base-200 px-3 py-2 rounded border-l-4 border-primary"><strong>{obj_str}</strong></p>'
        
        # Sistema de ecuaciones resultante
        html += '<p class="mb-2"><strong>Sistema de ecuaciones lineales:</strong></p><ul class="list-disc pl-5">'
        
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
            
            # Variables auxiliares según el tipo de restricción
            if constraint_type in ['<=', '<']:
                slack_idx += 1
                constraint_str += f" + <span class='text-info font-medium'>s<sub>{slack_idx}</sub></span>"
                
            elif constraint_type in ['>=', '>']:
                surplus_idx += 1
                artificial_idx += 1
                constraint_str += f" - <span class='text-warning font-medium'>H<sub>{surplus_idx}</sub></span> + <span class='text-error font-medium'>a<sub>{artificial_idx}</sub></span>"
                
            elif constraint_type == '=':
                artificial_idx += 1
                constraint_str += f" + <span class='text-error font-medium'>a<sub>{artificial_idx}</sub></span>"
            
            # Término independiente
            rhs_frac = Fraction(constraint[-1]).limit_denominator()
            if rhs_frac.denominator == 1:
                constraint_str += f" = {rhs_frac.numerator}"
            else:
                constraint_str += f" = {rhs_frac.numerator}/{rhs_frac.denominator}"
            
            html += f'<li class="mb-1 font-mono text-sm">{constraint_str}</li>'
        
        # Condiciones de no negatividad
        all_vars = [f"x<sub>{i+1}</sub>" for i in range(num_vars)]
        all_vars.extend([f"<span class='text-info font-medium'>s<sub>{i+1}</sub></span>" for i in range(len(slack_vars))])
        all_vars.extend([f"<span class='text-warning font-medium'>H<sub>{i+1}</sub></span>" for i in range(len(surplus_vars))])
        all_vars.extend([f"<span class='text-error font-medium'>a<sub>{i+1}</sub></span>" for i in range(len(artificial_vars))])
        
        html += f'<li class="mb-1 font-mono text-sm">Condiciones: {", ".join(all_vars)} ≥ 0</li>'
        html += '</ul></div>'
        
        return html

    def generate_initial_table_steps(self, objective: List[float], constraints: List[List[float]], 
                                   constraint_types: List[str], minimize: bool = True) -> str:
        """Genera la explicación detallada para establecer la tabla simplex inicial"""
        html = '<div class="mb-6 p-4 rounded bg-base-100 border-l-4 border-warning">'
        html += '<h2 class="font-bold text-lg mb-4 text-warning">Construcción de la Tabla Simplex Inicial</h2>'
        
        num_vars = len(objective)
        num_constraints = len(constraints)
        
        # Fase 1: Catálogo de variables del sistema
        html += '<h3 class="font-bold text-base mb-3 text-secondary">Fase 1: Inventario de Variables del Sistema</h3>'
        html += f'<p class="mb-2">Variables de decisión: x<sub>1</sub>, x<sub>2</sub>, ..., x<sub>{num_vars}</sub></p>'
        
        slack_count = sum(1 for ct in constraint_types if ct in ['<=', '<'])
        surplus_count = sum(1 for ct in constraint_types if ct in ['>=', '>'])
        artificial_count = sum(1 for ct in constraint_types if ct in ['>=', '>', '='])
        
        if slack_count > 0:
            html += f'<p class="mb-2">Variables de holgura: <span class="text-info font-medium">s<sub>1</sub>, s<sub>2</sub>, ..., s<sub>{slack_count}</sub></span></p>'
        if surplus_count > 0:
            html += f'<p class="mb-2">Variables de exceso: <span class="text-warning font-medium">H<sub>1</sub>, H<sub>2</sub>, ..., H<sub>{surplus_count}</sub></span></p>'
        if artificial_count > 0:
            html += f'<p class="mb-2">Variables artificiales: <span class="text-error font-medium">a<sub>1</sub>, a<sub>2</sub>, ..., a<sub>{artificial_count}</sub></span></p>'
        
        total_vars = num_vars + slack_count + surplus_count + artificial_count
        html += f'<p class="mb-4 font-bold">Dimensión total del sistema: {total_vars} variables</p>'
        
        # Fase 2: Estructuración matricial
        html += '<h3 class="font-bold text-base mb-3 text-secondary">Fase 2: Estructuración de la Matriz de Coeficientes</h3>'
        html += '<p class="mb-2">Configuración sistemática de la matriz por categorías de variables:</p><ul class="list-disc pl-5">'
        
        # Variables de decisión
        html += '<li class="mb-1"><strong>Variables de decisión (x<sub>1</sub>, x<sub>2</sub>, ...):</strong> Coeficientes extraídos directamente del planteamiento original</li>'
        
        # Variables de holgura
        if slack_count > 0:
            html += '<li class="mb-1"><strong>Variables de holgura (s<sub>i</sub>):</strong> <span class="text-info">Matriz identidad parcial - valor unitario en ecuación asociada, cero en resto</span></li>'
        
        # Variables de exceso
        if surplus_count > 0:
            html += '<li class="mb-1"><strong>Variables de exceso (H<sub>i</sub>):</strong> <span class="text-warning">Coeficiente negativo unitario en ecuación correspondiente, cero en otras</span></li>'
        
        # Variables artificiales
        if artificial_count > 0:
            html += '<li class="mb-1"><strong>Variables artificiales (a<sub>i</sub>):</strong> <span class="text-error">Matriz identidad completa - valor unitario en ecuación específica, cero en demás</span></li>'
        
        html += '</ul>'
        
        # Fase 3: Determinación de la base factible inicial
        html += '<h3 class="font-bold text-base mb-3 text-secondary">Fase 3: Establecimiento de la Solución Básica Factible Inicial</h3>'
        html += '<p class="mb-2">Selección de variables para formar la base inicial considerando la propiedad de independencia lineal:</p><ul class="list-disc pl-5">'
        
        basis_vars = []
        slack_idx = 0
        surplus_idx = 0
        artificial_idx = 0
        
        for i, constraint_type in enumerate(constraint_types):
            if constraint_type in ['<=', '<']:
                slack_idx += 1
                basis_vars.append(f"s<sub>{slack_idx}</sub>")
                html += f'<li class="mb-1">Ecuación {i+1}: Base constituida por <span class="text-info font-bold">s<sub>{slack_idx}</sub></span></li>'
            elif constraint_type in ['>=', '>']:
                artificial_idx += 1
                basis_vars.append(f"a<sub>{artificial_idx}</sub>")
                html += f'<li class="mb-1">Ecuación {i+1}: Base constituida por <span class="text-error font-bold">a<sub>{artificial_idx}</sub></span></li>'
            elif constraint_type == '=':
                artificial_idx += 1
                basis_vars.append(f"a<sub>{artificial_idx}</sub>")
                html += f'<li class="mb-1">Ecuación {i+1}: Base constituida por <span class="text-error font-bold">a<sub>{artificial_idx}</sub></span></li>'
        
        html += '</ul>'
        html += f'<p class="mb-4 font-bold">Conjunto básico inicial: {{{", ".join(basis_vars)}}}</p>'
        
        # Fase 4: Configuración de la función objetivo
        html += '<h3 class="font-bold text-base mb-3 text-secondary">Fase 4: Configuración de la Función de Evaluación (Fila Z)</h3>'
        html += '<p class="mb-2">Establecimiento de los coeficientes de evaluación para el proceso iterativo:</p><ol class="list-decimal pl-5">'
        html += '<li class="mb-1"><strong>Variables de decisión:</strong> Transferencia directa de coeficientes del objetivo original</li>'
        html += '<li class="mb-1"><strong>Variables de holgura y exceso:</strong> Coeficiente neutro (valor cero)</li>'
        html += '<li class="mb-1"><strong>Variables artificiales:</strong> Penalización mediante coeficiente M (minimización) o -M (maximización)</li>'
        html += '<li class="mb-1"><strong>Valor de la función:</strong> Inicialización en cero</li>'
        html += '</ol>'
        
        # Fase 5: Proceso de depuración de variables artificiales
        if artificial_count > 0:
            html += '<h3 class="font-bold text-base mb-3 text-secondary">Fase 5: Depuración de Variables Artificiales en la Función Objetivo</h3>'
            html += '<div class="bg-base-100 p-3 rounded border-l-4 border-error mb-4">'
            html += '<p class="mb-2 text-error">Las variables artificiales presentes en la base inicial requieren neutralización en la función objetivo '
            html += 'mediante operaciones de fila elementales para mantener la equivalencia del sistema:</p>'
            html += '<p class="mb-2 font-bold text-error">Procedimiento de neutralización para cada variable artificial a<sub>i</sub> básica:</p><ol class="list-decimal pl-5 text-error">'
            html += '<li class="mb-1">Localizar la ecuación donde a<sub>i</sub> actúa como variable básica (coeficiente unitario)</li>'
            html += '<li class="mb-1">Aplicar multiplicación escalar por -M (o +M según corresponda) a dicha ecuación</li>'
            html += '<li class="mb-1">Efectuar suma algebraica del resultado con la fila de evaluación Z</li>'
            html += '</ol>'
            html += '<p class="text-error">Esta operación garantiza coeficiente nulo para las variables artificiales en la función objetivo.</p>'
            html += '</div>'
        
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
            
            # bj (lado derecho)
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
        """Elimina variables artificiales de la fila Z con explicación detallada"""
        artificial_indices = [i for i, var in enumerate(all_var_names[:-1]) if var.startswith('a')]
        
        if not artificial_indices:
            return matrix
            
        self.html_output += '<div class="mb-6 p-4 rounded bg-base-100 border-l-4 border-error">'
        self.html_output += '<h2 class="font-bold text-lg mb-4 text-error">Neutralización de Variables Artificiales en la Función Objetivo</h2>'
        self.html_output += '<p class="mb-3">Las variables artificiales presentes en la base inicial requieren ser neutralizadas en la fila Z '
        self.html_output += 'mediante operaciones de fila para mantener la consistencia del algoritmo:</p>'
        
        for art_idx in artificial_indices:
            art_var = all_var_names[art_idx]
            z_coef = matrix[-1][art_idx]
            
            if z_coef.M_coefficient != 0 or z_coef.coefficient != 0:
                self.html_output += f'<h3 class="font-bold text-base mb-2">Procesando {art_var} (valor actual en Z: {self.mixed_value_to_html(z_coef, True)})</h3>'
                
                # Encontrar fila donde está la variable artificial
                for i, basis_var in enumerate(basis_vars):
                    if basis_var == art_var and i < len(matrix) - 1:
                        multiplier = matrix[-1][art_idx]
                        
                        self.html_output += f'<p class="mb-2">• {art_var} actúa como variable básica en la ecuación F{i+1}</p>'
                        self.html_output += f'<p class="mb-2">• Transformación aplicada: Fila_Z = Fila_Z - ({self.mixed_value_to_html(multiplier)}) × F{i+1}</p>'
                        
                        self.html_output += '<div class="overflow-x-auto mb-3"><table class="table table-sm w-full text-center text-xs">'
                        self.html_output += '<thead><tr><th class="bg-base-200 px-1 py-1">Variable</th><th class="bg-base-200 px-1 py-1">Z Original</th><th class="bg-base-200 px-1 py-1">-</th><th class="bg-base-200 px-1 py-1">Factor × F{i+1}</th><th class="bg-base-200 px-1 py-1">=</th><th class="bg-base-200 px-1 py-1">Z Nueva</th></tr></thead><tbody>'
                        
                        for j in range(len(matrix[0])):
                            old_z_val = matrix[-1][j]
                            factor_times_row = multiplier * matrix[i][j]
                            matrix[-1][j] = matrix[-1][j] - multiplier * matrix[i][j]
                            var_name = all_var_names[j] if j < len(all_var_names) else 'bj'
                            
                            css_class = "bg-warning bg-opacity-30 border-warning" if j == art_idx else ""
                            self.html_output += f'<tr class="{css_class}"><td class="px-1 py-1 font-bold">{var_name}</td>'
                            self.html_output += f'<td class="px-1 py-1">{self.mixed_value_to_html(old_z_val, True)}</td>'
                            self.html_output += f'<td class="px-1 py-1">-</td>'
                            self.html_output += f'<td class="px-1 py-1">{self.mixed_value_to_html(factor_times_row)}</td>'
                            self.html_output += f'<td class="px-1 py-1">=</td>'
                            self.html_output += f'<td class="px-1 py-1">{self.mixed_value_to_html(matrix[-1][j], True)}</td></tr>'
                        
                        self.html_output += '</tbody></table></div>'
                        break
                        
        self.html_output += '<p class="mt-3 font-bold text-success">✅ Neutralización completada. Las variables artificiales ahora tienen coeficiente cero en la función objetivo.</p>'
        self.html_output += '</div>'
        
        return matrix

    def find_pivot(self, matrix: List[List]) -> Tuple[int, int]:
        """Encuentra el elemento pivote con explicación detallada"""
        z_row = matrix[-1][:-1]
        
        # Agregar explicación del criterio de optimalidad
        self.html_output += '<div class="mb-6 p-4 rounded bg-base-100 border-l-4 border-accent">'
        self.html_output += f'<h3 class="font-bold text-lg mb-3 text-accent">{self._("Criterio de Optimalidad")}</h3>'
        self.html_output += f'<p class="mb-3">{self._("Analizando la fila Z para determinar si se ha alcanzado la solución óptima o si se requiere otra iteración")}:</p>'
        
        # Mostrar valores de la fila Z
        self.html_output += '<div class="overflow-x-auto"><table class="table table-sm w-full text-center text-xs">'
        self.html_output += '<thead><tr>'
        for i, val in enumerate(z_row):
            var_name = f"x{i+1}" if i < len(z_row) else "Variable"
            self.html_output += f'<th class="bg-base-200 px-1 py-1">{var_name}</th>'
        self.html_output += '</tr></thead><tbody><tr>'
        
        for val in z_row:
            css_class = ""
            if val.is_negative():
                css_class = "bg-error text-error-content font-bold border-2 border-error"
            self.html_output += f'<td class="px-1 py-1 {css_class}">{self.mixed_value_to_html(val, True)}</td>'
        self.html_output += '</tr></tbody></table></div>'
        
        # Encontrar el más negativo
        most_negative_idx = -1
        most_negative_val = None
        
        for i, val in enumerate(z_row):
            if val.is_negative():
                if most_negative_val is None or self.is_more_negative(val, most_negative_val):
                    most_negative_val = val
                    most_negative_idx = i
        
        if most_negative_idx == -1:
            self.html_output += f'<p class="mt-3 font-bold text-success">✅ {self._("Todos los coeficientes de la fila Z son no negativos. Se ha alcanzado la solución óptima")}.</p>'
            self.html_output += '</div>'
            return -1, -1  # Óptimo encontrado
        
        pivot_col = most_negative_idx
        self.html_output += f'<p class="mt-3">El coeficiente más negativo es <strong>{self.mixed_value_to_html(most_negative_val, True)}</strong> '
        self.html_output += f'en la columna {pivot_col + 1} (variable x{pivot_col + 1}).</p>'
        self.html_output += f'<p class="font-bold text-warning">→ Variable que entra: x{pivot_col + 1}</p>'
        self.html_output += '</div>'
        
        # Prueba de la razón
        ratios = []
        for i in range(len(matrix) - 1):
            if matrix[i][pivot_col].coefficient > 0 or matrix[i][pivot_col].M_coefficient > 0:
                # Calcular razón bj / elemento_columna
                rhs = matrix[i][-1]
                divisor = matrix[i][pivot_col]
                
                # Solo consideramos casos donde el divisor es positivo y sin M
                if divisor.M_coefficient == 0 and divisor.coefficient > 0:
                    if rhs.M_coefficient == 0:  # bj sin M
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
            self.html_output += '<div class="mb-4 p-3 rounded bg-base-100 border-l-4 border-error">'
            self.html_output += '<p class="font-bold">❌ El problema no tiene solución acotada (es no acotado).</p>'
            self.html_output += '</div>'
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
        """Realiza operación de pivoteo con fracciones y explicación detallada"""
        pivot_element = matrix[pivot_row][pivot_col]
        
        # HTML para identificación del pivoteo
        self.html_output += '<div class="mb-6 p-4 rounded bg-base-100 border-l-4 border-info">'
        self.html_output += '<h3 class="font-bold text-lg mb-3 text-info">Detalles del Pivoteo</h3>'
        self.html_output += f"<p class='mb-2'><strong>Variable que entra:</strong> <span class='badge badge-success'>{all_var_names[pivot_col]}</span></p>"
        self.html_output += f"<p class='mb-2'><strong>Variable que sale:</strong> <span class='badge badge-error'>{basis_vars[pivot_row]}</span></p>"
        self.html_output += f"<p class='mb-4'><strong>Elemento pivote:</strong> <span class='badge badge-warning'>{self.mixed_value_to_html(pivot_element)}</span></p>"
        
        # Justificación de selección de columna pivote
        self.html_output += '<h4 class="font-bold text-base mb-2 text-secondary">Justificación de la Columna Pivote:</h4>'
        self.html_output += f'<p class="mb-3 text-sm">Se selecciona la columna {pivot_col + 1} (variable {all_var_names[pivot_col]}) porque tiene el coeficiente más negativo en la fila Z, '
        self.html_output += 'indicando que es la variable que más puede mejorar la función objetivo.</p>'
        
        # Cálculo de razones para selección de fila pivote
        self.html_output += '<h4 class="font-bold text-base mb-2 text-secondary">Cálculo de Razones para Selección de Fila Pivote:</h4>'
        self.html_output += '<div class="overflow-x-auto"><table class="table table-sm w-full text-center text-xs">'
        self.html_output += '<thead><tr><th class="bg-base-200 px-1 py-1">Fila</th><th class="bg-base-200 px-1 py-1">bj</th><th class="bg-base-200 px-1 py-1">Coef. Pivote</th><th class="bg-base-200 px-1 py-1">Razón</th><th class="bg-base-200 px-1 py-1">Factible</th></tr></thead><tbody>'
        
        for i in range(len(matrix) - 1):  # Excluir fila Z
            rhs = matrix[i][-1]
            coef_pivote = matrix[i][pivot_col]
            
            if coef_pivote.coefficient > 0 and coef_pivote.M_coefficient == 0:
                ratio = rhs.coefficient / coef_pivote.coefficient
                factible = "Sí" if ratio >= 0 else "No"
                css_class = "bg-warning bg-opacity-30 border-warning" if i == pivot_row else ""
                ratio_float = float(ratio)
                self.html_output += f'<tr class="{css_class}"><td class="px-1 py-1">F{i+1}</td><td class="px-1 py-1">{self.mixed_value_to_html(rhs)}</td><td class="px-1 py-1">{self.mixed_value_to_html(coef_pivote)}</td><td class="px-1 py-1">{ratio_float:.3f}</td><td class="px-1 py-1">{factible}</td></tr>'
            else:
                self.html_output += f'<tr><td class="px-1 py-1">F{i+1}</td><td class="px-1 py-1">{self.mixed_value_to_html(rhs)}</td><td class="px-1 py-1">{self.mixed_value_to_html(coef_pivote)}</td><td class="px-1 py-1">N/A</td><td class="px-1 py-1">No</td></tr>'
        
        self.html_output += '</tbody></table></div>'
        self.html_output += f'<p class="mt-2 text-sm">{self._("Se selecciona la fila")} {pivot_row + 1} {self._("porque tiene la menor razón positiva")}.</p>'
        self.html_output += '</div>'
        
        # Normalizar fila pivote
        self.html_output += '<div class="mb-6 p-4 rounded bg-base-100 border-l-4 border-warning">'
        self.html_output += f"<h3 class='font-bold text-lg mb-3 text-warning'>{self._('Paso 1: Normalización de la Fila Pivote')} F{pivot_row+1}</h3>"
        self.html_output += f"<p class='mb-3'>{self._('Dividir toda la fila')} F{pivot_row+1} {self._('entre el elemento pivote')} ({self.mixed_value_to_html(pivot_element)}) {self._('para que el elemento pivote sea 1')}:</p>"
        self.html_output += '<div class="overflow-x-auto"><table class="table table-sm w-full text-center text-xs">'
        self.html_output += f'<thead><tr><th class="bg-base-200 px-1 py-1">{self._("Variable")}</th><th class="bg-base-200 px-1 py-1">{self._("Valor Original")}</th><th class="bg-base-200 px-1 py-1">÷</th><th class="bg-base-200 px-1 py-1">{self._("Pivote")}</th><th class="bg-base-200 px-1 py-1">=</th><th class="bg-base-200 px-1 py-1">{self._("Nuevo Valor")}</th></tr></thead><tbody>'
        
        for j in range(len(matrix[0])):
            old_val = matrix[pivot_row][j]
            matrix[pivot_row][j] = matrix[pivot_row][j] / pivot_element
            var_name = all_var_names[j] if j < len(all_var_names) else 'RHS'
            
            self.html_output += f'<tr><td class="px-1 py-1 font-bold">{var_name}</td>'
            self.html_output += f'<td class="px-1 py-1">{self.mixed_value_to_html(old_val)}</td>'
            self.html_output += f'<td class="px-1 py-1">÷</td>'
            self.html_output += f'<td class="px-1 py-1">{self.mixed_value_to_html(pivot_element)}</td>'
            self.html_output += f'<td class="px-1 py-1">=</td>'
            self.html_output += f'<td class="px-1 py-1 bg-warning bg-opacity-30 border-warning">{self.mixed_value_to_html(matrix[pivot_row][j])}</td></tr>'
        
        self.html_output += '</tbody></table></div></div>'
        
        # Actualizar otras filas
        self.html_output += '<div class="mb-6 p-4 rounded bg-base-100 border-l-4 border-secondary">'
        self.html_output += f"<h3 class='font-bold text-lg mb-3 text-secondary'>{self._('Paso 2: Actualización de las Otras Filas')}</h3>"
        self.html_output += f"<p class='mb-3'>{self._('Para cada fila i ≠ fila pivote')}: {self._('Nueva_Fila_i = Fila_i - (Factor × Fila_Pivote_Normalizada)')}</p>"
        
        for i in range(len(matrix)):
            if i != pivot_row:
                factor = matrix[i][pivot_col]
                if factor.coefficient != 0 or factor.M_coefficient != 0:
                    fila_name = f"F{i+1}" if i < len(matrix) - 1 else self._("Fila Z")
                    normalizada_text = self._("normalizada")
                    self.html_output += f"<h4 class='font-bold text-base mb-2 mt-4'>{fila_name} = {fila_name} - ({self.mixed_value_to_html(factor)}) × F{pivot_row+1}_{normalizada_text}</h4>"
                    
                    self.html_output += '<div class="overflow-x-auto"><table class="table table-sm w-full text-center text-xs">'
                    self.html_output += f'<thead><tr><th class="bg-base-200 px-1 py-1">{self._("Variable")}</th><th class="bg-base-200 px-1 py-1">{self._("Original")}</th><th class="bg-base-200 px-1 py-1">-</th><th class="bg-base-200 px-1 py-1">{self._("Factor × Pivote")}</th><th class="bg-base-200 px-1 py-1">=</th><th class="bg-base-200 px-1 py-1">{self._("Nuevo")}</th></tr></thead><tbody>'
                    
                    for j in range(len(matrix[0])):
                        old_val = matrix[i][j]
                        pivot_val = matrix[pivot_row][j]
                        producto = factor * pivot_val
                        matrix[i][j] = matrix[i][j] - factor * pivot_val
                        var_name = all_var_names[j] if j < len(all_var_names) else 'RHS'
                        is_z_row = (i == len(matrix) - 1)
                        
                        self.html_output += f'<tr><td class="px-1 py-1 font-bold">{var_name}</td>'
                        self.html_output += f'<td class="px-1 py-1">{self.mixed_value_to_html(old_val, is_z_row)}</td>'
                        self.html_output += f'<td class="px-1 py-1">-</td>'
                        self.html_output += f'<td class="px-1 py-1">({self.mixed_value_to_html(factor)} × {self.mixed_value_to_html(pivot_val)}) = {self.mixed_value_to_html(producto)}</td>'
                        self.html_output += f'<td class="px-1 py-1">=</td>'
                        self.html_output += f'<td class="px-1 py-1 bg-success bg-opacity-20">{self.mixed_value_to_html(matrix[i][j], is_z_row)}</td></tr>'
                    
                    self.html_output += '</tbody></table></div>'
        
        self.html_output += '</div>'
        
        # Actualizar base
        old_basic_var = basis_vars[pivot_row]
        basis_vars[pivot_row] = all_var_names[pivot_col]
        
        self.html_output += '<div class="mb-4 p-3 rounded bg-base-100 border border-base-300">'
        self.html_output += f'<p class="font-bold">Actualización de la Base:</p>'
        self.html_output += f'<p>La variable <span class="badge badge-error">{old_basic_var}</span> sale de la base y entra <span class="badge badge-success">{all_var_names[pivot_col]}</span>.</p>'
        self.html_output += '</div>'
        
        return matrix

    def create_table_html(self, matrix: List[List], all_var_names: List[str], 
                         basis_vars: List[str], pivot_row: int = -1, pivot_col: int = -1) -> str:
        """Crea tabla HTML con fracciones usando clases CSS modernas"""
        html = '<div class="mb-6 p-4 rounded-xl border border-primary/20 shadow-md bg-base-100 overflow-x-auto">'
        html += f'<h3 class="font-bold text-lg mb-4 text-primary">{self._("Iteración")} {self.iteration}</h3>'
        
        html += '<table class="table table-sm w-full overflow-x-auto border-collapse text-center">'
        html += f'<thead><tr><th class="bg-base-200 px-2 py-1 border font-bold">{self._("Base")}</th>'
        
        for var_name in all_var_names:
            html += f'<th class="bg-base-200 px-2 py-1 border font-bold">{var_name}</th>'
        html += '</tr></thead><tbody>'
        
        for i in range(len(matrix)):
            html += '<tr>'
            if i < len(basis_vars):
                html += f'<td class="border px-2 py-1 font-bold">{basis_vars[i]}</td>'
            else:
                html += '<td class="border px-2 py-1 font-bold">Z</td>'
            
            is_z_row = (i == len(matrix) - 1)
            
            for j in range(len(matrix[0])):
                css_class = "border px-2 py-1"
                if i == pivot_row and j == pivot_col:
                    css_class += " bg-error text-error-content font-bold border-2 border-error"  # Elemento pivote
                elif i == pivot_row:
                    css_class += " bg-warning bg-opacity-30"  # Fila pivote
                elif j == pivot_col:
                    css_class += " bg-warning bg-opacity-30"  # Columna pivote
                
                html += f'<td class="{css_class}">{self.mixed_value_to_html(matrix[i][j], is_z_row)}</td>'
            html += '</tr>'
        
        html += '</tbody></table></div>'
        return html

    def solve(self, objective: List[float], constraints: List[List[float]], 
              constraint_types: List[str], minimize: bool = True) -> str:
        """Resuelve usando fracciones exactas con modelo extendido y pasos detallados"""
        
        # HTML inicial con clases CSS modernas
        self.html_output = """
        <div class="w-full max-w-none">
            <h1 class="text-3xl font-bold text-primary mb-6 border-b-2 border-primary pb-3">
                Resolución mediante el Algoritmo de la Gran M - Solución Detallada
            </h1>
        """
        
        # Problema de programación lineal original
        self.html_output += '<div class="mb-6 p-4 rounded bg-base-100 border border-primary/20">'
        self.html_output += '<h2 class="font-bold text-lg mb-4 text-primary">Formulación del Problema de Programación Lineal</h2>'
        
        obj_str = self._("Minimizar") + " " if minimize else self._("Maximizar") + " "
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
        
        self.html_output += f'<p class="mb-3"><strong>{obj_str}</strong></p>'
        
        # Restricciones
        self.html_output += f'<p class="mb-2"><strong>{self._("Sujeto a")}:</strong></p><ul class="list-disc pl-5">'
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
            
            self.html_output += f'<li class="mb-1">{constraint_str}</li>'
        
        var_list = ", ".join([f"x<sub>{i+1}</sub>" for i in range(len(objective))])
        self.html_output += f'<li class="mb-1">{var_list} ≥ 0</li>'
        self.html_output += '</ul></div>'
        
        # Transformación a forma estándar
        self.html_output += self.generate_extended_model(objective, constraints, constraint_types, minimize)
        
        # Procedimiento de construcción de la tabla simplex
        self.html_output += self.generate_initial_table_steps(objective, constraints, constraint_types, minimize)
        
        # Configurar y resolver
        matrix, all_var_names, basis_vars = self.setup_problem(objective, constraints, constraint_types, minimize)
        
        self.html_output += '<div class="mb-6 p-4 rounded bg-base-100 border border-primary/20">'
        self.html_output += '<h2 class="font-bold text-lg mb-4 text-primary">Aplicación del Algoritmo Iterativo con Aritmética Exacta</h2>'
        self.html_output += '</div>'
        
        # Eliminar artificiales de Z
        matrix = self.eliminate_artificial_from_z(matrix, basis_vars, all_var_names)
        
        # Iteraciones
        self.iteration = 0
        max_iterations = 50
        
        while self.iteration < max_iterations:
            pivot_row, pivot_col = self.find_pivot(matrix)
            self.html_output += self.create_table_html(matrix, all_var_names, basis_vars, pivot_row, pivot_col)
            
            if pivot_row == -1:
                self.html_output += '<div class="mb-4 p-3 rounded bg-base-100 border-l-4 border-success">'
                self.html_output += f'<p class="font-bold text-success">✅ {self._("Solución óptima encontrada")}.</p>'
                self.html_output += '</div>'
                break
            
            matrix = self.pivot_operation(matrix, pivot_row, pivot_col, basis_vars, all_var_names)
            self.iteration += 1
        
        # Solución final
        self.html_output += '<div class="mb-6 p-4 rounded bg-base-100 border-l-4 border-success shadow">'
        self.html_output += f'<h2 class="font-bold text-lg mb-4 text-success">{self._("Solución Final")}</h2>'
        
        # Verificar factibilidad
        artificial_in_basis = False
        for i, var in enumerate(basis_vars):
            if var.startswith('a') and (matrix[i][-1].coefficient > 0 or matrix[i][-1].M_coefficient > 0):
                artificial_in_basis = True
                break
        
        if artificial_in_basis:
            self.html_output += '<p class="font-bold text-error">❌ El problema no tiene solución factible.</p>'
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
            
            min_max_text = self._("mínimo") if minimize else self._("máximo")
            self.html_output += f'<p class="mb-3">{self._("Se alcanzó una solución óptima con un valor")} <strong>{min_max_text} {self._("de Z")} = {self.mixed_value_to_html(z_value_display)}</strong>.</p>'
            self.html_output += f'<p class="mb-2"><strong>{self._("Valores de las variables")}:</strong></p><ul class="list-disc pl-5">'
            
            for i in range(len(objective)):
                var_name = f"x{i+1}"
                value = solution.get(var_name, MixedValue(0, 0))
                self.html_output += f'<li class="mb-1">{var_name} = {self.mixed_value_to_html(value)}</li>'
            
            self.html_output += '</ul>'
            
            # Interpretación adicional
            active_vars = []
            for i in range(len(objective)):
                var_name = f"x{i+1}"
                value = solution.get(var_name, MixedValue(0, 0))
                if value.coefficient > 0 and value.M_coefficient == 0:
                    active_vars.append(f"{var_name} = {self.mixed_value_to_html(value)}")
            
            if active_vars:
                self.html_output += f'<p class="mt-3">Las variables que contribuyen a este óptimo son: <strong>{", ".join(active_vars)}</strong>.</p>'
            else:
                self.html_output += '<p class="mt-3">Todas las variables tienen valor cero en esta solución óptima.</p>'
            
            self.html_output += '<p class="mt-2">Esto significa que, bajo las restricciones dadas, esta combinación de variables optimiza el valor de la función objetivo.</p>'
        
        self.html_output += '</div>'
        self.html_output += '</div>'  # Cerrar el contenedor principal
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
