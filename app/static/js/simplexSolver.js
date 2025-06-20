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

  document.getElementById("valorOptimo").textContent = solucion.optimo.toFixed(2);
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

  solucion.iteraciones.forEach((iteracion, index) => {
    const divIteracion = document.createElement("div");
    divIteracion.classList.add(
      "mb-6",
      "p-4",
      "rounded-xl",
      "border",
      "shadow-md",
      "bg-base-100",
      "text-base-content"
    );

    const titulo = document.createElement("h3");
    titulo.classList.add("font-bold", "text-lg", "mb-4", "text-primary");
    titulo.textContent = `Iteración ${index + 1}`;
    divIteracion.appendChild(titulo);

    const tabla = document.createElement("table");
    tabla.classList.add("table", "table-sm", "w-full", "overflow-x-auto", "border-collapse", "text-center");

    const thead = document.createElement("thead");
    const encabezados = ["VB", ...iteracion.encabezados];
    thead.innerHTML = `<tr>${encabezados
      .map(h => `<th class="bg-base-200 text-base-content px-2 py-1 border">${h}</th>`)
      .join("")}</tr>`;
    tabla.appendChild(thead);

    const tbody = document.createElement("tbody");
    iteracion.filas.forEach((fila, i) => {
      const tr = document.createElement("tr");
      const vb = iteracion.variables_basicas?.[i] || (i === iteracion.filas.length - 1 ? "Z" : "");
      const filaHTML = [
        `<td class="border px-2 py-1 font-bold">${vb}</td>`,
        ...fila.map(celda => `<td class="border px-2 py-1">${celda}</td>`),
      ];
      tr.innerHTML = filaHTML.join("");
      tbody.appendChild(tr);
    });
    tabla.appendChild(tbody);
    divIteracion.appendChild(tabla);

    if (iteracion.detalles) {
      const d = iteracion.detalles;
      const detallesDiv = document.createElement("div");
      detallesDiv.classList.add("mt-4", "text-sm", "bg-base-200", "p-3", "rounded", "text-left");

      const razonesHTML = d.fila_pivote.razones.map(r =>
        `<li>Fila ${r.fila}: RHS = ${r.rhs}, coef = ${r.coef_pivote} → razón = ${r.razon}</li>`
      ).join("");

      const transformacionesHTML = d.transformaciones.map(t =>
        `<li>
          Fila ${t.fila}: 
          <br>↳ <strong>original:</strong> [${t.original.join(", ")}] 
          <br>↳ <strong>factor:</strong> ${t.factor}
          <br>↳ <strong>explicación:</strong> ${t.explicacion}
          <br>↳ <strong>resultado:</strong> [${t.resultado.join(", ")}]
        </li>`
      ).join("");

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

  document.getElementById("solution-content").classList.remove("hidden");
  document.querySelector("#solution-content").previousElementSibling?.classList.add("hidden");
}
