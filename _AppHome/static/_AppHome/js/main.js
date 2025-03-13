// main.js - Punto de entrada a la _AppHome
async function loadEquiposPag(page = 1) {
    console.log("🔄 Cargando equipos...");
    const perPage = document.getElementById('recordsPerPage').value;
    const data = await fetchEquipos(page, perPage);
    if (data) renderEquipos(data);
}