// Configuración global de Notyf para toda la aplicación
let alerta;

// Inicializar Notyf cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
  // Verificar si Notyf está disponible
  if (typeof Notyf !== 'undefined') {
    alerta = new Notyf({
      duration: 3000,
      position: {
        x: "right",
        y: "top",
      },
      dismissible: true,
      types: [
        {
          type: "warning",
          background: "orange",
          icon: {
            className: "fas fa-exclamation-triangle",
            tagName: "i",
            color: "white"
          }
        },
        {
          type: "error",
          background: "red",
          icon: {
            className: "fas fa-times-circle",
            tagName: "i",
            color: "white"
          }
        },
        {
          type: "success",
          background: "green",
          icon: {
            className: "fas fa-check-circle",
            tagName: "i",
            color: "white"
          }
        },
        {
          type: "info",
          background: "blue",
          icon: {
            className: "fas fa-info-circle",
            tagName: "i",
            color: "white"
          }
        }
      ],
    });

    // Hacer el objeto alerta disponible globalmente
    window.alerta = alerta;
    
    console.log('Notyf inicializado globalmente');
  } else {
    console.error('Notyf no está disponible');
  }
});
