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

export async function resolverSimplexGeneral(payload) {
  try {
    const response = await fetch("/resolver-simplex-general", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    const data = await response.json();

    console.log("resultado m g", data)
    
    // ✅ Manejar errores HTTP
    if (!response.ok) {
      throw new Error(data.error || `Error del servidor: ${response.status}`);
    }
    
    return data;
  } catch (error) {
    console.error("Error al resolver con el método general:", error);
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
    titulo.textContent = `Iteración ${index + 1}`;
    divIteracion.appendChild(titulo);

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
        (celda, idx) =>
          `<td class="border px-2 py-1 ${
            idx === 0 ? "font-bold" : ""
          }">${celda}</td>`
      );//forma alternativa para evitar desbordamiento + agregando estilo a la primera cell VB

      tr.innerHTML = filaHTML.join("");
      tbody.appendChild(tr);
    });
    tabla.appendChild(tbody);
    divIteracion.appendChild(tabla);

    if (iteracion.detalles) {
      const d = iteracion.detalles;
      const detallesDiv = document.createElement("div");
      detallesDiv.classList.add(
        "mt-4",
        "text-sm",
        "bg-base-200",
        "p-3",
        "rounded",
        "text-left"
      );

      const razonesHTML = d.fila_pivote.razones
        .map(
          (r) =>
            `<li>Fila ${r.fila}: RHS = ${r.rhs}, coef = ${r.coef_pivote} → razón = ${r.razon}</li>`
        )
        .join("");

      const transformacionesHTML = d.transformaciones
        .map(
          (t) =>
            `<li>
          Fila ${t.fila}: 
          <br>↳ <strong>original:</strong> [${t.original.join(", ")}] 
          <br>↳ <strong>factor:</strong> ${t.factor}
          <br>↳ <strong>explicación:</strong> ${t.explicacion}
          <br>↳ <strong>resultado:</strong> [${t.resultado.join(", ")}]
        </li>`
        )
        .join("");

      detallesDiv.innerHTML = `
        <p><strong>Justificación de la columna pivote:</strong><br>
        ${d.columna_pivote.explicacion}</p>

        <p class="mt-2"><strong>Justificación de la fila pivote:</strong><br>
        ${d.fila_pivote.explicacion}</p>

        <p><strong>Cálculo de razones:</strong></p>
        <ul class="list-disc pl-5">${razonesHTML}</ul>

        <p class="mt-2"><strong>Normalización de la fila pivote:</strong><br>
        ${d.normalizacion.explicacion}<br>
        Fila original: [${d.normalizacion.original.join(", ")}], 
        pivote = ${d.normalizacion.pivote}, 
        resultado = [${d.normalizacion.resultado.join(", ")}]
        </p>

        <p class="mt-2"><strong>Transformaciones de otras filas:</strong></p>
        <ul class="list-disc pl-5">${transformacionesHTML}</ul>
      `;
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


export function mostrarResultadoGranM(solucion) {
  // Comprobaciones para evitar errores
  if (!solucion) {
    console.error("No se recibieron datos de solución");
    return;
  }

  // Mostrar valor óptimo y estado
  document.getElementById("valorOptimo").textContent = 
    solucion.optimo.toFixed(2);
  
  document.getElementById("estadoSolucion").textContent = 
    solucion.status === "ok" ? "Óptimo" : solucion.status;

  // Tabla de variables
  const tablaVariables = document.getElementById("tablaVariables");
  tablaVariables.innerHTML = "";
  solucion.valores.forEach((valor, i) => {
    const fila = document.createElement("tr");
    fila.innerHTML = `<td>x${i + 1}</td><td>${valor.toFixed(2)}</td>`;
    tablaVariables.appendChild(fila);
  });

  const resultadosEl = document.getElementById("resultados");
  resultadosEl.innerHTML = "";

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
    titulo.textContent = `Iteración ${index + 1}`;
    divIteracion.appendChild(titulo);

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
    const encabezados = iteracion.encabezados;
    thead.innerHTML = `<tr>${encabezados
      .map(
        (h) =>
          `<th class="bg-base-200 text-base-content px-2 py-1 border">${h}</th>`
      )
      .join("")}</tr>`;
    tabla.appendChild(thead);

    const tbody = document.createElement("tbody");
    iteracion.filas.forEach((fila) => {
      const tr = document.createElement("tr");
      const filaHTML = fila.map(
        (celda, idx) =>
          `<td class="border px-2 py-1 ${
            idx === 0 ? "font-bold" : ""
          }">${celda}</td>`
      );
      tr.innerHTML = filaHTML.join("");
      tbody.appendChild(tr);
    });
    tabla.appendChild(tbody);
    divIteracion.appendChild(tabla);

    if (iteracion.detalles) {
      const d = iteracion.detalles;
      const detallesDiv = document.createElement("div");
      detallesDiv.classList.add(
        "mt-4",
        "text-sm",
        "bg-base-200",
        "p-3",
        "rounded",
        "text-left"
      );

      const razonesHTML = d.fila_pivote.razones
        .map(
          (r) =>
            `<li>Fila ${r.fila}: RHS = ${r.rhs}, coef = ${r.coef_pivote} → razón = ${r.razon}</li>`
        )
        .join("");

      const transformacionesHTML = d.transformaciones
        .map(
          (t) =>
            `<li>
          Fila ${t.fila}: 
          <br>↳ <strong>original:</strong> [${t.original.join(", ")}] 
          <br>↳ <strong>factor:</strong> ${t.factor}
          <br>↳ <strong>explicación:</strong> ${t.explicacion}
          <br>↳ <strong>resultado:</strong> [${t.resultado.join(", ")}]
        </li>`
        )
        .join("");

      detallesDiv.innerHTML = `
        <p><strong>Justificación de la columna pivote:</strong><br>
        ${d.columna_pivote.explicacion}</p>

        <p class="mt-2"><strong>Justificación de la fila pivote:</strong><br>
        ${d.fila_pivote.explicacion}</p>

        <p><strong>Cálculo de razones:</strong></p>
        <ul class="list-disc pl-5">${razonesHTML}</ul>

        <p class="mt-2"><strong>Normalización de la fila pivote:</strong><br>
        ${d.normalizacion.explicacion}<br>
        Fila original: [${d.normalizacion.original.join(", ")}], 
        pivote = ${d.normalizacion.pivote}, 
        resultado = [${d.normalizacion.resultado.join(", ")}]
        </p>

        <p class="mt-2"><strong>Transformaciones de otras filas:</strong></p>
        <ul class="list-disc pl-5">${transformacionesHTML}</ul>
      `;
      divIteracion.appendChild(detallesDiv);
    }

    resultadosEl.appendChild(divIteracion);
  });

  // 🔽 Interpretación y conclusión final
  if (solucion.status === "ok") {
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
  } else if (solucion.status === "infactible") {
    const errorDiv = document.createElement("div");
    errorDiv.classList.add(
      "mb-6",
      "p-4",
      "rounded",
      "bg-error",
      "text-error-content"
    );
    errorDiv.innerHTML = `
      <h3 class="font-bold text-lg mb-2">Problema Infactible</h3>
      <p>${solucion.mensaje || "El problema no tiene solución factible"}</p>
    `;
    resultadosEl.appendChild(errorDiv);
  }

  document.getElementById("solution-content").classList.remove("hidden");
  document
    .querySelector("#solution-content")
    .previousElementSibling?.classList.add("hidden");
}