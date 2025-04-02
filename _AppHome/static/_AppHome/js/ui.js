// ui.js - Manipulación del DOM
function renderEquipos(data) {
    const tableBody = document.getElementById('equiposTableBody');
    tableBody.innerHTML = ""; // Limpiar tabla

    // ✅ Ajustar a la clave correcta ("results" en lugar de "equipos")
    data.results.forEach(equipo => {
        const row = `<tr data-id="${equipo.id}">
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
    updatePagination(data, "loadEquiposPag");
}


function openEditModal(id, serial, sap, marca) {
    document.getElementById("editEquipoId").value = id;
    document.getElementById("editSerial").value = serial;
    document.getElementById("editSap").value = sap;
    document.getElementById("editMarca").value = marca;
    new bootstrap.Modal(document.getElementById('editModal')).show();
}
