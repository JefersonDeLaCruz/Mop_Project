

document.addEventListener("DOMContentLoaded", () => {
    const metodo = document.getElementById("metodo").value.trim()
    if (metodo !== "Simplex") {
        console.log("me fui de simplex")
        return;
    }
    console.log("se ejecuto simplex")
  document.getElementById("formulario").addEventListener("submit", async (e) => {
    e.preventDefault();

    const tipoOperacion = document.getElementById("tipoOperacion").value;
    const funcionObjetivo = document.getElementById("funcionObjetivo").value;
    const numeroVariables = parseInt(document.getElementById("numeroVariables").value);
    const restricciones = [];
    const wrapper = document.getElementById("resWrapper");

    Array.from(wrapper.children).forEach((div, index) => {
      const expr = div.querySelector(`[name^="restriccion_"]`).value;
      const op = div.querySelector(`[name^="operadorRestriccion_"]`).value;
      const val = div.querySelector(`[name^="valorRes_"]`).value;
      restricciones.push({ expr, op, val });
    });

    const payload = { tipoOperacion, funcionObjetivo, numeroVariables, restricciones };
    console.log("payload", payload)
    try {
      const response = await fetch("/resolver_simplex_pasos", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (data.status === "ok") {
        mostrarIteraciones(data.pasos);
      } else {
        alert(data.mensaje);
      }

    } catch (err) {
      console.error("Error:", err); //LINEA 44 AQUI <----
    }
  });
});

function mostrarIteraciones(pasos) {
  const contenedor = document.getElementById("resultados");
  contenedor.innerHTML = "";

  pasos.forEach(paso => {
    const div = document.createElement("div");
    div.innerHTML = `<h4>Iteración ${paso.iteracion}</h4>`;
    if (paso.pivote_col !== null) {
      div.innerHTML += `<p>Pivote columna: ${paso.pivote_col + 1}, fila: ${paso.pivote_fila + 1}</p>`;
    }
    const tabla = document.createElement("table");
    tabla.classList.add("table", "table-bordered");
    paso.tabla.forEach(fila => {
      const tr = document.createElement("tr");
      fila.forEach(celda => {
        const td = document.createElement("td");
        td.textContent = parseFloat(celda).toFixed(2);
        tr.appendChild(td);
      });
      tabla.appendChild(tr);
    });
    div.appendChild(tabla);
    contenedor.appendChild(div);
  });
}
