//aqui me voy a auxiliar para obtener la infor de los inputs
import { resolverProblema, mostrarSolucion } from "./solver.js";
import {
  resolverSimplex,
  mostrarResultadoSimplex,
  resolverSimplexGeneral,
  mostrarResultadoGranM
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
      className: "alert alert-warning",
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
      className: "alert alert-warning",
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
const metodoGeneralBtn = document.getElementById("metodo_general");
const metodoScipyBtn = document.getElementById("metodo_scipy");


let metodoSelecionado;

function activarBotonSeleccionado(boton) {
  [metodoSimplexBtn, metodoGeneralBtn, metodoScipyBtn].forEach((btn) => {
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

metodoGeneralBtn.addEventListener("click", () => {
  activarBotonSeleccionado(metodoGeneralBtn);
});

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

  if (metodoSelecionado === metodoGeneralBtn.innerText) {
    const tipoOperacion = document.getElementById("tipoOperacion").value;
    const funcionObjetivo = document.getElementById("funcionObjetivo").value;
    const numeroVariables = parseInt(
      document.getElementById("numeroVariables").value
    );

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
      numeroVariables,
      restricciones,
    };

    try {
      console.log("payload para general: ", payload);
      const data = await resolverSimplexGeneral(payload);

      // ✅ CORRECCIÓN: Verificar la estructura correcta de la respuesta
      if (data.status !== "success" || !data.resultado?.optimo) {
        // Manejar casos especiales
        if (
          data.status === "warning" &&
          data.resultado?.status === "infactible"
        ) {
          throw new Error(
            "Problema infactible: " +
              (data.resultado.mensaje || "No tiene solución factible")
          );
        } else if (data.tipo === "no_acotada") {
          throw new Error(
            "Problema no acotado: La solución tiende al infinito"
          );
        } else {
          throw new Error(
            data.error || "El servidor no devolvió una solución válida"
          );
        }
      }

      // ✅ Pasar solo el resultado, no toda la respuesta del servidor
      mostrarResultadoGranM(data.resultado);
    } catch (err) {
      console.error("Error al resolver:", err);
      alerta.open({
        type: "error",
        message: "Error al resolver con Simplex General: " + err.message,
        className: "alert alert-error",
      });
    }
  } else if (metodoSelecionado === metodoSimplexBtn.innerText) {
    // alerta.open({
    //   type: "warning",
    //   message: `El método Simplex aún no está implementado`,
    //   className: "alert alert-warning alert-outline",
    // });
    // return;

    const tipoOperacion = document.getElementById("tipoOperacion").value;
    const funcionObjetivo = document.getElementById("funcionObjetivo").value;
    const numeroVariables = parseInt(
      document.getElementById("numeroVariables").value
    );

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
      numeroVariables,
      restricciones,
    };

    if (!esValidoParaSimplex(payload)) {
      alerta.open({
        type: "error",
        message:
          "Solo se permiten problemas de maximización con restricciones '≤' y coeficientes positivos.",
        className: "alert alert-warning",
      });
      return;
    }

    try {
      console.log("payload para simplex: ", payload);
      const data = await resolverSimplex(payload);
      mostrarResultadoSimplex(data);
    } catch (err) {
      console.error("Error al resolver con Simplex:", err);
      alerta.open({
        type: "error",
        message: "Error al resolver el problema con Simplex.",
        className: "alert alert-warning",
      });
    }
  } else if (metodoSelecionado === metodoScipyBtn.innerText) {
    const tipoOperacion = document.getElementById("tipoOperacion").value;
    const funcionObjetivo = document.getElementById("funcionObjetivo").value;
    const numeroVariables = parseInt(
      document.getElementById("numeroVariables").value
    );

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
      numeroVariables,
      restricciones,
    };

    try {
      console.log("payload para scipy: ", payload);
      const data = await resolverProblema(payload);
      mostrarSolucion(data);
    } catch (err) {
      console.error("Error al resolver con Scipy:", err);
      alerta.open({
        type: "error",
        message: "Error al resolver el problema con Scipy.",
        className: "alert alert-warning",
      });
    }
  }
});

function esValidoParaSimplex(payload) {
  const { tipoOperacion, restricciones } = payload;

  console.log(tipoOperacion, restricciones, "fuck this shit");
  if (tipoOperacion !== "Maximizar") return false;

  const todasMenorIgual = restricciones.every((r) => r.op === "≤");
  if (!todasMenorIgual) return false;

  const todosCoeficientesPositivos = restricciones.every((r) => {
    const regex = /[-]/;
    return !regex.test(r.expr);
  });

  return todosCoeficientesPositivos;
}
