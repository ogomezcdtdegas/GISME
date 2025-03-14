// api.js - Manejo de peticiones AJAX con Django
async function fetchEquipos(page = 1, perPage) {
    try {
        const response = await fetch(`/?page=${page}&per_page=${perPage}`, {
            method: "GET",
            headers: { "X-Requested-With": "XMLHttpRequest" }
        });
        return await response.json();
    } catch (error) {
        console.error("❌ Error al cargar equipos:", error);
    }
}

async function crearEquipo(serial, sap, marca) {
    try {
        const response = await fetch("/crear-equipo/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": getCSRFToken(),
            },
            body: JSON.stringify({ serial, sap, marca }),
        });
        return await response.json();
    } catch (error) {
        console.error("❌ Error al registrar equipo:", error);
    }
}

async function actualizarEquipo(id, serial, sap, marca, csrftoken) {
    try {
        const response = await fetch(`/editar-equipo/${id}/`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken,
                "X-Requested-With": "XMLHttpRequest"
            },
            body: JSON.stringify({ serial, sap, marca })
        });
        return await response.json();
    } catch (error) {
        console.error("❌ Error en la actualización:", error);
    }
}
