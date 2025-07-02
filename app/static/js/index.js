//aqui me voy a auxiliar para obtener la infor de los inputs
import { resolverProblema, mostrarSolucion } from "./solver.js";
import {
  resolverSimplex,
  mostrarResultadoSimplex,
} from "./simplexSolver.js";
import { normalizePayload, I18N_DEBUG, translateTerm } from "./i18n.js";

// Usar la instancia global de Notyf definida en base.js
// La variable 'alerta' estará disponible globalmente

console.log("hola index");

const limpiarBtn = document.getElementById("limpiarBtn")
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
  div.className = "flex flex-col sm:flex-row gap-2 items-stretch sm:items-center p-3 bg-base-200 rounded-lg";

  div.innerHTML = `
      <input name="restriccion_${numero}" id="restriccion_${numero}" type="text" placeholder="ej: x1 + x2" class="input input-sm input-bordered flex-1 min-w-0" />
      <select name="operadorRestriccion_${numero}" id="operadorRestriccion_${numero}" class="select select-sm select-bordered w-full sm:w-auto">
        <option>≤</option>
        <option>≥</option>
        <option>=</option>
      </select>
      <input name="valorRes_${numero}" id="valorRes_${numero}" type="number" placeholder="valor" required class="input input-sm input-bordered w-full sm:w-20"/>
      <span class="btn btn-sm btn-error btn-outline btnEliminar self-stretch sm:self-auto">
        <i class="fas fa-trash"></i>
        <span class="sm:hidden ml-2">${translateTerm('Eliminar')}</span>
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

// Inicializar botones de método sin selección
function inicializarBotonesMetodo() {
  [metodoSimplexBtn, metodoScipyBtn].forEach((btn) => {
    btn.classList.remove("btn-active");
    btn.classList.add("btn-outline");
  });
  metodoSelecionado = undefined;
}

function activarBotonSeleccionado(boton) {
  [metodoSimplexBtn, metodoScipyBtn].forEach((btn) => {
    if (btn === boton) {
      // Activar: remover btn-outline y agregar btn-active (color sólido)
      btn.classList.remove("btn-outline");
      btn.classList.add("btn-active");
    } else {
      // Desactivar: remover btn-active y agregar btn-outline
      btn.classList.remove("btn-active");
      btn.classList.add("btn-outline");
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

  // Normalizar el payload para que sea compatible con el backend
  const normalizedPayload = normalizePayload(payload);
  I18N_DEBUG.log("Payload normalizado para envío al backend", normalizedPayload);

  if (metodoSelecionado === metodoSimplexBtn.innerText) {
    // MÉTODO SIMPLEX: varía el endpoint según el tipo de operación
    // Usar los valores normalizados para las comparaciones
    if (normalizedPayload.tipoOperacion === "Maximizar") {
      // Verificar si hay restricciones mixtas (no solo ≤)
      const tieneRestriccionesMixtas = normalizedPayload.restricciones.some(r => r.op === "≥" || r.op === "=");
      
      if (tieneRestriccionesMixtas) {
        // Usar Gran M para restricciones mixtas en maximización
        try {
          console.log("payload para simplex Gran M (maximizar con restricciones mixtas): ", normalizedPayload);
          
          // Llamada paralela: Gran M para pasos detallados y SciPy para la tarjeta
          const [granMResponse, scipyData] = await Promise.all([
            fetch("/resolver_gran_m", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify(normalizedPayload),
            }).then(res => res.json()),
            resolverProblema(normalizedPayload)  // SciPy para llenar la tarjeta
          ]);
          
          console.log("Respuesta Gran M (maximizar):", granMResponse);
          console.log("Respuesta SciPy para tarjeta:", scipyData);
          
          // Mostrar el HTML detallado del Gran M
          document.getElementById("resultados").innerHTML = granMResponse.html;
          
          // Llenar la tarjeta de solución con los datos de SciPy
          if (scipyData.resultado.status === "ok") {
            mostrarSolucion(scipyData);
          } else {
            console.warn("SciPy no pudo resolver para llenar la tarjeta:", scipyData.resultado.mensaje);
          }
          
          // Scroll automático a la sección de resultados
          scrollToResults();
          
        } catch (err) {
          console.error("Error al resolver con Gran M (maximizar):", err);
          alerta.open({
            type: "error",
            message: "Error al resolver con Simplex Gran M: " + err.message,
            className: "alert alert-error",
          });
        }
      } else {
        // Simplex clásico para maximización con solo restricciones ≤
        try {
          console.log("payload para simplex clásico (maximizar solo ≤): ", normalizedPayload);
          const data = await resolverSimplex(normalizedPayload);
          mostrarResultadoSimplex(data);
          
          // Scroll automático a la sección de resultados
          scrollToResults();
          
          // Guardar en historial
          guardarEnHistorial(normalizedPayload, "Simplex Clásico");
        } catch (err) {
          console.error("Error al resolver con Simplex clásico:", err);
          alerta.open({
            type: "error",
            message: "Error al resolver el problema con Simplex clásico.",
            className: "alert alert-warning",
          });
        }
      }
      
    } else if (normalizedPayload.tipoOperacion === "Minimizar") {
      // Gran M para minimización + SciPy para llenar la tarjeta de solución
      try {
        console.log("payload para simplex Gran M (minimizar): ", normalizedPayload);
        
        // Llamada paralela: Gran M para pasos detallados y SciPy para la tarjeta
        const [granMResponse, scipyData] = await Promise.all([
          fetch("/resolver_gran_m", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(normalizedPayload),
          }).then(res => res.json()),
          resolverProblema(normalizedPayload)  // SciPy para llenar la tarjeta
        ]);
        
        console.log("Respuesta Gran M:", granMResponse);
        console.log("Respuesta SciPy para tarjeta:", scipyData);
        
        // Mostrar el HTML detallado del Gran M
        document.getElementById("resultados").innerHTML = granMResponse.html;
        
        // Llenar la tarjeta de solución con los datos de SciPy
        if (scipyData.resultado.status === "ok") {
          mostrarSolucion(scipyData);
          
          // Guardar en historial
          guardarEnHistorial(normalizedPayload, "Gran M");
        } else {
          console.warn("SciPy no pudo resolver para llenar la tarjeta:", scipyData.resultado.mensaje);
        }
        
        // Scroll automático a la sección de resultados
        scrollToResults();
        
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
      console.log("payload para scipy: ", normalizedPayload);
      const data = await resolverProblema(normalizedPayload);
      console.log("respuesta de scipy:", data);
      if (data.resultado.status == "ok") {
        mostrarSolucion(data);
        
        // Scroll automático a la sección de resultados
        scrollToResults();
        
        // Guardar en historial
        guardarEnHistorial(normalizedPayload, "SciPy");
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

// Función para guardar problema en el historial
async function guardarEnHistorial(payload, metodoUsado) {
  try {
    // Esperar un momento para que el DOM se actualice completamente
    setTimeout(async () => {
      const htmlGenerado = document.getElementById("resultados").innerHTML;
      
      // Solo guardar si hay contenido HTML generado
      if (htmlGenerado && htmlGenerado.trim() !== "") {
        const historialData = {
          payload: payload,
          metodo: metodoUsado,
          html_detallado: htmlGenerado,
          fecha: new Date().toISOString()
        };
        
        console.log("Guardando en historial:", historialData);
        
        // Enviar al backend para guardar
        const response = await fetch("/guardar_historial", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(historialData),
        });
        
        if (response.ok) {
          console.log("Problema guardado en historial exitosamente");
        } else {
          console.warn("Error al guardar en historial:", response.status);
        }
      }
    }, 1000); // Esperar 1 segundo para que se complete el renderizado
    
  } catch (error) {
    console.error("Error al guardar en historial:", error);
  }
}

// Función para cargar problema desde parámetros URL (para edición)
function cargarProblemaDesdeURL() {
  const urlParams = new URLSearchParams(window.location.search);
  
  // Verificar si estamos en modo edición
  if (urlParams.get('edit') === '1') {
    try {
      // Cargar tipo de operación
      const tipoOperacion = urlParams.get('tipoOperacion');
      if (tipoOperacion) {
        document.getElementById('tipoOperacion').value = tipoOperacion;
      }
      
      // Cargar función objetivo
      const funcionObjetivo = urlParams.get('funcionObjetivo');
      if (funcionObjetivo) {
        document.getElementById('funcionObjetivo').value = funcionObjetivo;
      }
      
      // Cargar restricciones
      const restriccionesParam = urlParams.get('restricciones');
      if (restriccionesParam) {
        const restricciones = JSON.parse(restriccionesParam);
        
        // Limpiar restricciones existentes
        const resWrapper = document.getElementById("resWrapper");
        resWrapper.innerHTML = '';
        
        // Función local para crear restricción (copia de la función principal)
        function crearRestriccionLocal(numero) {
          const div = document.createElement("div");
          div.className = "flex gap-2 items-center p-3 bg-base-200 rounded-lg";

          div.innerHTML = `
              <input name="restriccion_${numero}" id="restriccion_${numero}" type="text" placeholder="ej: x1 + x2" class="input input-sm input-bordered flex-grow" />
              <select name="operadorRestriccion_${numero}" id="operadorRestriccion_${numero}" class="select select-sm select-bordered flex-shrink-0 w-fit">
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
            if (resWrapper.children.length > 2) { // MIN_RESTRICCIONES = 2
              div.remove();
              actualizarNombresLocal();
            } else {
              alerta.open({
                type: "warning",
                message: `Debe haber al menos 2 restricciones`,
                className: "alert alert-warning",
              });
            }
          });

          return div;
        }
        
        // Función local para actualizar nombres
        function actualizarNombresLocal() {
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
        
        // Agregar las restricciones del problema
        restricciones.forEach((restriccion, index) => {
          const nuevaRestriccion = crearRestriccionLocal(index + 1);
          
          // Poblar los valores
          const expresionInput = nuevaRestriccion.querySelector(`[type="text"]`);
          const operadorSelect = nuevaRestriccion.querySelector('select');
          const valorInput = nuevaRestriccion.querySelector(`[type="number"]`);
          
          expresionInput.value = restriccion.expr || '';
          operadorSelect.value = restriccion.op || '≤';
          valorInput.value = restriccion.val || '';
          
          resWrapper.appendChild(nuevaRestriccion);
        });
        
        // Si hay menos de 2 restricciones, agregar las mínimas
        while (resWrapper.children.length < 2) {
          const nueva = crearRestriccionLocal(resWrapper.children.length + 1);
          resWrapper.appendChild(nueva);
        }
        
        // Actualizar nombres después de cargar
        actualizarNombresLocal();
      }
      
      // Cargar método seleccionado
      const metodo = urlParams.get('metodo');
      if (metodo) {
        const metodoSimplexBtn = document.getElementById("metodo_simplex");
        const metodoScipyBtn = document.getElementById("metodo_scipy");
        
        // Función para activar botón (copia de la función principal)
        function activarBotonSeleccionadoLocal(boton) {
          [metodoSimplexBtn, metodoScipyBtn].forEach((btn) => {
            if (btn === boton) {
              btn.classList.remove("btn-dash");
              btn.classList.add("btn-active");
            } else {
              btn.classList.remove("btn-active");
              btn.classList.add("btn-dash");
            }
          });
        }
        
        // Mapear nombres de métodos
        if (metodo === 'Simplex Clásico' || metodo === 'Gran M') {
          activarBotonSeleccionadoLocal(metodoSimplexBtn);
        } else if (metodo === 'SciPy') {
          activarBotonSeleccionadoLocal(metodoScipyBtn);
        }
      }
      
      // Limpiar la URL después de cargar los datos
      window.history.replaceState({}, document.title, window.location.pathname);
      
      // Mostrar mensaje de confirmación
      setTimeout(() => {
        alerta.open({
          type: "info",
          message: "Problema cargado para edición. Puedes modificar los valores y resolver de nuevo.",
          className: "alert alert-info",
        });
      }, 500);
      
    } catch (error) {
      console.error('Error al cargar problema desde URL:', error);
      alerta.open({
        type: "error",
        message: "Error al cargar los datos del problema para edición.",
        className: "alert alert-error",
      });
    }
  }
}

