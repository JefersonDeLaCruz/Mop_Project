
import "https://unpkg.com/mathlive";
import "https://esm.run/@cortex-js/compute-engine";

const mte = document.querySelector("math-field");

console.log(mte.getValue("math-json"))

mte.addEventListener('focus', () => {
    mathVirtualKeyboard.layouts = ["numeric", "symbols"];
    mathVirtualKeyboard.visible = true;
  });