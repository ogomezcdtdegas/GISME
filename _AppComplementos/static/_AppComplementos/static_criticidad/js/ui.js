// ui.js - Manipulación del DOM
function renderCriticidades(data) {
    const tableBody = document.getElementById('critTableBody');
    tableBody.innerHTML = ""; // Limpiar tabla

    data.results.forEach(criticidad => {
        const row = `<tr data-id="${criticidad.id}">
            <td>${criticidad.name}</td>
            <td>${criticidad.created_at}</td>
            <td>
                <button class="btn btn-primary btn-sm" onclick="openEditModal('${criticidad.id}', '${criticidad.name}')">
                    <i class="bi bi-pencil-square"></i>
                </button>
            </td>
        </tr>`;
        tableBody.insertAdjacentHTML('beforeend', row);
    });

    updatePagination(data, "loadCriticidadesPag");
}

function openEditModal(id, name) {
    document.getElementById("editCritId").value = id;
    document.getElementById("editName").value = name;
    new bootstrap.Modal(document.getElementById('editModal')).show();
}
