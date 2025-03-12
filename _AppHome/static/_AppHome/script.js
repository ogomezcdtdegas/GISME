document.addEventListener("DOMContentLoaded", function () {
    console.log("🟢 Página cargada - Inicializando...");
    
    loadEquiposPag(); // Cargar equipos al iniciar

    document.getElementById('recordsPerPage').addEventListener('change', function() {
        loadEquiposPag(); // Recargar equipos con nueva cantidad por página
    });
});

// 🔹 Función para cargar los equipos vía AJAX
function loadEquiposPag(page = 1) {
    console.log("🔄 Cargando equipos...");
    
    const perPage = document.getElementById('recordsPerPage').value;

    fetch(`/allEquiposPag/?page=${page}&per_page=${perPage}`, {
        method: "GET",
        headers: {
            "X-Requested-With": "XMLHttpRequest"  // 🔹 Para que Django lo detecte como AJAX
        }
    })
    .then(response => response.json())
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

        updatePagination(data, "loadEquipos");
    })
    .catch(error => console.error("❌ Error al cargar equipos:", error));
}

// 🔹 Manejo del formulario de registro de equipos
document.getElementById('equipoForm').addEventListener('submit', async function(event) {
    event.preventDefault();

    const serial = document.getElementById('serial').value;
    const sap = document.getElementById('sap').value;
    const marca = document.getElementById('marca').value;
    const requestBody = JSON.stringify({ serial, sap, marca });

    console.log("🚀 Enviando datos:", requestBody);

    try {
        const response = await fetch("/crear-equipo/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": getCSRFToken(),
            },
            body: requestBody
        });

        console.log("📩 Estado de respuesta:", response.status);

        if (!response.ok) {
            const errorText = await response.text();
            console.error("❌ Error en la solicitud:", errorText);
            throw new Error(`HTTP ${response.status}: ${errorText}`);
        }

        const data = await response.json();
        console.log("📩 Respuesta del servidor:", data);

        if (data.success) {
            const newRow = `<tr>
                <td>${serial}</td>
                <td>${sap}</td>
                <td>${marca}</td>
                <td>${new Date().toLocaleString()}</td> 
            </tr>`;
            document.getElementById('equiposTableBody').insertAdjacentHTML('afterbegin', newRow);
            document.getElementById('equipoForm').reset();
        } else {
            alert("❌ Error: " + (data.error || "No se pudo registrar el equipo"));
        }
    } catch (error) {
        console.error("❌ Error en el registro de equipo:", error);
    }
});