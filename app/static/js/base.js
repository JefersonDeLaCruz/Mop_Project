

document.addEventListener('DOMContentLoaded', () => {

  // Get all "navbar-burger" elements
  const $navbarBurgers = Array.prototype.slice.call(document.querySelectorAll('.navbar-burger'), 0);

  // Add a click event on each of them
  $navbarBurgers.forEach( el => {
    el.addEventListener('click', () => {

      // Get the target from the "data-target" attribute
      const target = el.dataset.target;
      const $target = document.getElementById(target);

      // Toggle the "is-active" class on both the "navbar-burger" and the "navbar-menu"
      el.classList.toggle('is-active');
      $target.classList.toggle('is-active');

    });
  });

});



const toggleBtn = document.getElementById("toggle-theme");
const htmlEl = document.documentElement;
// const darkClass = "theme-dark";
const themeAttr = "data-theme";
// const Attr = "data-theme";

// Inicializar tema según localStorage
const savedTheme = localStorage.getItem("theme");
if (savedTheme === "dark") {
//   htmlEl.classList.add(darkClass);
  htmlEl.setAttribute(themeAttr, "dark");
} else {

    //   htmlEl.classList.remove(darkClass);
    //   htmlEl.removeAttribute(darkAttr);
    htmlEl.setAttribute(themeAttr, "light")

}

// Lógica para alternar tema
toggleBtn.addEventListener("click", () => {
//   const isDark = htmlEl.classList.contains(darkClass);
  const theme = htmlEl.getAttribute(themeAttr);

  if (theme == "dark") {
    // htmlEl.classList.remove(darkClass);
    // htmlEl.removeAttribute(darkAttr);
    htmlEl.setAttribute(themeAttr, "light")
    localStorage.setItem("theme", "light");
  } else {
    // htmlEl.classList.add(darkClass);
    htmlEl.setAttribute(themeAttr, "dark");
    localStorage.setItem("theme", "dark");
  }
});