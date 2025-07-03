// api.js - Manejo de peticiones AJAX con Django
async function fetchProductos(page = 1, perPage) {
    try {
        const response = await fetch(`/complementos/listar-todo-productos/?page=${page}&per_page=${perPage}`, {
            method: "GET",
            headers: { "X-Requested-With": "XMLHttpRequest" }
        });
        const data = await response.json();

        console.log("📡 Datos recibidos:", data);  // <-- Verificar en la consola

        return data; 
    } catch (error) {
        console.error("❌ Error al cargar productos:", error);
        return { productos: [] };  // Devolver un objeto vacío para evitar errores en .forEach()
    }
}

async function fetchAllTipoCriticidades() {
    try {
        const response = await fetch("/complementos/listar-todo-tipocriticidad/", {
            method: "GET",
            headers: { "X-Requested-With": "XMLHttpRequest" }
        });

        const data = await response.json();
        return data.results;  // 🔹 Lista completa de criticidades
    } catch (error) {
        console.error("❌ Error al cargar todas los tipos de criticidades:", error);
        return [];
    }
}

async function crearProducto(name, producto_id) {
    try {
        const response = await fetch("/complementos/crear-producto/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": getCSRFToken(),
            },
            body: JSON.stringify({ name, producto_id }),
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

// Obtener criticidades por tipo de criticidad
async function fetchCriticidadesByTipo(tipoId) {
    try {
        const response = await fetch(`/complementos/criticidades-por-tipo/${tipoId}/`, {
            headers: { "X-Requested-With": "XMLHttpRequest" }
        });
        
        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        // Transforma a formato {id, name} que espera tu frontend
        return data.map(item => ({
            id: item.value,
            name: item.label
        }));
        
    } catch (error) {
        console.error("Error al cargar criticidades:", error);
        showErrorToast("No se pudieron cargar las criticidades");
        return [];
    }
}

// Crear producto con ambos campos
async function crearProductoCompleto(name, tipoCriticidadId, criticidadId) {
    try {
        const response = await fetch("/complementos/crear-producto-completo/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": getCSRFToken(),
            },
            body: JSON.stringify({ 
                name, 
                tipo_criticidad_id: tipoCriticidadId,
                criticidad_id: criticidadId 
            }),
        });
        return await response.json();
    } catch (error) {
        console.error("❌ Error al crear producto:", error);
        return { success: false, error: "Error de conexión" };
    }
}

// Actualizar producto existente
async function actualizarProductoCompleto(id, name, tipoCriticidadId, criticidadId) {
    try {
        const response = await fetch(`/complementos/actualizar-producto/${id}/`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": getCSRFToken(),
            },
            body: JSON.stringify({ 
                name, 
                tipo_criticidad_id: tipoCriticidadId,
                criticidad_id: criticidadId 
            }),
        });
        
        const data = await response.json();
        
        // Si es un error de duplicado
        if (response.status === 400 && data.error && data.error.includes('duplicate key value violates')) {
            return {
                success: false,
                error: "Ya existe un producto con esta combinación de Tipo de Criticidad y Criticidad"
            };
        }
        
        // Si hay otros errores del servidor
        if (!response.ok) {
            return {
                success: false,
                error: data.error || "Error al actualizar el producto"
            };
        }

        return data;
    } catch (error) {
        console.error("❌ Error al actualizar producto:", error);
        return { success: false, error: "Error de conexión con el servidor" };
    }
}