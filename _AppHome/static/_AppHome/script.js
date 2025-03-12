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
                <td>
                    <button class="btn btn-primary btn-sm" onclick="openEditModal('${equipo.id}', '${equipo.serial}', '${equipo.sap}', '${equipo.marca}')">
                        <i class="bi bi-pencil-square"></i>
                    </button>
                </td>
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

    // Capturar datos manualmente
    const serial = document.getElementById('serial').value;
    const sap = document.getElementById('sap').value;
    const marca = document.getElementById('marca').value;

    const requestBody = JSON.stringify({ serial, sap, marca });

    try {
        const response = await fetch("/crear-equipo/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": getCSRFToken(),  // Agregar CSRF Token
            },
            body: requestBody
        });

        const data = await response.json();
        console.log("📩 Respuesta del servidor:", data);

        if (data.success) {
            const newRow = `<tr>
                <td>${serial}</td>
                <td>${sap}</td>
                <td>${marca}</td>
                <td>${new Date().toLocaleString()}</td> 
                <td>
                    <button class="btn btn-primary btn-sm" onclick="openEditModal('${data.id}', '${serial}', '${sap}', '${marca}')">
                        <i class="bi bi-pencil-square"></i>
                    </button>
                </td>
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


function openEditModal(id, serial, sap, marca) {
    console.log("🛠 Abriendo modal de edición para ID:", id, "Serial:", serial, "SAP:", sap, "Marca:", marca);

    if (!id) {
        console.error("❌ Error: El ID del equipo es undefined o vacío.");
        return;
    }
    document.getElementById("editEquipoId").value = id;
    document.getElementById("editSerial").value = serial;
    document.getElementById("editSap").value = sap;
    document.getElementById("editMarca").value = marca;
    var modal = new bootstrap.Modal(document.getElementById('editModal'));
    modal.show();
}

document.getElementById("editEquipoForm").addEventListener("submit", async function(event) {
    event.preventDefault();

    const id = document.getElementById("editEquipoId").value;
    const serial = document.getElementById("editSerial").value;
    const sap = document.getElementById("editSap").value;
    const marca = document.getElementById("editMarca").value;
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    try {
        const response = await fetch(`/editar-equipo/${id}/`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken,
                "X-Requested-With": "XMLHttpRequest"
            },
            body: JSON.stringify({ serial, sap, marca })
        });

        const data = await response.json();
        if (data.success) {
            location.reload();
        } else {
            alert("Error al actualizar el equipo");
        }
    } catch (error) {
        console.error("Error en la actualización:", error);
    }
});