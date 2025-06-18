//aqui me voy a auxiliar para obtener la infor de los inputs
//const notyf = new Notyf();

// notyf.error({
//           message: `Debe haber al menos ${MIN_RESTRICCIONES} restricciones`,
//           duration: 1500,
//           icon: false,
//           className: "alert alert-error alert-outline",
//           position: {
//             x: "right",
//             y: "top"
//           },
//           background: "inherit"
//         });
const alerta = new Notyf({
  duration: 2000,
  position: {
    x: "right",
    y: "top",
  },
  dismissible: false,
  types: [
    {
      type: "warning",
      background: "inherit",
    },
    {
      type: "error",
      background: "inherit",
    },
  ],
});

console.log("hola index");

const input = document.getElementById("numeroVariables");
const wrapper = document.getElementById("var_badge-wrapper");
const btnAdd = document.getElementById("btnAdd");
const btnRemove = document.getElementById("btnRemove");

//para la parte de restricciones
const resWrapper = document.getElementById("resWrapper");
const addResBtn = document.getElementById("addResBtn");
const MAX_RESTRICCIONES = 8;
const MIN_RESTRICCIONES = 2;

// Función para actualizar los badges
function actualizarBadges(cantidad) {
  wrapper.innerHTML = ""; // Limpiar todo
  for (let i = 1; i <= cantidad; i++) {
    const badge = document.createElement("div");
    badge.className = "badge badge-secondary badge-lg";
    badge.textContent = `x${subIndice(i)}`;
    wrapper.appendChild(badge);
  }
}

// Función para convertir a subíndice Unicode (₁, ₂, ₃, ...)
function subIndice(num) {
  const mapa = ["₀", "₁", "₂", "₃", "₄", "₅", "₆", "₇", "₈", "₉"];
  return num
    .toString()
    .split("")
    .map((d) => mapa[d])
    .join("");
}

// Manejar botón +
btnAdd.addEventListener("click", () => {
  let valor = parseInt(input.value);
  if (valor < 10) {
    valor++;
    input.value = valor;
    actualizarBadges(valor);
  } else {
    alerta.open({
      type: "warning",
      message: `Solo se permiten hasta 10 variables de decision`,
      className: "alert alert-warning alert-outline",
    });
  }
});

// Manejar botón -
btnRemove.addEventListener("click", () => {
  let valor = parseInt(input.value);
  if (valor > 2) {
    valor--;
    input.value = valor;
    actualizarBadges(valor);
  } else {
    alerta.open({
      type: "warning",
      message: `Debe haber al menos 2 variables de decision`,
      className: "alert alert-warning alert-outline",
    });
  }
});

// Cambios en el input manualmente
input.addEventListener("input", () => {
  let valor = parseInt(input.value);
  if (isNaN(valor)) valor = 2;
  if (valor < 2) valor = 2;
  if (valor > 10) valor = 10;
  input.value = valor;
  actualizarBadges(valor);
});

// Crear una restricción (con número de orden)
function crearRestriccion(numero) {
  const div = document.createElement("div");
  div.className = "flex gap-2 items-center p-3 bg-base-200 rounded-lg";

  div.innerHTML = `
      <input name="restriccion_${numero}" id="restriccion_${numero}" type="text" placeholder="ej: x1 + x2" class="input input-sm input-bordered flex-1" />
      <select name="operadorRestriccion_${numero}" id="operadorRestriccion_${numero}" class="select select-sm select-bordered">
        <option>≤</option>
        <option>≥</option>
        <option>=</option>
      </select>
      <input name="valorRes_${numero}" id="valorRes_${numero}" type="number" placeholder="valor" required class="input input-sm input-bordered w-20" />
      <span class="btn btn-sm btn-error btn-outline btnEliminar">
        <i class="fas fa-trash"></i>
      </span>
    `;

  // Agregar evento al botón eliminar
  div.querySelector(".btnEliminar").addEventListener("click", () => {
    if (resWrapper.children.length > MIN_RESTRICCIONES) {
      div.remove();
      actualizarNombres();
    } else {
      //   alert(`Debe haber al menos ${MIN_RESTRICCIONES} restricciones`);

      // alerta.warning({
      //   message: `Debe haber al menos ${MIN_RESTRICCIONES} restricciones`,
      //   className: "alert alert-warning alert-outline"
      // })

      alerta.open({
        type: "warning",
        message: `Debe haber al menos ${MIN_RESTRICCIONES} restricciones`,
        className: "alert alert-warning alert-outline",
      });

      //
    }
  });

  return div;
}

