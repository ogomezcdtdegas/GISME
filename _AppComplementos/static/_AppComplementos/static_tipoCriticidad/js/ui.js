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
                <button class="btn btn-primary btn-sm" 
                    onclick="openEditModal('${relacion.id}', '${relacion.tipo_criticidad_name}', '${relacion.criticidad}', '${relacion.tipo_criticidad_id}')">
                    <i class="bi bi-pencil-square"></i>
                </button>
            </td>
        </tr>`;
        tableBody.insertAdjacentHTML('beforeend', row);
    });

    updatePagination(data, "loadTipCriticidadesPag");
}

function openEditModal(id, name, criticidadId, tipoCriticidadId) {
    // 🔹 Asegúrate de que estos campos existan en el modal HTML
    document.getElementById("edittipCritId").value = id;
    document.getElementById("editName").value = name;
    document.getElementById("edittipCritTipoId").value = tipoCriticidadId;  // 🔥 ¡Este es clave!

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

