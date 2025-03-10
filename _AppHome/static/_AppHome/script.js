document.addEventListener("DOMContentLoaded", function () {
    console.log("🟢 Página cargada - Inicializando...");
    
    loadEquipos(); // Cargar equipos al iniciar

    document.getElementById('recordsPerPage').addEventListener('change', function() {
        loadEquipos(); // Recargar equipos con nueva cantidad por página
    });
});

// 🔹 Función para cargar los equipos vía AJAX
function loadEquipos(page = 1) {
    console.log("🔄 Cargando equipos...");
    
    const perPage = document.getElementById('recordsPerPage').value;

    fetch(`/allEquiposPag/?page=${page}&per_page=${perPage}`, {
        method: "GET",
        headers: {
            "X-Requested-With": "XMLHttpRequest"  // 🔹 Para que Django lo detecte como AJAX
        }
    })
    .then(response => {
        console.log("📥 Content-Type recibido:", response.headers.get("content-type"));
        return response.json();
    })
    .then(data => {
        console.log("✅ Respuesta AJAX:", data);

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
    .catch(error => console.error("❌ Error al cargar equipos:", error));
}

// 🔹 Función para actualizar los controles de paginación
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

// 🔹 Manejo del formulario de registro de equipos
document.getElementById('equipoForm').addEventListener('submit', function(event) {
    event.preventDefault();
    
    const formData = new FormData(this);

    fetch("{% url 'crearEquipo' %}", {
        method: "POST",
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const newRow = `<tr>
                <td>${data.equipo.serial}</td>
                <td>${data.equipo.sap}</td>
                <td>${data.equipo.marca}</td>
                <td>${data.equipo.created_at}</td>
            </tr>`;
            document.getElementById('equiposTableBody').insertAdjacentHTML('afterbegin', newRow);
            document.getElementById('equipoForm').reset();
        }
    })
    .catch(error => console.error("❌ Error en el registro de equipo:", error));
});
