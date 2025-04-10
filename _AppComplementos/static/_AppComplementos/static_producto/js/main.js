// main.js - Punto de entrada a la _AppHome
async function loadProductosPag(page = 1) {
    console.log("🔄 Cargando los tipos de productos...");
    console.log("🔄 Cargando los tipos de criticidades para la página:", page);
    const perPage = document.getElementById('recordsPerPage').value;

    // 🔹 Cargar tipos de criticidades paginados
    const data = await fetchProductos(page, perPage);
    console.log("🔄 datos paginados de productos:", data);
    if (data) renderProductos(data);

    // 🔹 Cargar todas las criticidades sin paginación y verificar en consola
    const allTipoCriticidades = await fetchAllTipoCriticidades();
    if (allTipoCriticidades) populateTipoCriticidadDropdown(allTipoCriticidades);
    console.log("📡 Todas los tipo de criticidad:", allTipoCriticidades);
    
}

// 🔹 Función para poblar el dropdown con todas las criticidades
function populateTipoCriticidadDropdown(tipocriticidades) {
    const select = document.getElementById('tipocriticidadDropdown');
    select.innerHTML = '<option value="">Seleccione un tipo de criticidad</option>'; // Resetear opciones

    tipocriticidades.forEach(tipocriticidad => {
        const option = document.createElement('option');
        option.value = tipocriticidad.id;
        option.textContent = tipocriticidad.name;
        select.appendChild(option);
    });

    console.log("✅ Dropdown de tipo de criticidades actualizado.");
}

// Cargar criticidades basado en el tipo seleccionado
async function loadCriticidadesByTipo() {
    const tipoSelect = document.getElementById('tipocriticidadDropdown');
    const critSelect = document.getElementById('criticidadDropdown');
    const tipoId = tipoSelect.value;

    critSelect.innerHTML = '<option value="">Cargando...</option>';
    critSelect.disabled = true;

    if (!tipoId) {
        critSelect.innerHTML = '<option value="">Seleccione un tipo primero</option>';
        return;
    }

    const criticidades = await fetchCriticidadesByTipo(tipoId);
    
    critSelect.innerHTML = '<option value="">Seleccione una criticidad</option>';
    criticidades.forEach(crit => {
        const option = document.createElement('option');
        option.value = crit.id;
        option.textContent = crit.name;
        critSelect.appendChild(option);
    });
    
    critSelect.disabled = false;
}

// Modificar la función existente para poblar el dropdown de tipos
function populateTipoCriticidadDropdown(tipocriticidades) {
    const select = document.getElementById('tipocriticidadDropdown');
    select.innerHTML = '<option value="">Seleccione un tipo de criticidad</option>';

    tipocriticidades.forEach(tipocriticidad => {
        const option = document.createElement('option');
        option.value = tipocriticidad.id;
        option.textContent = tipocriticidad.name;
        select.appendChild(option);
    });
}