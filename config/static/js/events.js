console.log("🎭 events.js cargado.");

document.addEventListener("DOMContentLoaded", function () {
    let toggleComplementos = document.getElementById("toggleComplementos");
    let submenuComplementos = document.getElementById("complementosSubmenu");
    let toggleAdministracion = document.getElementById("toggleAdministracion");
    let submenuAdministracion = document.getElementById("administracionSubmenu");

    // Función para alternar menú
    function toggleMenu(button, submenu, name) {
        if (button && submenu) {
            button.addEventListener("click", function (event) {
                event.preventDefault();
                window.toggleElement(submenu);
                console.log(`📂 Submenú de ${name} toggled:`, submenu.style.display);
            });
        } else {
            console.warn(`⚠ No se encontró el botón o el submenú de ${name}.`);
        }
    }

    toggleMenu(toggleComplementos, submenuComplementos, "Complementos");
    toggleMenu(toggleAdministracion, submenuAdministracion, "Administración");
});
