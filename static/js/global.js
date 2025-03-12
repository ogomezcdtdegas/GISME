document.addEventListener("DOMContentLoaded", function () {
    console.log("Script global cargado correctamente.");

    // Definir la función en el objeto window para que sea accesible en todos los scripts
    window.getCSRFToken = function () {
        let csrfToken = null;
        document.cookie.split(";").forEach(cookie => {
            let [name, value] = cookie.trim().split("=");
            if (name === "csrftoken") {
                csrfToken = value;
            }
        });
        return csrfToken;
    };

    console.log("CSRF Token function registrada.");
});

function updatePagination(data, loadFunction) {
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
