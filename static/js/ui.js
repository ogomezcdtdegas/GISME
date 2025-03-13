// Función para mostrar u ocultar el submenú de "Complementos"
export function toggleSubMenu() {
    let submenu = document.getElementById("complementosSubmenu");
    if (submenu) {
        submenu.style.display = submenu.style.display === "block" ? "none" : "block";
        console.log("📂 Submenú de Complementos toggled:", submenu.style.display);
    }
}

// Función para actualizar la paginación
export function updatePagination(data, loadFunction) {
    const paginationContainer = document.querySelector(".pagination");
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
}
