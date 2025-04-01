console.log("🎭 events.js cargado.");

document.addEventListener("DOMContentLoaded", function () {
    let toggleComplementos = document.getElementById("toggleComplementos");
    let submenu = document.getElementById("complementosSubmenu");

    if (toggleComplementos && submenu) {
        toggleComplementos.addEventListener("click", function (event) {
            event.preventDefault();
            window.toggleElement(submenu);
            console.log("📂 Submenú de Complementos toggled:", submenu.style.display);
        });
    } else {
        console.warn("⚠ No se encontró el botón o el submenú de Complementos.");
    }
});