// Agregar restricción
addResBtn.addEventListener("click", () => {
  const cantidadActual = resWrapper.children.length;
  if (cantidadActual < MAX_RESTRICCIONES) {
    const nueva = crearRestriccion(cantidadActual + 1);
    resWrapper.appendChild(nueva);
  } else {
    // alert(`Solo se permiten hasta ${MAX_RESTRICCIONES} restricciones`);
    alerta.open({
      type: "warning",
      message: `Solo se permiten hasta ${MAX_RESTRICCIONES} restricciones`,
      className: "alert alert-warning alert-outline",
    });
  }
});

// Renombrar todos los campos para que mantengan el orden correcto
function actualizarNombres() {
  Array.from(resWrapper.children).forEach((div, index) => {
    const i = index + 1;
    div.querySelector(`[type="text"]`).name = `restriccion_${i}`;
    div.querySelector(`[type="text"]`).id = `restriccion_${i}`;

    div.querySelector("select").name = `operadorRestriccion_${i}`;
    div.querySelector("select").id = `operadorRestriccion_${i}`;

    div.querySelector(`[type="number"]`).name = `valorRes_${i}`;
    div.querySelector(`[type="number"]`).id = `valorRes_${i}`;
  });
}

// Inicializar con 2 restricciones mínimas
for (let i = 1; i <= MIN_RESTRICCIONES; i++) {
  resWrapper.appendChild(crearRestriccion(i));
}

document.addEventListener("DOMContentLoaded", () => {
  const metodo_ = document.getElementById("metodo").value.trim()
  if (metodo === "Simplex") {
    console.log("me fui de linprog")
    return;
  }

  console.log("se ejecuto lingprog")
  document
    .getElementById("formulario")
    .addEventListener("submit", async (e) => {
      e.preventDefault(); // Prevenir el envío tradicional del form

      const tipoOperacion = document.getElementById("tipoOperacion").value;
      const funcionObjetivo = document.getElementById("funcionObjetivo").value;
      const numeroVariables = parseInt(
        document.getElementById("numeroVariables").value
      );

      const restricciones = [];
      const wrapper = document.getElementById("resWrapper");

      Array.from(wrapper.children).forEach((div, index) => {
        const expr = div.querySelector(`[name^="restriccion_"]`).value;
        const op = div.querySelector(`[name^="operadorRestriccion_"]`).value;
        const val = div.querySelector(`[name^="valorRes_"]`).value;

        restricciones.push({
          expr: expr,
          op: op,
          val: val,
        });
      });

      const payload = {
        tipoOperacion,
        funcionObjetivo,
        numeroVariables,
        restricciones,
      };

      try {
        const response = await fetch("/resolver", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        });

        const data = await response.json();

        mostrarSolucion(data);

        // if (data.resultado.graficable) {
        //   generarGrafica(
            
        //     data.resultado.funcion_objetivo,
        //     data.resultado.restricciones
        //   );
        // }
        // Mostrar resultado (esto depende de cómo lo querés renderizar)
        // console.log("Resultado:", data);
        // // ejemplo:
        // document.getElementById("resultado").innerText =
        //   data.resultado || "Sin solución";
      } catch (err) {
        console.error("Error al resolver:", err);
      }
    });
});

// Mostrar solución en el DOM
function mostrarSolucion(data) {
  const solucion = data.resultado;

  // Elementos DOM
  const valorOptimoEl = document.getElementById("valorOptimo");
  const estadoSolucionEl = document.getElementById("estadoSolucion");
  const tablaVariablesEl = document.getElementById("tablaVariables");
  const contenedorSolucion = document.getElementById("solution-content");

  // Rellenar valores
  valorOptimoEl.textContent = solucion.optimo.toFixed(2);
  estadoSolucionEl.textContent =
    solucion.status === "ok" ? "Óptimo" : solucion.status;

  // Limpiar tabla
  tablaVariablesEl.innerHTML = "";

  // Agregar variables
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

  // Mostrar la sección de solución
  contenedorSolucion.classList.remove("hidden");

  // Opcional: ocultar el estado inicial
  document
    .querySelector("#solution-content")
    .previousElementSibling?.classList.add("hidden");
}

