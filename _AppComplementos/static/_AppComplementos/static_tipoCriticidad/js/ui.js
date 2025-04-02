// ui.js - Manipulación del DOM
function renderTipCriticidades(data) {
    const tableBody = document.getElementById('tipcritTableBody');
    tableBody.innerHTML = ""; // Limpiar tabla

    data.results.forEach(relacion => {
        console.log("🟢 Procesando:", relacion); // Para depuración

        const row = `<tr data-id="${relacion.id}">
            <td>${relacion.tipo_criticidad_name || "Sin datos"}</td>
            <td>${relacion.criticidad_name || "Sin datos"}</td>
            <td>${relacion.created_at ? new Date(relacion.created_at).toLocaleString() : "Sin fecha"}</td>
            <td>
                <button class="btn btn-primary btn-sm" onclick="openEditModal('${relacion.id}', '${relacion.tipo_criticidad_name}')">
                    <i class="bi bi-pencil-square"></i>
                </button>
            </td>
        </tr>`;
        tableBody.insertAdjacentHTML('beforeend', row);
    });

    updatePagination(data, "loadTipCriticidadesPag");
}


function openEditModal(id, name) {
    document.getElementById("edittipCritId").value = id;
    document.getElementById("editName").value = name;
    new bootstrap.Modal(document.getElementById('editModal')).show();
}
