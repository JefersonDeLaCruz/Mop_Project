// const toggleBtn = document.getElementById("toggle-theme");
// const htmlEl = document.documentElement;
// const iconEl = document.getElementById("theme-icon");
// const themeAttr = "data-theme";

// function applyTheme() {
//   const savedTheme = localStorage.getItem("theme") || "light";

//   htmlEl.setAttribute(themeAttr, savedTheme);

//   if (iconEl) {
//     if (savedTheme === "dark") {
//       iconEl.classList.add("fa-sun");
//       iconEl.classList.remove("fa-moon");
//     } else {
//       iconEl.classList.remove("fa-sun");
//       iconEl.classList.add("fa-moon");
//     }
//   }
// }

// document.addEventListener("DOMContentLoaded", () => {
//   applyTheme();

//   const $navbarBurgers = Array.prototype.slice.call(
//     document.querySelectorAll(".navbar-burger"), 0
//   );

//   $navbarBurgers.forEach((el) => {
//     el.addEventListener("click", () => {
//       const target = el.dataset.target;
//       const $target = document.getElementById(target);
//       el.classList.toggle("is-active");
//       $target.classList.toggle("is-active");
//     });
//   });
// });

// // Aplica el tema incluso cuando el usuario usa los botones "atrás" o "adelante"
// window.addEventListener("pageshow", (event) => {
//   if (
//     event.persisted ||
//     performance.getEntriesByType("navigation")[0].type === "back_forward"
//   ) {
//     applyTheme();
//   }
// });

// // Manejar toggle del tema
// if (toggleBtn) {
//   toggleBtn.addEventListener("click", () => {
//     const currentTheme = htmlEl.getAttribute(themeAttr);
//     const newTheme = currentTheme === "dark" ? "light" : "dark";

//     localStorage.setItem("theme", newTheme);
//     applyTheme();
//   });
// }
