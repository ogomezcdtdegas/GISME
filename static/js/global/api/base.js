// base.js - Funciones base para comunicación con la API

export const BaseAPI = {
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    },

    async request(endpoint, options = {}) {
        const defaultHeaders = {
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": this.getCSRFToken()
        };

        try {
            const response = await fetch(endpoint, {
                ...options,
                headers: { ...defaultHeaders, ...options.headers }
            });
            
            // Verificar si la respuesta es JSON
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                const textResponse = await response.text();
                console.error('Respuesta no es JSON:', textResponse.substring(0, 200));
                return {
                    success: false,
                    error: "El servidor devolvió una respuesta inválida"
                };
            }
            
            const data = await response.json();
            
            // Si hay error de duplicado
            if (response.status === 400 && data.error?.includes('duplicate key value violates')) {
                return {
                    success: false,
                    error: "Ya existe un registro con estos valores"
                };
            }
            
            // Si hay otros errores del servidor
            if (!response.ok) {
                return {
                    success: false,
                    error: data.error || "Error en la operación"
                };
            }

            return data;
        } catch (error) {
            console.error("❌ Error en la solicitud:", error);
            return { 
                success: false, 
                error: "Error de conexión con el servidor" 
            };
        }
    },

    // Métodos CRUD base
    async get(endpoint, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return this.request(`${endpoint}?${queryString}`, { method: 'GET' });
    },

    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    async put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },

    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }
};