// Ejecutar al cargar la página
document.addEventListener('DOMContentLoaded', () => {
  // Inicializar los botones de método para que no estén seleccionados
  inicializarBotonesMetodo();
  
  // Cargar problema desde URL si corresponde
  cargarProblemaDesdeURL();
});

// Función para limpiar todos los campos del formulario
function limpiarFormulario() {
  // Limpiar tipo de operación (volver al primer valor)
  document.getElementById('tipoOperacion').selectedIndex = 0;
  
  // Limpiar función objetivo
  document.getElementById('funcionObjetivo').value = '';
  
  // Limpiar restricciones existentes y volver a las 2 mínimas
  resWrapper.innerHTML = '';
  
  // Recrear las 2 restricciones mínimas vacías
  for (let i = 1; i <= MIN_RESTRICCIONES; i++) {
    resWrapper.appendChild(crearRestriccion(i));
  }
  
  // Limpiar selección de método
  inicializarBotonesMetodo();
  
  // Limpiar resultados si existen
  const resultadosDiv = document.getElementById("resultados");
  if (resultadosDiv) {
    resultadosDiv.innerHTML = '';
  }
  
  // Mostrar mensaje de confirmación
  alerta.open({
    type: "success",
    message: "Formulario limpiado correctamente",
    className: "alert alert-success",
  });
}

// Agregar evento al botón limpiar
limpiarBtn.addEventListener("click", limpiarFormulario);

// Función para hacer scroll automático a la sección de resultados
function scrollToResults() {
  const resultadosSection = document.getElementById("resultados");
  if (resultadosSection) {
    resultadosSection.scrollIntoView({
      behavior: "smooth",
      block: "start"
    });
  }
}


