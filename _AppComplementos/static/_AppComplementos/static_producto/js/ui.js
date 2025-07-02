// ui.js - Manipulación del DOM
function renderProductos(data) {
    console.log("🔄 datos paginados recibidos por el render de productos:", data);
    const tableBody = document.getElementById('prodTableBody');
    tableBody.innerHTML = "";

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
                        '${relacion.tipo_criticidad_id || ""}',
                        '${relacion.criticidad_id || ""}'  // Asegúrate de pasar este valor
                    )">
                    <i class="bi bi-pencil-square"></i>
                </button>
            </td>
        </tr>`;
        tableBody.insertAdjacentHTML('beforeend', row);
    });

    updatePagination(data, "loadProductosPag");
}

async function openEditModal(id, productoName, criticidadName, tipoCriticidadId, criticidadId) {
    // Setear valores básicos
    document.getElementById("editprodId").value = id;
    document.getElementById("editprodName").value = productoName;
    document.getElementById("editCriticidad").value = criticidadId; 
    
    // Referencias a los selects
    const tipoCritSelect = document.getElementById("editTipoCriticidad");
    const critSelect = document.getElementById("editCriticidad");
    
    // Cargar tipos de criticidad
    const allTipoCriticidades = await fetchAllTipoCriticidades();
    
    // Limpiar y poblar tipos de criticidad
    tipoCritSelect.innerHTML = '<option value="">Seleccione un tipo de criticidad</option>';
    allTipoCriticidades.forEach(tipo => {
        const option = document.createElement("option");
        option.value = tipo.id;
        option.textContent = tipo.name;
        if (tipo.id == tipoCriticidadId) option.selected = true;
        tipoCritSelect.appendChild(option);
    });
    
    // Configurar criticidades
    critSelect.innerHTML = '<option value="">Cargando criticidades...</option>';
    critSelect.disabled = true;
    
    // Si hay un tipo seleccionado, cargar sus criticidades
    if (tipoCriticidadId) {
        const criticidades = await fetchCriticidadesByTipo(tipoCriticidadId);
        
        // Limpiar y poblar criticidades
        critSelect.innerHTML = '';
        
        /*
        // Agregar opción por defecto solo si no hay criticidad seleccionada
        if (!criticidadId) {
            critSelect.appendChild(new Option("Seleccione una criticidad", ""));
        }*/
        
        // Poblar opciones
        criticidades.forEach(crit => {
            const option = new Option(crit.name, crit.id);
            if (crit.id == criticidadId) option.selected = true;
            critSelect.appendChild(option);
        });
        
        critSelect.disabled = false;
    }

    // Si hay un tipo seleccionado, cargar sus criticidades y seleccionar la correcta
    if (tipoCriticidadId) {
        await loadEditCriticidadesByTipo(criticidadId);
    }
    
    // Mostrar modal
    new bootstrap.Modal(document.getElementById('editModal')).show();
}

async function loadEditCriticidadesByTipo(selectedCriticidadId = null) {
    const tipoId = document.getElementById("editTipoCriticidad").value;
    const critSelect = document.getElementById("editCriticidad");

    critSelect.innerHTML = '<option value="">Cargando...</option>';
    critSelect.disabled = true;

    if (!tipoId) {
        critSelect.innerHTML = '<option value="">Seleccione un tipo primero</option>';
        return;
    }

    const criticidades = await fetchCriticidadesByTipo(tipoId);

    critSelect.innerHTML = '';
    criticidades.forEach(crit => {
        const option = new Option(crit.name, crit.id);
        // Comparación robusta: ambos a string
        if (String(crit.id) === String(selectedCriticidadId)) {
            option.selected = true;
        }
        critSelect.appendChild(option);
    });

    critSelect.disabled = false;
}
