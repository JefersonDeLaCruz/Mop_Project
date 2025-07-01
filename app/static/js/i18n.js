// i18n.js - Gestión de internacionalización para el frontend
// Este archivo maneja la normalización de valores dependientes del idioma

/**
 * Mapas de traducción para normalizar valores del frontend
 * Los valores se normalizan a español para mantener compatibilidad con el backend
 */

// Mapa de tipos de operación
const OPERATION_TYPES = {
  // Español (valores internos)
  'Maximizar': 'Maximizar',
  'Minimizar': 'Minimizar',
  
  // Inglés -> Español
  'Maximize': 'Maximizar',
  'Minimize': 'Minimizar',
  
  // Otros posibles valores
  'maximizar': 'Maximizar',
  'minimizar': 'Minimizar',
  'maximize': 'Maximizar',
  'minimize': 'Minimizar'
};

// Mapa de operadores de restricciones
const CONSTRAINT_OPERATORS = {
  // Símbolos (universales)
  '≤': '≤',
  '≥': '≥',
  '=': '=',
  
  // Texto en español
  'menor o igual': '≤',
  'mayor o igual': '≥',
  'igual': '=',
  
  // Texto en inglés
  'less than or equal': '≤',
  'greater than or equal': '≥',
  'equal': '=',
  
  // Abreviaciones
  'leq': '≤',
  'geq': '≥',
  'eq': '='
};

// Mapa de métodos de solución
const SOLUTION_METHODS = {
  // Español (valores internos)
  'Simplex': 'Simplex',
  'General': 'General',
  
  // Inglés -> Español
  'Simplex': 'Simplex',
  'General': 'General',
  'SciPy': 'General'
};

// Términos que pueden aparecer en mensajes y necesitan normalización
const TERMS_MAP = {
  // Estados/resultados
  'optimal': 'óptimo',
  'infeasible': 'no factible',
  'unbounded': 'no acotado',
  'error': 'error',
  
  // Términos matemáticos
  'variable': 'variable',
  'constraint': 'restricción',
  'objective': 'objetivo',
  'solution': 'solución',
  'maximum': 'máximo',
  'minimum': 'mínimo'
};

/**
 * Normaliza un tipo de operación a su valor interno (español)
 * @param {string} operationType - Tipo de operación en cualquier idioma
 * @returns {string} - Tipo de operación normalizado
 */
export function normalizeOperationType(operationType) {
  if (!operationType) return 'Maximizar'; // Default
  
  const normalized = OPERATION_TYPES[operationType.trim()];
  if (normalized) {
    return normalized;
  }
  
  console.warn(`Tipo de operación no reconocido: "${operationType}". Usando "Maximizar" por defecto.`);
  return 'Maximizar';
}

/**
 * Normaliza un operador de restricción a su símbolo estándar
 * @param {string} operator - Operador en cualquier idioma/formato
 * @returns {string} - Operador normalizado
 */
export function normalizeConstraintOperator(operator) {
  if (!operator) return '≤'; // Default
  
  const normalized = CONSTRAINT_OPERATORS[operator.trim()];
  if (normalized) {
    return normalized;
  }
  
  console.warn(`Operador de restricción no reconocido: "${operator}". Usando "≤" por defecto.`);
  return '≤';
}

/**
 * Normaliza un método de solución a su valor interno
 * @param {string} method - Método en cualquier idioma
 * @returns {string} - Método normalizado
 */
export function normalizeSolutionMethod(method) {
  if (!method) return 'General'; // Default
  
  const normalized = SOLUTION_METHODS[method.trim()];
  if (normalized) {
    return normalized;
  }
  
  console.warn(`Método de solución no reconocido: "${method}". Usando "General" por defecto.`);
  return 'General';
}

/**
 * Normaliza un payload completo antes de enviarlo al backend
 * @param {Object} payload - Datos del formulario
 * @returns {Object} - Payload normalizado
 */
