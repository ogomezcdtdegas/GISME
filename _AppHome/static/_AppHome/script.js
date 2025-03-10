document.addEventListener("DOMContentLoaded", function () {
    loadEquipos(); // Cargar equipos al iniciar

    document.getElementById('recordsPerPage').addEventListener('change', function() {
        loadEquipos();
        console.log("cargando equipos1")
    });
});

// 🔹 Función para cargar los equipos vía AJAX
function loadEquipos(page = 1) {
    console.log("cargando equipos2")
    const perPage = document.getElementById('recordsPerPage').value;
    
    fetch(`/allEquiposPag/?page=${page}&per_page=${perPage}`, {
        method: "GET",
        headers: {
            "X-Requested-With": "XMLHttpRequest"  // 🔹 Importante para que Django lo detecte
        }
    })
    .then(response => {
        console.log("Content-Type recibido:", response.headers.get("content-type"));
        return response.json();
    })
    .then(data => {
        console.log("Respuesta AJAX:", data);

        const tableBody = document.getElementById('equiposTableBody');
        tableBody.innerHTML = ""; // Limpiar tabla

        data.equipos.forEach(equipo => {
            const row = `<tr>
                <td>${equipo.serial}</td>
                <td>${equipo.sap}</td>
                <td>${equipo.marca}</td>
                <td>${equipo.created_at}</td>
            </tr>`;
            tableBody.insertAdjacentHTML('beforeend', row);
        });

        updatePagination(data);
    })
    .catch(error => console.error("Error:", error));
}

// Llamar a la función al cargar la página
document.addEventListener("DOMContentLoaded", function () {
    loadEquipos();
});



// Función para actualizar los controles de paginación
function updatePagination(data) {
    const paginationContainer = document.querySelector(".pagination");
    paginationContainer.innerHTML = ""; // Limpiar paginación

    if (data.has_previous) {
        paginationContainer.innerHTML += `<li class="page-item"><a class="page-link" href="#" onclick="loadEquipos(1)">« Primero</a></li>`;
        paginationContainer.innerHTML += `<li class="page-item"><a class="page-link" href="#" onclick="loadEquipos(${data.previous_page_number})">Anterior</a></li>`;
    }

    paginationContainer.innerHTML += `<li class="page-item disabled"><span class="page-link">Página ${data.current_page} de ${data.total_pages}</span></li>`;

    if (data.has_next) {
        paginationContainer.innerHTML += `<li class="page-item"><a class="page-link" href="#" onclick="loadEquipos(${data.next_page_number})">Siguiente</a></li>`;
        paginationContainer.innerHTML += `<li class="page-item"><a class="page-link" href="#" onclick="loadEquipos(${data.total_pages})">Última »</a></li>`;
    }
}
