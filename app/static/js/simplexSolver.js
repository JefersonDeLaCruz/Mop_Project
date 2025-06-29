// simplexSolver.js

export async function resolverSimplex(payload) {
  try {
    const response = await fetch("/resolver-simplex", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error al resolver con Simplex:", error);
    throw error;
  }
}



export function mostrarResultadoSimplex(data) {
  const solucion = data.resultado;

  document.getElementById("valorOptimo").textContent =
    solucion.optimo.toFixed(2);
  document.getElementById("estadoSolucion").textContent =
    solucion.status === "ok" ? "Óptimo" : solucion.status;

  const tablaVariables = document.getElementById("tablaVariables");
  tablaVariables.innerHTML = "";
  solucion.valores.forEach((valor, i) => {
    const fila = document.createElement("tr");
    fila.innerHTML = `<td>x${i + 1}</td><td>${valor.toFixed(2)}</td>`;
    tablaVariables.appendChild(fila);
  });

  const resultadosEl = document.getElementById("resultados");
  resultadosEl.innerHTML = "";

  // 🔽 Agregar información del método usado
  const metodoDiv = document.createElement("div");
  metodoDiv.classList.add(
    "mb-6",
    "p-4",
    "rounded",
    "bg-primary",
    "bg-opacity-10",
    "text-primary-content",
    "border-l-4",
    "border-primary"
  );
  
  metodoDiv.innerHTML = `
    <h3 class="font-bold text-lg mb-2 text-primary">Método Utilizado: Simplex Clásico</h3>
  `;
  resultadosEl.appendChild(metodoDiv);

  // 🔽 Mostrar planteamiento del problema
  const planteamientoDiv = document.createElement("div");
  planteamientoDiv.classList.add(
    "mb-6",
    "p-4",
    "rounded",
    "bg-base-200",
    "text-base-content"
  );

  const { tipo, funcion_objetivo, restricciones } = solucion.planteamiento;
  const modelo = solucion.modelo_estandar;

  const restriccionesHTML = restricciones
    .map((r, i) => `<li>${r.expr} ${r.op} ${r.val}</li>`)
    .join("");

  const modeloRestricciones = modelo.restricciones
    .map((r) => `<li>${r}</li>`)
    .join("");
  const modeloVariables = modelo.variables.map((v) => `<li>${v}</li>`).join("");

  planteamientoDiv.innerHTML = `
    <h3 class="font-bold text-lg mb-2 text-primary">Planteamiento del problema</h3>
    <p><strong>Tipo:</strong> ${tipo}</p>
    <p><strong>Función objetivo:</strong> ${funcion_objetivo}</p>
    <p><strong>Restricciones:</strong></p>
    <ul class="list-disc pl-5">${restriccionesHTML}</ul>

    <h4 class="mt-4 font-bold text-base">Modelo estándar:</h4>
    <p><strong>Función objetivo:</strong> ${modelo.funcion_objetivo}</p>
    <p><strong>Restricciones:</strong></p>
    <ul class="list-disc pl-5">${modeloRestricciones}</ul>
    <p><strong>Restricciones de no negatividad:</strong></p>
    <ul class="list-disc pl-5">${modeloVariables}</ul>
  `;
  resultadosEl.appendChild(planteamientoDiv);

  // 🔽 Agregar detalles del modelo extendido (como en test.py)
  const modeloExtendidoDiv = document.createElement("div");
  modeloExtendidoDiv.classList.add(
    "mb-6",
    "p-4",
    "rounded",
    "bg-warning",
    "bg-opacity-10",
    "text-warning-content"
  );
  
  modeloExtendidoDiv.innerHTML = `
    <h3 class="font-bold text-lg mb-3 text-warning">Construcción del Modelo Estándar</h3>
    <div class="space-y-3">
      <div class="bg-base-100 p-3 rounded">
        <h4 class="font-bold text-base mb-2">Pasos de transformación:</h4>
        <ol class="list-decimal pl-5 text-sm space-y-1">
          <li><strong>Variables originales:</strong> Se mantienen tal como están en el problema</li>
          <li><strong>Variables de holgura (s):</strong> Se agregan para restricciones ≤ (coeficiente +1)</li>
          <li><strong>Variables de exceso (H):</strong> Se agregan para restricciones ≥ (coeficiente -1)</li>
          <li><strong>Variables artificiales (a):</strong> Se agregan para restricciones ≥ y = (coeficiente +1)</li>
          <li><strong>Función objetivo:</strong> Se modifica para incluir penalización M a variables artificiales</li>
        </ol>
      </div>
      <div class="bg-info bg-opacity-20 p-3 rounded">
        <p class="text-sm"><strong>Objetivo:</strong> Convertir el problema a la forma estándar para poder aplicar el algoritmo simplex.</p>
      </div>
    </div>
  `;
  resultadosEl.appendChild(modeloExtendidoDiv);

  // 🔽 Mostrar iteraciones
  solucion.iteraciones.forEach((iteracion, index) => {
    const divIteracion = document.createElement("div");
    divIteracion.classList.add(
      "mb-6",
      "p-4",
      "rounded-xl",
      "border",
      "shadow-md",
      "bg-base-100",
      "text-base-content",
      "overflow-x-auto"
    );

    const titulo = document.createElement("h3");
    titulo.classList.add("font-bold", "text-lg", "mb-4", "text-primary");
    titulo.textContent = `Iteración ${index}`;
    divIteracion.appendChild(titulo);

    // Agregar criterio de optimalidad antes de la tabla
    if (index > 0) { // No mostrar para la iteración 0 (tabla inicial)
      const criterioDiv = document.createElement("div");
      criterioDiv.classList.add("mb-4", "p-3", "rounded", "bg-accent", "bg-opacity-10", "text-accent-content");
      criterioDiv.innerHTML = `
        <h4 class="font-bold text-base mb-2 text-accent">Criterio de Optimalidad:</h4>
        <p class="text-sm">Se revisa la fila Z en busca de coeficientes negativos:</p>
        <ul class="list-disc pl-5 text-sm mt-2">
          <li>Si hay coeficientes negativos, la solución actual NO es óptima</li>
          <li>Se selecciona la variable con el coeficiente más negativo para entrar a la base</li>
          <li>Si todos los coeficientes son no negativos, se ha alcanzado la solución óptima</li>
        </ul>
      `;
      divIteracion.appendChild(criterioDiv);
    }

    const tabla = document.createElement("table");
    tabla.classList.add(
      "table",
      "table-sm",
      "w-full",
      "overflow-x-auto",
      "border-collapse",
      "text-center"
    );

    const thead = document.createElement("thead");
    // const encabezados = ["VB", ...iteracion.encabezados]; con esto se nmostraban dos veces la columna VB
    const encabezados = iteracion.encabezados;
    thead.innerHTML = `<tr>${encabezados
      .map(
        (h) =>
          `<th class="bg-base-200 text-base-content px-2 py-1 border">${h}</th>`
      )
      .join("")}</tr>`;
    tabla.appendChild(thead);

    const tbody = document.createElement("tbody");
    iteracion.filas.forEach((fila, i) => {
      const tr = document.createElement("tr");
      // const vb = iteracion.variables_basicas?.[i] || (i === iteracion.filas.length - 1 ? "Z" : "");
      // const filaHTML = [
      //   `<td class="border px-2 py-1 font-bold">${vb}</td>`,
      //   ...fila.map(celda => `<td class="border px-2 py-1">${celda}</td>`),
      // ];

      // const filaHTML = fila.map(celda => `<td class="border px-2 py-1">${celda}</td>`); solucion al problema de desbordamiento de filas
      const filaHTML = fila.map(
        (celda, idx) => {
          let cssClass = "border px-2 py-1";
          
          // Resaltar elemento pivote, fila pivote y columna pivote si están disponibles
          if (iteracion.pivot_info) {
            const pivotRow = iteracion.pivot_info.fila;
            const pivotCol = iteracion.pivot_info.columna;
            
            if (i === pivotRow && idx === pivotCol + 1) { // +1 porque la primera columna es VB
              cssClass += " bg-error text-error-content font-bold"; // Elemento pivote
            } else if (i === pivotRow) {
              cssClass += " bg-warning bg-opacity-30"; // Fila pivote
            } else if (idx === pivotCol + 1) {
              cssClass += " bg-warning bg-opacity-30"; // Columna pivote
            }
          }
          
          if (idx === 0) {
            cssClass += " font-bold";
          }
          
          return `<td class="${cssClass}">${celda}</td>`;
        }
      );//forma alternativa para evitar desbordamiento + agregando estilo a la primera cell VB + resaltado de pivotes

      tr.innerHTML = filaHTML.join("");
      tbody.appendChild(tr);
    });
    tabla.appendChild(tbody);
    divIteracion.appendChild(tabla);

    if (iteracion.detalles) {
      const d = iteracion.detalles;
      
      // Detalles del pivoteo con diseño mejorado
      const detallesDiv = document.createElement("div");
      detallesDiv.classList.add("mt-4", "space-y-4");

      // Encabezado de análisis de la iteración
      const analisisDiv = document.createElement("div");
      analisisDiv.classList.add("mb-6", "p-4", "rounded", "bg-base-300", "text-base-content");
      analisisDiv.innerHTML = `
        <h4 class="font-bold text-lg mb-3 text-primary">Análisis de la Iteración ${index}</h4>
        <p class="text-sm mb-2">En esta iteración se realizan los siguientes pasos:</p>
        <ol class="list-decimal pl-5 text-sm space-y-1">
          <li><strong>Verificar optimalidad:</strong> Revisar si existen coeficientes negativos en la fila Z</li>
          <li><strong>Seleccionar variable entrante:</strong> Elegir la variable con el coeficiente más negativo</li>
          <li><strong>Seleccionar variable saliente:</strong> Aplicar la prueba de la razón mínima</li>
          <li><strong>Realizar pivoteo:</strong> Normalizar fila pivote y transformar las demás filas</li>
          <li><strong>Actualizar base:</strong> Cambiar la variable básica en la posición correspondiente</li>
        </ol>
      `;

      // Identificación del pivoteo
      const pivoteoDiv = document.createElement("div");
      pivoteoDiv.classList.add("mb-6", "p-4", "rounded", "bg-info", "bg-opacity-10", "text-info-content");
      pivoteoDiv.innerHTML = `
        <h4 class="font-bold text-lg mb-3 text-info">Detalles del Pivoteo</h4>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4">
          <div class="bg-base-100 p-3 rounded">
            <p class="font-bold text-sm mb-1">Variable Entrante</p>
            <span class="badge badge-success text-lg">${d.columna_pivote.variable || 'N/A'}</span>
            <p class="text-xs mt-1">Mejora la función objetivo</p>
          </div>
          <div class="bg-base-100 p-3 rounded">
            <p class="font-bold text-sm mb-1">Variable Saliente</p>
            <span class="badge badge-error text-lg">${d.fila_pivote.variable_sale || d.fila_pivote.variable || 'Variable saliente'}</span>
            <p class="text-xs mt-1">Abandona la base</p>
          </div>
          <div class="bg-base-100 p-3 rounded">
            <p class="font-bold text-sm mb-1">Elemento Pivote</p>
            <span class="badge badge-warning text-lg">${d.normalizacion?.pivote || 'N/A'}</span>
            <p class="text-xs mt-1">Punto de intersección</p>
          </div>
        </div>
      `;

      // Justificación de la columna pivote con más detalles
      const colPivoteDiv = document.createElement("div");
      colPivoteDiv.classList.add("mb-4", "p-3", "rounded", "bg-accent", "bg-opacity-10", "text-accent-content");
      colPivoteDiv.innerHTML = `
        <h5 class="font-bold text-base mb-2 text-accent">Paso 1: Selección de la Variable Entrante (Columna Pivote)</h5>
        <div class="bg-base-100 p-3 rounded mb-3">
          <p class="text-sm mb-2"><strong>Criterio:</strong> Se busca el coeficiente más negativo en la fila Z.</p>
          <p class="text-sm mb-2"><strong>Justificación matemática:</strong> Un coeficiente negativo en la fila Z indica que incrementar esa variable mejorará el valor de la función objetivo.</p>
          <p class="text-sm"><strong>Resultado:</strong> ${d.columna_pivote.explicacion}</p>
        </div>
        <div class="bg-warning bg-opacity-20 p-2 rounded">
          <p class="text-xs"><strong>Nota:</strong> Si no hay coeficientes negativos, la solución actual es óptima.</p>
        </div>
      `;

      // Cálculo de razones con tabla detallada y explicaciones matemáticas
      const razonesDiv = document.createElement("div");
      razonesDiv.classList.add("mb-4", "p-3", "rounded", "bg-warning", "bg-opacity-10", "text-warning-content");
      
      const razonesHTML = d.fila_pivote.razones
        .map((r) => {
          const esMinima = r.fila === d.fila_pivote.fila_seleccionada;
          const cssClass = esMinima ? "bg-success bg-opacity-20 font-bold" : "";
          const factibilidad = r.razon !== '∞' && r.razon >= 0;
          return `
            <tr class="${cssClass}">
              <td class="px-2 py-1 border">${r.variable_basica || `F${r.fila}`}</td>
              <td class="px-2 py-1 border">${r.rhs}</td>
              <td class="px-2 py-1 border">${r.coef_pivote}</td>
              <td class="px-2 py-1 border">${r.razon}</td>
              <td class="px-2 py-1 border">
                <span class="badge ${factibilidad ? 'badge-success' : 'badge-error'} badge-sm">
                  ${factibilidad ? 'Sí' : 'No'}
                </span>
              </td>
              <td class="px-2 py-1 border text-xs">${esMinima ? '← Seleccionada' : ''}</td>
            </tr>
          `;
        })
        .join("");

      razonesDiv.innerHTML = `
        <h5 class="font-bold text-base mb-2 text-warning">Paso 2: Prueba de la Razón Mínima (Selección de Variable Saliente)</h5>
        <div class="bg-base-100 p-3 rounded mb-3">
          <p class="text-sm mb-2"><strong>Objetivo:</strong> Determinar cuál variable básica debe salir de la base para mantener la factibilidad.</p>
          <p class="text-sm mb-2"><strong>Fórmula:</strong> Razón = bj / Coeficiente de la columna pivote (solo si coeficiente > 0)</p>
          <p class="text-sm mb-2"><strong>Criterio:</strong> Se selecciona la fila con la menor razón positiva.</p>
          <p class="text-sm">${d.fila_pivote.explicacion}</p>
        </div>
        <div class="overflow-x-auto">
          <table class="table table-sm w-full text-center text-xs border-collapse">
            <thead>
              <tr>
                <th class="bg-base-200 px-2 py-1 border">Variable Básica</th>
                <th class="bg-base-200 px-2 py-1 border">bj</th>
                <th class="bg-base-200 px-2 py-1 border">Coef. Pivote</th>
                <th class="bg-base-200 px-2 py-1 border">Razón</th>
                <th class="bg-base-200 px-2 py-1 border">Factible</th>
                <th class="bg-base-200 px-2 py-1 border">Selección</th>
              </tr>
            </thead>
            <tbody>
              ${razonesHTML}
            </tbody>
          </table>
        </div>
        <div class="bg-info bg-opacity-20 p-2 rounded mt-3">
          <p class="text-xs"><strong>Interpretación:</strong> La variable básica seleccionada será la primera en alcanzar cero cuando se incremente la variable entrante, garantizando que no se violen las restricciones de no negatividad.</p>
        </div>
      `;

      // Normalización de la fila pivote con más detalles
      const normalizacionDiv = document.createElement("div");
      normalizacionDiv.classList.add("mb-4", "p-3", "rounded", "bg-secondary", "bg-opacity-10", "text-secondary-content");
      
      if (d.normalizacion) {
        const normTablaHTML = d.normalizacion.original
          .map((val, idx) => {
            // Los encabezados están disponibles desde iteracion.encabezados
            // Excluir VB (primera columna) para obtener solo variables
            const variableHeaders = encabezados.slice(1); // Quitar VB
            const variableName = idx < variableHeaders.length ? variableHeaders[idx] : 'bj';
            return `
            <tr>
              <td class="px-2 py-1 border font-bold">${variableName}</td>
              <td class="px-2 py-1 border">${val}</td>
              <td class="px-2 py-1 border text-warning">÷</td>
              <td class="px-2 py-1 border bg-warning bg-opacity-30 font-bold">${d.normalizacion.pivote}</td>
              <td class="px-2 py-1 border text-success">=</td>
              <td class="px-2 py-1 border bg-success bg-opacity-30 font-bold">${d.normalizacion.resultado[idx]}</td>
            </tr>
          `})
          .join("");

        normalizacionDiv.innerHTML = `
          <h5 class="font-bold text-base mb-2 text-secondary">Paso 3: Normalización de la Fila Pivote</h5>
          <div class="bg-base-100 p-3 rounded mb-3">
            <p class="text-sm mb-2"><strong>Objetivo:</strong> Convertir el elemento pivote en 1 dividiendo toda la fila por su valor.</p>
            <p class="text-sm mb-2"><strong>Operación:</strong> Nueva_Fila_Pivote = Fila_Pivote ÷ Elemento_Pivote</p>
            <p class="text-sm"><strong>Resultado:</strong> ${d.normalizacion.explicacion}</p>
          </div>
          <div class="overflow-x-auto">
            <table class="table table-sm w-full text-center text-xs border-collapse">
              <thead>
                <tr>
                  <th class="bg-base-200 px-2 py-1 border">Variable</th>
                  <th class="bg-base-200 px-2 py-1 border">Valor Original</th>
                  <th class="bg-base-200 px-2 py-1 border">Operación</th>
                  <th class="bg-base-200 px-2 py-1 border">Pivote</th>
                  <th class="bg-base-200 px-2 py-1 border"></th>
                  <th class="bg-base-200 px-2 py-1 border">Nuevo Valor</th>
                </tr>
              </thead>
              <tbody>
                ${normTablaHTML}
              </tbody>
            </table>
          </div>
          <div class="bg-success bg-opacity-20 p-2 rounded mt-3">
            <p class="text-xs"><strong>Verificación:</strong> El elemento pivote ahora tiene valor 1, lo que permite eliminar la variable correspondiente de las otras ecuaciones.</p>
          </div>
        `;
      }

      // Transformaciones de otras filas con más detalles
      const transformacionesDiv = document.createElement("div");
      transformacionesDiv.classList.add("mb-4", "p-3", "rounded", "bg-primary", "bg-opacity-10", "text-primary-content");
      
      const transformacionesHTML = d.transformaciones
        .map((t) => {
          const filaTablaHTML = t.original
            .map((val, idx) => {
              const factor = t.factor;
              const pivoteVal = d.normalizacion ? d.normalizacion.resultado[idx] : 0;
              const producto = `${factor} × ${pivoteVal}`;
              const operacion = factor >= 0 ? '-' : '+';
              const factorAbs = Math.abs(factor);
              // Usar nombres reales de variables
              const variableHeaders = encabezados.slice(1); // Quitar VB
              const variableName = idx < variableHeaders.length ? variableHeaders[idx] : 'bj';
              return `
                <tr>
                  <td class="px-1 py-1 border font-bold">${variableName}</td>
                  <td class="px-1 py-1 border">${val}</td>
                  <td class="px-1 py-1 border text-warning">${operacion}</td>
                  <td class="px-1 py-1 border text-xs">(${factorAbs} × ${pivoteVal})</td>
                  <td class="px-1 py-1 border text-success">=</td>
                  <td class="px-1 py-1 border bg-success bg-opacity-30 font-bold">${t.resultado[idx]}</td>
                </tr>
              `;
            })
            .join("");

          return `
            <div class="mb-4 p-3 bg-base-100 rounded border-l-4 border-primary">
              <h6 class="font-bold text-sm mb-2 text-primary">Transformación de la Fila ${t.fila}:</h6>
              <p class="text-xs mb-2">${t.explicacion}</p>
              <div class="overflow-x-auto">
                <table class="table table-sm w-full text-center text-xs border-collapse">
                  <thead>
                    <tr>
                      <th class="bg-base-200 px-1 py-1 border">Variable</th>
                      <th class="bg-base-200 px-1 py-1 border">Valor Original</th>
                      <th class="bg-base-200 px-1 py-1 border">Op</th>
                      <th class="bg-base-200 px-1 py-1 border">Factor × Pivote</th>
                      <th class="bg-base-200 px-1 py-1 border"></th>
                      <th class="bg-base-200 px-1 py-1 border">Nuevo Valor</th>
                    </tr>
                  </thead>
                  <tbody>
                    ${filaTablaHTML}
                  </tbody>
                </table>
              </div>
            </div>
          `;
        })
        .join("");

      transformacionesDiv.innerHTML = `
        <h5 class="font-bold text-base mb-3 text-primary">Paso 4: Eliminación Gaussiana (Transformación de Otras Filas)</h5>
        <div class="bg-base-100 p-3 rounded mb-3">
          <p class="text-sm mb-2"><strong>Objetivo:</strong> Hacer cero todos los elementos de la columna pivote excepto el elemento normalizado.</p>
          <p class="text-sm mb-2"><strong>Fórmula:</strong> Nueva_Fila_i = Fila_i - (Elemento_Columna_Pivote_i × Fila_Pivote_Normalizada)</p>
          <p class="text-sm">Para cada fila i ≠ fila pivote:</p>
        </div>
        ${transformacionesHTML}
        <div class="bg-info bg-opacity-20 p-2 rounded mt-3">
          <p class="text-xs"><strong>Resultado:</strong> Ahora la columna de la variable entrante tiene 1 en la posición de la variable básica y 0 en todas las demás posiciones.</p>
        </div>
      `;

      // Actualización de la base con más detalle
      const baseDiv = document.createElement("div");
      baseDiv.classList.add("mb-4", "p-3", "rounded", "bg-base-300", "text-base-content");
      baseDiv.innerHTML = `
        <h5 class="font-bold text-base mb-3">Paso 5: Actualización de la Base</h5>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="bg-error bg-opacity-10 p-3 rounded">
            <p class="font-bold text-sm mb-1 text-error">Variable Saliente:</p>
            <span class="badge badge-error">${d.fila_pivote.variable_sale || 'Variable saliente'}</span>
            <p class="text-xs mt-2">Esta variable deja de ser básica y se vuelve no básica (valor = 0)</p>
          </div>
          <div class="bg-success bg-opacity-10 p-3 rounded">
            <p class="font-bold text-sm mb-1 text-success">Variable Entrante:</p>
            <span class="badge badge-success">${d.columna_pivote.variable || 'Variable entrante'}</span>
            <p class="text-xs mt-2">Esta variable se vuelve básica y tendrá un valor positivo</p>
          </div>
        </div>
        <div class="bg-info bg-opacity-20 p-2 rounded mt-3">
          <p class="text-xs"><strong>Resultado:</strong> La nueva base está formada por las variables que tienen exactamente un coeficiente 1 en su columna y 0 en todas las demás filas.</p>
        </div>
      `;

      // Ensamblar todos los elementos con encabezado
      detallesDiv.appendChild(analisisDiv);
      detallesDiv.appendChild(pivoteoDiv);
      detallesDiv.appendChild(colPivoteDiv);
      detallesDiv.appendChild(razonesDiv);
      if (d.normalizacion) {
        detallesDiv.appendChild(normalizacionDiv);
      }
      detallesDiv.appendChild(transformacionesDiv);
      detallesDiv.appendChild(baseDiv);
      
      divIteracion.appendChild(detallesDiv);
    }

    resultadosEl.appendChild(divIteracion);
  });
  // 🔽 Interpretación y conclusión final
  const interpretacionDiv = document.createElement("div");
  interpretacionDiv.classList.add(
    "mb-6",
    "p-4",
    "rounded",
    "bg-success",
    "bg-opacity-10",
    "text-success-content",
    "shadow"
  );

  const valorZ = solucion.optimo.toFixed(2);
  const variablesActivas = solucion.valores
    .map((val, i) => ({ nombre: `x${i + 1}`, valor: val }))
    .filter((v) => v.valor > 0)
    .map((v) => `${v.nombre} = ${v.valor.toFixed(2)}`)
    .join(", ");

  interpretacionDiv.innerHTML = `
    <h3 class="font-bold text-lg mb-2 text-success">Conclusión e interpretación</h3>
    <p>Se alcanzó una solución óptima con un valor de <strong>Z = ${valorZ}</strong>.</p>
    <p>Las variables que contribuyen a este óptimo son: <strong>${
      variablesActivas || "ninguna (todas son 0)"
    }</strong>.</p>
    <p class="mt-2">
      Esto significa que, bajo las restricciones dadas, esta combinación de variables maximiza el valor de la función objetivo.
    </p>
  `;

  resultadosEl.appendChild(interpretacionDiv);
  document.getElementById("solution-content").classList.remove("hidden");
  document
    .querySelector("#solution-content")
    .previousElementSibling?.classList.add("hidden");
}


