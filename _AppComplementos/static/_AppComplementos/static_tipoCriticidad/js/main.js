// main.js - Punto de entrada a la _AppHome
async function loadTipCriticidadesPag(page = 1) {
    console.log("🔄 Cargando los tipos de criticidades...");
    console.log("🔄 Cargando los tipos de criticidades para la página:", page);
    const perPage = document.getElementById('recordsPerPage').value;

    // 🔹 Cargar tipos de criticidades paginados
    const data = await fetchTipCriticidades(page, perPage);
    console.log("🔄 datos paginados de tipo de criticidades:", data);
    if (data) renderTipCriticidades(data);

    // 🔹 Cargar todas las criticidades sin paginación y verificar en consola
    const allCriticidades = await fetchAllCriticidades();
    if (allCriticidades) populateCriticidadDropdown(allCriticidades);
    console.log("📡 Todas las criticidades:", allCriticidades);
    
}

// 🔹 Función para poblar el dropdown con todas las criticidades
function populateCriticidadDropdown(criticidades) {
    const select = document.getElementById('criticidadDropdown');
    select.innerHTML = '<option value="">Seleccione una criticidad</option>'; // Resetear opciones

    criticidades.forEach(criticidad => {
        const option = document.createElement('option');
        option.value = criticidad.id;
        option.textContent = criticidad.name;
        select.appendChild(option);
    });

    console.log("✅ Dropdown de criticidades actualizado.");
}