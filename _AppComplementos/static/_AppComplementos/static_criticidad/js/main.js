// main.js - Punto de entrada a la _AppHome
async function loadCriticidadesPag(page = 1) {
    console.log("🔄 Cargando criticidades...");
    const perPage = document.getElementById('recordsPerPage').value;
    const data = await fetchCriticidades(page, perPage);
    if (data) renderCriticidades(data);
}