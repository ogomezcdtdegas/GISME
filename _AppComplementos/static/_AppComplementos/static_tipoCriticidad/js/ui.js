// ui.js - Manipulación del DOM
function renderTipCriticidades(data) {
    const tableBody = document.getElementById('tipcritTableBody');
    tableBody.innerHTML = ""; // Limpiar tabla

    data.results.forEach(tipcriticidad => {
        const row = `<tr data-id="${tipcriticidad.id}">
            <td>${tipcriticidad.name}</td>
            <td>${tipcriticidad.created_at}</td>
            <td>
                <button class="btn btn-primary btn-sm" onclick="openEditModal('${tipcriticidad.id}', '${tipcriticidad.name}')">
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
