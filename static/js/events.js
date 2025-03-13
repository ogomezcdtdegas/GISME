import { toggleSubMenu } from "./ui.js";

export function registerEvents() {
    console.log("📌 Registrando eventos...");

    let toggleComplementos = document.getElementById("toggleComplementos");
    if (toggleComplementos) {
        toggleComplementos.addEventListener("click", function (event) {
            event.preventDefault();
            toggleSubMenu();
        });
    } else {
        console.warn("⚠ No se encontró el botón de Complementos.");
    }
}
