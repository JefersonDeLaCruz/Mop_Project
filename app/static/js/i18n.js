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
    // Términos básicos
    'Maximizar': 'Maximize',
    'Minimizar': 'Minimize',
    'variable': 'variable',
    'restricción': 'constraint',
    'objetivo': 'objective',
    'solución': 'solution',
    'óptimo': 'optimal',
    'no factible': 'infeasible',
    'no acotado': 'unbounded',
    
    // Simplex Solver específico
    'Método Utilizado: Simplex Clásico': 'Method Used: Classic Simplex',
    'Planteamiento del problema': 'Problem Statement',
    'Tipo': 'Type',
    'Función objetivo': 'Objective Function',
    'Restricciones': 'Constraints',
    'Modelo estándar': 'Standard Model',
    'Restricciones de no negatividad': 'Non-negativity Constraints',
    'Construcción del Modelo Estándar': 'Standard Model Construction',
    'Pasos de transformación': 'Transformation Steps',
    'Variables originales': 'Original variables',
    'Se mantienen tal como están en el problema': 'Are kept as they are in the problem',
    'Variables de holgura (s)': 'Slack variables (s)',
    'Se agregan para restricciones ≤ (coeficiente +1)': 'Are added for ≤ constraints (coefficient +1)',
    'Variables de exceso (H)': 'Surplus variables (H)',
    'Se agregan para restricciones ≥ (coeficiente -1)': 'Are added for ≥ constraints (coefficient -1)',
    'Variables artificiales (a)': 'Artificial variables (a)',
    'Se agregan para restricciones ≥ y = (coeficiente +1)': 'Are added for ≥ and = constraints (coefficient +1)',
    'Se modifica para incluir penalización M a variables artificiales': 'Is modified to include M penalty for artificial variables',
    'Objetivo': 'Objective',
    'Convertir el problema a la forma estándar para poder aplicar el algoritmo simplex': 'Convert the problem to standard form to apply the simplex algorithm',
    
    // Iteraciones
    'Iteración': 'Iteration',
    'Criterio de Optimalidad': 'Optimality Criterion',
    'Se revisa la fila Z en busca de coeficientes negativos': 'The Z-row is checked for negative coefficients',
    'Si hay coeficientes negativos, la solución actual NO es óptima': 'If there are negative coefficients, the current solution is NOT optimal',
    'Se selecciona la variable con el coeficiente más negativo para entrar a la base': 'The variable with the most negative coefficient is selected to enter the basis',
    'Si todos los coeficientes son no negativos, se ha alcanzado la solución óptima': 'If all coefficients are non-negative, the optimal solution has been reached',
    
    // Leyenda de colores
    'Leyenda de colores': 'Color Legend',
    'Elemento pivote': 'Pivot element',
    'Fila pivote': 'Pivot row',
    'sale': 'exits',
    'Columna pivote': 'Pivot column',
    'entra': 'enters',
    
    // Análisis de iteración
    'Análisis de la Iteración': 'Iteration Analysis',
    'En esta iteración se realizan los siguientes pasos': 'In this iteration the following steps are performed',
    'Verificar optimalidad': 'Check optimality',
    'Revisar si existen coeficientes negativos en la fila Z': 'Check if there are negative coefficients in the Z-row',
    'Seleccionar variable entrante': 'Select entering variable',
    'Elegir la variable con el coeficiente más negativo': 'Choose the variable with the most negative coefficient',
    'Seleccionar variable saliente': 'Select exiting variable',
    'Aplicar la prueba de la razón mínima': 'Apply the minimum ratio test',
    'Realizar pivoteo': 'Perform pivoting',
    'Normalizar fila pivote y transformar las demás filas': 'Normalize pivot row and transform other rows',
    'Actualizar base': 'Update basis',
    'Cambiar la variable básica en la posición correspondiente': 'Change the basic variable in the corresponding position',
    
    // Detalles del pivoteo
    'Detalles del Pivoteo': 'Pivoting Details',
    'Variable Entrante': 'Entering Variable',
    'Mejora la función objetivo': 'Improves the objective function',
    'Variable Saliente': 'Exiting Variable',
    'Abandona la base': 'Leaves the basis',
    'Punto de intersección': 'Intersection point',
    
    // Pasos detallados
    'Paso 1: Selección de la Variable Entrante (Columna Pivote)': 'Step 1: Entering Variable Selection (Pivot Column)',
    'Criterio': 'Criterion',
    'Se busca el coeficiente más negativo en la fila Z': 'The most negative coefficient in the Z-row is sought',
    'Justificación matemática': 'Mathematical justification',
    'Un coeficiente negativo en la fila Z indica que incrementar esa variable mejorará el valor de la función objetivo': 'A negative coefficient in the Z-row indicates that increasing that variable will improve the objective function value',
    'Resultado': 'Result',
    'Nota': 'Note',
    'Si no hay coeficientes negativos, la solución actual es óptima': 'If there are no negative coefficients, the current solution is optimal',
    
    'Paso 2: Prueba de la Razón Mínima (Selección de Variable Saliente)': 'Step 2: Minimum Ratio Test (Exiting Variable Selection)',
    'Determinar cuál variable básica debe salir de la base para mantener la factibilidad': 'Determine which basic variable should exit the basis to maintain feasibility',
    'Fórmula': 'Formula',
    'Razón = bj / Coeficiente de la columna pivote (solo si coeficiente > 0)': 'Ratio = bj / Pivot column coefficient (only if coefficient > 0)',
    'Se selecciona la fila con la menor razón positiva': 'The row with the smallest positive ratio is selected',
    'Variable Básica': 'Basic Variable',
    'Coef. Pivote': 'Pivot Coef.',
    'Razón': 'Ratio',
    'Factible': 'Feasible',
    'Selección': 'Selection',
    'Sí': 'Yes',
    'No': 'No',
    'Seleccionada': 'Selected',
    'Interpretación': 'Interpretation',
    'La variable básica seleccionada será la primera en alcanzar cero cuando se incremente la variable entrante, garantizando que no se violen las restricciones de no negatividad': 'The selected basic variable will be the first to reach zero when the entering variable is increased, ensuring that non-negativity constraints are not violated',
    
    'Paso 3: Normalización de la Fila Pivote': 'Step 3: Pivot Row Normalization',
    'Convertir el elemento pivote en 1 dividiendo toda la fila por su valor': 'Convert the pivot element to 1 by dividing the entire row by its value',
    'Operación': 'Operation',
    'Nueva_Fila_Pivote = Fila_Pivote ÷ Elemento_Pivote': 'New_Pivot_Row = Pivot_Row ÷ Pivot_Element',
    'Variable': 'Variable',
    'Valor Original': 'Original Value',
    'Nuevo Valor': 'New Value',
    'Verificación': 'Verification',
    'El elemento pivote ahora tiene valor 1, lo que permite eliminar la variable correspondiente de las otras ecuaciones': 'The pivot element now has value 1, which allows eliminating the corresponding variable from other equations',
    
    'Paso 4: Eliminación Gaussiana (Transformación de Otras Filas)': 'Step 4: Gaussian Elimination (Other Rows Transformation)',
    'Hacer cero todos los elementos de la columna pivote excepto el elemento normalizado': 'Make zero all elements in the pivot column except the normalized element',
    'Nueva_Fila_i = Fila_i - (Elemento_Columna_Pivote_i × Fila_Pivote_Normalizada)': 'New_Row_i = Row_i - (Pivot_Column_Element_i × Normalized_Pivot_Row)',
    'Para cada fila i ≠ fila pivote': 'For each row i ≠ pivot row',
    'Transformación de la Fila': 'Row Transformation',
    'Op': 'Op',
    'Factor × Pivote': 'Factor × Pivot',
    'Ahora la columna de la variable entrante tiene 1 en la posición de la variable básica y 0 en todas las demás posiciones': 'Now the entering variable column has 1 in the basic variable position and 0 in all other positions',
    
    'Paso 5: Actualización de la Base': 'Step 5: Basis Update',
    'Esta variable deja de ser básica y se vuelve no básica (valor = 0)': 'This variable stops being basic and becomes non-basic (value = 0)',
    'Esta variable se vuelve básica y tendrá un valor positivo': 'This variable becomes basic and will have a positive value',
    'La nueva base está formada por las variables que tienen exactamente un coeficiente 1 en su columna y 0 en todas las demás filas': 'The new basis is formed by variables that have exactly one coefficient 1 in their column and 0 in all other rows',
    
    // Conclusión
    'Conclusión e interpretación': 'Conclusion and Interpretation',
    'Se alcanzó una solución óptima con un valor de': 'An optimal solution was reached with a value of',
    'Las variables que contribuyen a este óptimo son': 'The variables that contribute to this optimum are',
    'ninguna (todas son 0)': 'none (all are 0)',
    'Esto significa que, bajo las restricciones dadas, esta combinación de variables maximiza el valor de la función objetivo': 'This means that, under the given constraints, this combination of variables maximizes the objective function value'
  };
  
  return spanishToEnglish[term] || term;
}

/**
 * Función auxiliar para traducir texto con interpolación de variables
 * @param {string} text - Texto a traducir
 * @param {Object} variables - Variables para interpolar en el texto
 * @returns {string} - Texto traducido
 */
export function t(text, variables = {}) {
  let translatedText = translateTerm(text);
  
  // Interpolar variables si se proporcionan
  Object.keys(variables).forEach(key => {
    const placeholder = `{${key}}`;
    if (translatedText.includes(placeholder)) {
      translatedText = translatedText.replace(new RegExp(`\\{${key}\\}`, 'g'), variables[key]);
    }
  });
  
  return translatedText;
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
  t,
  I18N_DEBUG
};
