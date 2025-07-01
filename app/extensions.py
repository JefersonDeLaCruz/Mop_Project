from flask_babel import Babel
from flask import request, session
from flask_login import LoginManager

babel = Babel()
login_manager = LoginManager()

def get_local_lang():
    """
    Función para obtener el idioma preferido del usuario.
    Prioridad: 1) Idioma guardado en sesión, 2) Idioma del navegador, 3) Español por defecto
    """
    # Primero revisar si ya existe en la sesión
    lang = session.get("lang")
    if lang and lang in ["en", "es"]:
        return lang
    
    # Si no hay idioma en sesión, usar el idioma preferido del navegador
    lang = request.accept_languages.best_match(["en", "es"])
    if lang:
        print(f"Idioma detectado del navegador: {lang}")
        return lang
    
    # Por defecto español si no se puede determinar
    print("Usando idioma por defecto: es")
    return "es"

def normalize_operation_type(operation_type):
    """
    Normaliza el tipo de operación a valores estándar en español.
    Garantiza compatibilidad entre frontend y backend independientemente del idioma.
    """
    if not operation_type:
        return "Maximizar"
    
    # Mapeo de diferentes formatos al estándar interno
    normalization_map = {
        # Español (valores estándar)
        "Maximizar": "Maximizar",
        "Minimizar": "Minimizar",
        "maximizar": "Maximizar",
        "minimizar": "Minimizar",
        
        # Inglés
        "Maximize": "Maximizar",
        "Minimize": "Minimizar",
        "maximize": "Maximizar",
        "minimize": "Minimizar",
        
        # Otras variaciones
        "MAX": "Maximizar",
        "MIN": "Minimizar",
        "max": "Maximizar",
        "min": "Minimizar"
    }
    
    normalized = normalization_map.get(operation_type.strip())
    if normalized:
        return normalized
    
    print(f"Warning: Tipo de operación no reconocido '{operation_type}', usando 'Maximizar' por defecto")
    return "Maximizar"

def normalize_constraint_operator(operator):
    """
    Normaliza operadores de restricciones a símbolos estándar Unicode.
    """
    if not operator:
        return "≤"
    
    normalization_map = {
        # Símbolos Unicode (estándar)
        "≤": "≤",
        "≥": "≥", 
        "=": "=",
        
        # Símbolos ASCII
        "<=": "≤",
        ">=": "≥",
        "==": "=",
        
        # Texto en español
        "menor o igual": "≤",
        "mayor o igual": "≥",
        "igual": "=",
        
        # Texto en inglés
        "less than or equal": "≤",
        "greater than or equal": "≥",
        "equal": "=",
        "less or equal": "≤",
        "greater or equal": "≥",
        
        # Abreviaciones
        "leq": "≤",
        "geq": "≥",
        "eq": "="
    }
    
    normalized = normalization_map.get(operator.strip())
    if normalized:
        return normalized
    
    print(f"Warning: Operador de restricción no reconocido '{operator}', usando '≤' por defecto")
    return "≤"

def normalize_payload_backend(data):
    """
    Normaliza un payload completo en el backend para garantizar compatibilidad.
    Esta función actúa como una capa de seguridad adicional.
    """
    if not isinstance(data, dict):
        return data
    
    normalized_data = data.copy()
    
    # Normalizar tipo de operación
    if "tipoOperacion" in normalized_data:
        normalized_data["tipoOperacion"] = normalize_operation_type(normalized_data["tipoOperacion"])
    
    # Normalizar operadores de restricciones
    if "restricciones" in normalized_data and isinstance(normalized_data["restricciones"], list):
        for restriccion in normalized_data["restricciones"]:
            if isinstance(restriccion, dict) and "op" in restriccion:
                restriccion["op"] = normalize_constraint_operator(restriccion["op"])
    
    return normalized_data



