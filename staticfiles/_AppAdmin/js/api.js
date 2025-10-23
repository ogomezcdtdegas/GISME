// _AppAdmin/js/api.js - API para gestión de usuarios admin (sin módulos ES6)

// Función para obtener CSRF token
function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value;
}

// Función para realizar peticiones AJAX básicas
async function makeAPIRequest(url, options = {}) {
    const defaultHeaders = {
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFToken": getCSRFToken()
    };

    try {
        console.log('🌐 API Request:', url, options);
        
        const response = await fetch(url, {
            ...options,
            headers: { ...defaultHeaders, ...options.headers }
        });

        // Intentar leer el contenido JSON independientemente del status
        let data;
        try {
            data = await response.json();
        } catch (jsonError) {
            console.error('❌ Error parsing JSON:', jsonError);
            data = { success: false, error: `HTTP ${response.status}: ${response.statusText}` };
        }

        // Si la respuesta HTTP no es OK pero tenemos datos JSON, retornar los datos
        // (esto permite que los errores 400 con mensajes específicos lleguen al código)
        if (!response.ok) {
            // Si el JSON no tiene estructura de error, crear una
            if (!data.hasOwnProperty('success')) {
                data = { success: false, error: `HTTP ${response.status}: ${response.statusText}`, details: data };
            }
        }

        console.log('📦 API Response:', data);
        return data;
        
    } catch (error) {
        console.error('❌ API Error:', error);
        return { success: false, error: error.message };
    }
}

// AdminAPI - API para usuarios admin
window.AdminAPI = {
    // Métodos de usuarios
    users: {
        async listarPaginado(page = 1, perPage = 10, ordering = '-date_joined', search = '') {
            const params = new URLSearchParams({
                page: page,
                per_page: perPage,
                ordering: ordering
            });
            
            if (search && search.trim()) {
                params.append('search', search.trim());
            }
            
            const url = `/admin_panel/api/users/paginated/?${params.toString()}`;
            return await makeAPIRequest(url);
        },

        async obtenerPorId(id) {
            const url = `/admin_panel/api/users/${id}/`;
            return await makeAPIRequest(url);
        },

        async crear(userData) {
            const url = `/admin_panel/api/users/create/`;
            return await makeAPIRequest(url, {
                method: 'POST',
                body: JSON.stringify(userData)
            });
        },

        async actualizar(id, userData) {
            const url = `/admin_panel/api/users/${id}/`;
            return await makeAPIRequest(url, {
                method: 'PUT',
                body: JSON.stringify(userData)
            });
        },

        async eliminar(id) {
            const url = `/admin_panel/api/users/${id}/delete/`;
            return await makeAPIRequest(url, {
                method: 'DELETE'
            });
        }
    },

    // Métodos de roles
    roles: {
        async obtenerTodos() {
            const url = `/admin_panel/api/roles/`;
            return await makeAPIRequest(url);
        }
    }
};

console.log('✅ AdminAPI cargado');
