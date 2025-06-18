// simplexSolver.js

// Enviar el problema al backend para resolverlo con el método Simplex
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

// Mostrar la solución del método Simplex (óptimo + variables + iteraciones)
export function mostrarResultadoSimplex(data) {
  const solucion = data.resultado;

  // Mostrar valor óptimo
  document.getElementById("valorOptimo").textContent = solucion.optimo.toFixed(2);
  document.getElementById("estadoSolucion").textContent =
    solucion.status === "ok" ? "Óptimo" : solucion.status;

  // Mostrar valores de variables
  const tablaVariables = document.getElementById("tablaVariables");
  tablaVariables.innerHTML = "";
  solucion.valores.forEach((valor, i) => {
    const fila = document.createElement("tr");
    fila.innerHTML = `<td>x${i + 1}</td><td>${valor.toFixed(2)}</td>`;
    tablaVariables.appendChild(fila);
  });

  // Mostrar pasos iterativos (tablas del método Simplex)
  const resultadosEl = document.getElementById("resultados");
  resultadosEl.innerHTML = ""; // Limpiar

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
    tabla.classList.add(
      "table",
      "table-sm",
      "w-full",
      "overflow-x-auto",
      "border-collapse",
      "text-center"
    );

    const thead = document.createElement("thead");
    thead.innerHTML = `<tr>${iteracion.encabezados.map(h => `<th class="bg-base-200 text-base-content px-2 py-1 border">${h}</th>`).join("")}</tr>`;
    tabla.appendChild(thead);

    const tbody = document.createElement("tbody");
    iteracion.filas.forEach(fila => {
      const tr = document.createElement("tr");
      tr.innerHTML = fila.map(celda => `<td class="border px-2 py-1">${celda}</td>`).join("");
      tbody.appendChild(tr);
    });
    tabla.appendChild(tbody);

    divIteracion.appendChild(tabla);
    resultadosEl.appendChild(divIteracion);
  });

  // Mostrar sección de solución
  document.getElementById("solution-content").classList.remove("hidden");
  document.querySelector("#solution-content").previousElementSibling?.classList.add("hidden");
}

