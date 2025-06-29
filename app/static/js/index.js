//aqui me voy a auxiliar para obtener la infor de los inputs
import { resolverProblema, mostrarSolucion } from "./solver.js";
import {
  resolverSimplex,
  mostrarResultadoSimplex,
  resolverSimplexGeneral,
  mostrarResultadoGranM,
} from "./simplexSolver.js";

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
// btnAdd.addEventListener("click", () => {
//   let valor = parseInt(input.value);
//   if (valor < 10) {
//     valor++;
//     input.value = valor;
//     actualizarBadges(valor);
//   } else {
//     alerta.open({
//       type: "warning",
//       message: `Solo se permiten hasta 10 variables de decision`,
//       className: "alert alert-warning",
//     });
//   }
// });

// Manejar botón -
// btnRemove.addEventListener("click", () => {
//   let valor = parseInt(input.value);
//   if (valor > 2) {
//     valor--;
//     input.value = valor;
//     actualizarBadges(valor);
//   } else {
//     alerta.open({
//       type: "warning",
//       message: `Debe haber al menos 2 variables de decision`,
//       className: "alert alert-warning",
//     });
//   }
// });

// Cambios en el input manualmente
// input.addEventListener("input", () => {
//   let valor = parseInt(input.value);
//   if (isNaN(valor)) valor = 2;
//   if (valor < 2) valor = 2;
//   if (valor > 10) valor = 10;
//   input.value = valor;
//   actualizarBadges(valor);
// });

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
      <input name="valorRes_${numero}" id="valorRes_${numero}" type="number" placeholder="valor" required class="input input-sm input-bordered sm:w-20"/>
      <span class="btn btn-xs sm:btn-sm btn-error btn-outline btnEliminar">
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
        className: "alert alert-warning",
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
      className: "alert alert-warning",
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

const metodoSimplexBtn = document.getElementById("metodo_simplex");
const metodoScipyBtn = document.getElementById("metodo_scipy");

let metodoSelecionado;

function activarBotonSeleccionado(boton) {
  [metodoSimplexBtn, metodoScipyBtn].forEach((btn) => {
    if (btn === boton) {
      btn.classList.remove("btn-dash");
      btn.classList.add("btn-active");
    } else {
      btn.classList.remove("btn-active");
      btn.classList.add("btn-dash");
    }
  });
  metodoSelecionado = boton.innerText;
  console.log("Método seleccionado:", metodoSelecionado);
}

metodoSimplexBtn.addEventListener("click", () => {
  activarBotonSeleccionado(metodoSimplexBtn);
});

metodoScipyBtn.addEventListener("click", () => {
  activarBotonSeleccionado(metodoScipyBtn);
});

//AQUI ESTA LA VERDADERA SAUCEEE!!!
document.getElementById("formulario").addEventListener("submit", async (e) => {
  e.preventDefault();

  if (!metodoSelecionado) {
    alerta.open({
      type: "error",
      message: `Debe elegir un método para resolver el problema`,
      className: "alert alert-error",
    });
    return;
  }

  // Obtener datos del formulario
  const tipoOperacion = document.getElementById("tipoOperacion").value;
  const funcionObjetivo = document.getElementById("funcionObjetivo").value;
  const restricciones = [];
  const wrapper = document.getElementById("resWrapper");

  Array.from(wrapper.children).forEach((div) => {
    const expr = div.querySelector(`[name^="restriccion_"]`).value;
    const op = div.querySelector(`[name^="operadorRestriccion_"]`).value;
    const val = div.querySelector(`[name^="valorRes_"]`).value;

    restricciones.push({ expr, op, val });
  });

  const payload = {
    tipoOperacion,
    funcionObjetivo,
    restricciones,
  };

  if (metodoSelecionado === metodoSimplexBtn.innerText) {
    // MÉTODO SIMPLEX: varía el endpoint según el tipo de operación
    
    if (tipoOperacion === "Maximizar") {
      // Simplex clásico para maximización
      try {
        console.log("payload para simplex clásico (maximizar): ", payload);
        const data = await resolverSimplex(payload);
        mostrarResultadoSimplex(data);
      } catch (err) {
        console.error("Error al resolver con Simplex clásico:", err);
        alerta.open({
          type: "error",
          message: "Error al resolver el problema con Simplex clásico.",
          className: "alert alert-warning",
        });
      }
      
    } else if (tipoOperacion === "Minimizar") {
      // Gran M para minimización + SciPy para llenar la tarjeta de solución
      try {
        console.log("payload para simplex Gran M (minimizar): ", payload);
        
        // Llamada paralela: Gran M para pasos detallados y SciPy para la tarjeta
        const [granMResponse, scipyData] = await Promise.all([
          fetch("/resolver_gran_m", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
          }).then(res => res.json()),
          resolverProblema(payload)  // SciPy para llenar la tarjeta
        ]);
        
        console.log("Respuesta Gran M:", granMResponse);
        console.log("Respuesta SciPy para tarjeta:", scipyData);
        
        // Mostrar el HTML detallado del Gran M
        document.getElementById("resultados").innerHTML = granMResponse.html;
        
        // Llenar la tarjeta de solución con los datos de SciPy
        if (scipyData.resultado.status === "ok") {
          mostrarSolucion(scipyData);
        } else {
          console.warn("SciPy no pudo resolver para llenar la tarjeta:", scipyData.resultado.mensaje);
        }
        
      } catch (err) {
        console.error("Error al resolver con Gran M:", err);
        alerta.open({
          type: "error",
          message: "Error al resolver con Simplex Gran M: " + err.message,
          className: "alert alert-error",
        });
      }
    }
    
  } else if (metodoSelecionado === metodoScipyBtn.innerText) {
    // MÉTODO SCIPY: siempre usa el mismo endpoint
    try {
      console.log("payload para scipy: ", payload);
      const data = await resolverProblema(payload);
      console.log("respuesta de scipy:", data);
      if (data.resultado.status == "ok") {
        mostrarSolucion(data);
      } else {
        alerta.open({
          type: "error",
          message: data.resultado.mensaje,
          className: "alert alert-warning",
        });
      }
    } catch (err) {
      console.error("Error al resolver con Scipy:", err);
      alerta.open({
        type: "error",
        message:
          "Error al resolver el problema con Scipy. El problema no tiene una region factible",
        className: "alert alert-warning",
      });
    }
  }
});


