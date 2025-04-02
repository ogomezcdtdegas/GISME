console.log("🎨 ui.js cargado.");

// Función para mostrar/ocultar elementos
window.toggleElement = function (element) {
    element.style.display = element.style.display === "block" ? "none" : "block";
};

// Función para actualizar la paginación
window.onload = function () {
    console.log("🎨 ui.js cargado.");

    window.toggleElement = function (element) {
        element.style.display = element.style.display === "block" ? "none" : "block";
    };

    window.updatePagination = function (data, loadFunction) {
        const paginationContainer = document.querySelector(".pagination");
        if (!paginationContainer) {
            console.warn("⚠ No se encontró el contenedor de paginación.");
            return;
        }

        paginationContainer.innerHTML = ""; // Limpiar paginación

        if (data.has_previous) {
            paginationContainer.innerHTML += `<li class="page-item"><a class="page-link" href="#" onclick="${loadFunction}(1)">« Primero</a></li>`;
            paginationContainer.innerHTML += `<li class="page-item"><a class="page-link" href="#" onclick="${loadFunction}(${data.previous_page_number})">Anterior</a></li>`;
        }

        paginationContainer.innerHTML += `<li class="page-item disabled"><span class="page-link">Página ${data.current_page} de ${data.total_pages}</span></li>`;

        if (data.has_next) {
            paginationContainer.innerHTML += `<li class="page-item"><a class="page-link" href="#" onclick="${loadFunction}(${data.next_page_number})">Siguiente</a></li>`;
            paginationContainer.innerHTML += `<li class="page-item"><a class="page-link" href="#" onclick="${loadFunction}(${data.total_pages})">Última »</a></li>`;
        }
    };

    console.log("🔄 Función updatePagination registrada.");
};