export function normalizePayload(payload) {
  const normalized = {
    ...payload,
    tipoOperacion: normalizeOperationType(payload.tipoOperacion),
    funcionObjetivo: payload.funcionObjetivo, // No necesita normalización
    restricciones: payload.restricciones?.map(restriccion => ({
      ...restriccion,
      op: normalizeConstraintOperator(restriccion.op)
    })) || []
  };
  
  console.log('Payload original:', payload);
  console.log('Payload normalizado:', normalized);
  
  return normalized;
}

/**
 * Obtiene el idioma actual de la página
 * @returns {string} - Código de idioma ('es' o 'en')
 */
export function getCurrentLanguage() {
  // Intentar obtener de la etiqueta html lang
  const htmlLang = document.documentElement.lang;
  if (htmlLang) {
    return htmlLang.toLowerCase().substring(0, 2);
  }
  
  // Fallback: buscar en el DOM señales del idioma actual
  const languageIndicators = document.querySelectorAll('[data-lang], .language-indicator');
  for (const indicator of languageIndicators) {
    const lang = indicator.dataset.lang || indicator.textContent?.toLowerCase();
    if (lang?.includes('en') || lang?.includes('english')) return 'en';
    if (lang?.includes('es') || lang?.includes('español')) return 'es';
  }
  
  // Último fallback: español por defecto
  return 'es';
}

/**
 * Verifica si los valores del formulario necesitan normalización
 * @param {Object} formData - Datos del formulario
 * @returns {boolean} - true si necesita normalización
 */
export function needsNormalization(formData) {
  const currentLang = getCurrentLanguage();
  
  // Si estamos en español, probablemente no necesite normalización
  if (currentLang === 'es') {
    return false;
  }
  
  // Si estamos en inglés, verificar si hay valores en inglés
  const hasEnglishValues = 
    formData.tipoOperacion && (formData.tipoOperacion.includes('Maxim') || formData.tipoOperacion.includes('Minim')) ||
    formData.restricciones?.some(r => 
      r.op && (r.op.includes('than') || r.op.includes('equal'))
    );
    
  return hasEnglishValues;
}

/**
 * Traduce términos específicos del español al idioma actual
 * Útil para mostrar términos normalizados en la UI
 * @param {string} term - Término en español
 * @returns {string} - Término traducido
 */
export function translateTerm(term) {
  const currentLang = getCurrentLanguage();
  
  if (currentLang === 'es') {
    return term; // Ya está en español
  }
  
  // Mapeo inverso para mostrar en inglés
  const spanishToEnglish = {
    'Maximizar': 'Maximize',
    'Minimizar': 'Minimize',
    'variable': 'variable',
    'restricción': 'constraint',
    'objetivo': 'objective',
    'solución': 'solution',
    'óptimo': 'optimal',
    'no factible': 'infeasible',
    'no acotado': 'unbounded'
  };
  
  return spanishToEnglish[term] || term;
}

/**
 * Configuración de debug para desarrollo
 */
export const I18N_DEBUG = {
  enabled: true, // Cambiar a false en producción
  
  log: function(message, data = null) {
    if (this.enabled) {
      console.log(`[I18N] ${message}`, data || '');
    }
  },
  
  warn: function(message, data = null) {
    if (this.enabled) {
      console.warn(`[I18N] ${message}`, data || '');
    }
  }
};

// Inicialización del módulo
document.addEventListener('DOMContentLoaded', function() {
  const currentLang = getCurrentLanguage();
  I18N_DEBUG.log(`Idioma detectado: ${currentLang}`);
  
  // Agregar clase CSS al body para estilos específicos de idioma si es necesario
  document.body.classList.add(`lang-${currentLang}`);
});

// Exportar todas las funciones para uso en otros módulos
export default {
  normalizeOperationType,
  normalizeConstraintOperator,
  normalizeSolutionMethod,
  normalizePayload,
  getCurrentLanguage,
  needsNormalization,
  translateTerm,
  I18N_DEBUG
};
