// solverClient.js

// Función para enviar los datos al backend
export async function resolverProblema(payload) {
  try {
    const response = await fetch("/resolver", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    const data = await response.json();
    return data;
  } catch (err) {
    console.error("Error al resolver:", err);
    throw err;
  }
}

// Función para mostrar la solución en el DOM
export function mostrarSolucion(data) {
  const solucion = data.resultado;

  const valorOptimoEl = document.getElementById("valorOptimo");
  const estadoSolucionEl = document.getElementById("estadoSolucion");
  const tablaVariablesEl = document.getElementById("tablaVariables");
  const contenedorSolucion = document.getElementById("solution-content");

  valorOptimoEl.textContent = solucion.optimo.toFixed(2);
  estadoSolucionEl.textContent =
    solucion.status === "ok" ? "Óptimo" : solucion.status;

  tablaVariablesEl.innerHTML = "";

  solucion.valores.forEach((valor, i) => {
    const tr = document.createElement("tr");

    const tdVar = document.createElement("td");
    tdVar.textContent = `x${i + 1}`;

    const tdVal = document.createElement("td");
    tdVal.textContent = valor.toFixed(2);

    tr.appendChild(tdVar);
    tr.appendChild(tdVal);
    tablaVariablesEl.appendChild(tr);
  });

  contenedorSolucion.classList.remove("hidden");
  document.querySelector("#solution-content").previousElementSibling?.classList.add("hidden");
}
