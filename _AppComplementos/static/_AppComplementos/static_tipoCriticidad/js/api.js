// api.js - Manejo de peticiones AJAX con Django
async function fetchTipCriticidades(page = 1, perPage) {
    try {
        const response = await fetch(`/complementos/tipCriticidades/?page=${page}&per_page=${perPage}`, {
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

async function fetchAllCriticidades() {
    try {
        const response = await fetch("/complementos/listar-todo-criticidad/", {
            method: "GET",
            headers: { "X-Requested-With": "XMLHttpRequest" }
        });

        const data = await response.json();
        return data.results;  // 🔹 Lista completa de criticidades
    } catch (error) {
        console.error("❌ Error al cargar todas las criticidades:", error);
        return [];
    }
}

async function crearTipCriticidad(name, criticidad_id) {
    try {
        const response = await fetch("/complementos/crear-tipCriticidad/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": getCSRFToken(),
            },
            body: JSON.stringify({ name, criticidad_id }),
        });

        const result = await response.json(); // Convertir la respuesta en JSON

        // 🔹 Si la API devuelve success: false, tratamos el mensaje como error
        if (!result.success) {
            return { success: false, error: result.message || "Error desconocido" };
        }

        return result;

    } catch (error) {
        console.error("❌ Error en la solicitud:", error);
        return { success: false, error: "Error de conexión con el servidor" };
    }
}

async function actualizarTipCriticidad(id, name, tipoCriticidadId, criticidadId, csrftoken) {
    try {
        console.log("📡 Enviando actualización:", { id, name, tipoCriticidadId, criticidadId });

        const response = await fetch(`/complementos/editar-tipCriticidad/${id}/`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken,
                "X-Requested-With": "XMLHttpRequest"
            },
            body: JSON.stringify({ 
                name, 
                tipo_criticidad_id: tipoCriticidadId,  
                criticidad_id: criticidadId 
            })
        });

        return await response.json();
    } catch (error) {
        console.error("❌ Error en la actualización:", error);
        return { success: false, error: "Error en la actualización" };
    }
}
