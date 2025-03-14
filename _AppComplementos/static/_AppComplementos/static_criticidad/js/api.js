// api.js - Manejo de peticiones AJAX con Django
async function fetchCriticidades(page = 1, perPage) {
    try {
        const response = await fetch(`/complementos/?page=${page}&per_page=${perPage}`, {
            method: "GET",
            headers: { "X-Requested-With": "XMLHttpRequest" }
        });
        const data = await response.json();

        console.log("📡 Datos recibidos:", data);  // <-- Verificar en la consola

        return data; 
    } catch (error) {
        console.error("❌ Error al cargar criticidades:", error);
        return { criticidades: [] };  // Devolver un objeto vacío para evitar errores en .forEach()
    }
}

async function crearCriticidad(name) {
    try {
        const response = await fetch("crear-criticidad/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": getCSRFToken(),
            },
            body: JSON.stringify({ name }),
        });
        return await response.json();
    } catch (error) {
        console.error("❌ Error al registrar la criticidad:", error);
    }
}

async function actualizarCriticidad(id, name, csrftoken) {
    try {
        const response = await fetch(`editar-criticidad/${id}/`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken,
                "X-Requested-With": "XMLHttpRequest"
            },
            body: JSON.stringify({ name })
        });
        return await response.json();
    } catch (error) {
        console.error("❌ Error en la actualización:", error);
    }
}
