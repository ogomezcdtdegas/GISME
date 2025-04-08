// ui.js - Manipulación del DOM
function renderProductos(data) {
    const tableBody = document.getElementById('prodTableBody');
    tableBody.innerHTML = ""; // Limpiar tabla

    if (!data || !data.results || data.results.length === 0) {
        const row = `<tr><td colspan="4">No hay productos registrados</td></tr>`;
        tableBody.insertAdjacentHTML('beforeend', row);
        return;
    }

    data.results.forEach(relacion => {
        const row = `<tr data-id="${relacion.id}">
            <td>${relacion.producto_name || "Sin datos"}</td>
            <td>${relacion.tipo_criticidad_name || "Sin datos"}</td>
            <td>${relacion.criticidad_name || "Sin datos"}</td>
            <td>
                <button class="btn btn-primary btn-sm" 
                    onclick="openEditModal(
                        '${relacion.id}', 
                        '${relacion.producto_name || ""}', 
                        '${relacion.criticidad_name || ""}', 
                        '${relacion.tipo_criticidad_id || ""}'
                    )">
                    <i class="bi bi-pencil-square"></i>
                </button>
            </td>
        </tr>`;
        tableBody.insertAdjacentHTML('beforeend', row);
    });

    // Actualizar paginación si es necesario
    if (data.paginator) {
        updatePagination(data, "loadProductosPag");
    }
}

function openEditModal(id, name, criticidadId, tipoCriticidadId) {
    // 🔹 Asegúrate de que estos campos existan en el modal HTML
    document.getElementById("edittipCritId").value = id;
    document.getElementById("editName").value = productoName;
    document.getElementById("edittipCritTipoId").value = tipoCriticidadId;

    const select = document.getElementById("editCriticidad");
    select.innerHTML = '<option value="">Cargando...</option>';

    fetchAllCriticidades().then(criticidades => {
        select.innerHTML = '<option value="">Seleccione una criticidad</option>'; 
        criticidades.forEach(crit => {
            const option = document.createElement("option");
            option.value = crit.id;
            option.textContent = crit.name;
            if (crit.id == criticidadId) option.selected = true;
            select.appendChild(option);
        });
    });

    new bootstrap.Modal(document.getElementById('editModal')).show();
}

