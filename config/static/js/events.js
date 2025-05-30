console.log("🎭 events.js cargado.");

document.addEventListener("DOMContentLoaded", function () {
    // Selectores de menú existentes
    let toggleHerramientas = document.getElementById("toggleHerramientas");
    let submenuHerramientas = document.getElementById("herramientasSubmenu");

    let toggleComplementos = document.getElementById("toggleComplementos");
    let submenuComplementos = document.getElementById("complementosSubmenu");

    let toggleAdministracion = document.getElementById("toggleAdministracion");
    let submenuAdministracion = document.getElementById("administracionSubmenu");

    // --- NUEVO: Selectores para el submenú de Cálculo de Caudal ---
    let toggleCalculoCaudal = document.getElementById("toggleCalculoCaudal");
    let submenuCalculoCaudal = document.getElementById("calculoCaudalSubmenu");
    // --- FIN NUEVO ---

    // Función para alternar menú
    // (Asegúrate de que window.toggleElement esté definida en tu proyecto)
    // Ejemplo de cómo podría ser window.toggleElement:
    /* if (typeof window.toggleElement !== 'function') {
         window.toggleElement = function(element) {
             if (!element) return;
             if (element.style.display === "none" || element.style.display === "") {
                 element.style.display = "block"; // o "flex", según tu layout
             } else {
                 element.style.display = "none";
             }
         };
     }*/

    function toggleMenu(button, submenu, name) {
        if (button && submenu) {
            button.addEventListener("click", function (event) {
                event.preventDefault(); // Evita la navegación por el '#'
                window.toggleElement(submenu); // Llama a tu función global para mostrar/ocultar
                console.log(`📂 Submenú de ${name} toggled:`, submenu.style.display);
            });
        } else {
            // Solo advertir si el botón principal de una sección no se encuentra.
            // Para sub-submenús, podría ser opcional si no siempre están presentes.
            if (name === "Herramientas" || name === "Complementos" || name === "Administración") {
                 console.warn(`⚠ No se encontró el botón o el submenú de ${name}.`);
            } else if (button || submenu) { // Si uno existe pero el otro no para submenús
                 console.warn(`⚠ Problema con el botón o submenú de ${name}. Botón: ${!!button}, Submenú: ${!!submenu}`);
            }
            // No mostrar advertencia si ambos (botón y submenú de un subnivel) son null/undefined
            // ya que puede ser que esa sección no esté cargada.
        }
    }

    // Asignar eventos a los botones principales
    toggleMenu(toggleHerramientas, submenuHerramientas, "Herramientas");
    toggleMenu(toggleComplementos, submenuComplementos, "Complementos");
    toggleMenu(toggleAdministracion, submenuAdministracion, "Administración");

    // --- NUEVO: Asignar evento al submenú de Cálculo de Caudal ---
    toggleMenu(toggleCalculoCaudal, submenuCalculoCaudal, "Cálculo de Caudal");
    // --- FIN NUEVO ---
});