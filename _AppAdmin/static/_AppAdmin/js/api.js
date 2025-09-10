// _AppAdmin/js/api.js - Manejo de APIs y llamadas AJAX
class AdminAPI {
    constructor() {
        this.baseUrl = '/admin_panel/usuarios/';
        this.csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }

    // Crear usuario
    async createUser(formData) {
        try {
            const response = await fetch(`${this.baseUrl}crear/`, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': this.csrfToken
                },
                body: formData
            });

            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            } else {
                throw new Error('La respuesta del servidor no es JSON válido');
            }
        } catch (error) {
            console.error('Error en createUser:', error);
            throw error;
        }
    }

    // Editar usuario
    async updateUser(userId, formData) {
        try {
            const response = await fetch(`${this.baseUrl}editar/${userId}/`, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': this.csrfToken
                },
                body: formData
            });

            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            } else {
                throw new Error('La respuesta del servidor no es JSON válido');
            }
        } catch (error) {
            console.error('Error en updateUser:', error);
            throw error;
        }
    }

    // Eliminar usuario
    async deleteUser(userId) {
        try {
            const response = await fetch('/admin_panel/usuarios/eliminar/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': this.csrfToken
                },
                body: `user_id=${userId}`
            });

            return await response.json();
        } catch (error) {
            console.error('Error en deleteUser:', error);
            throw error;
        }
    }
}

// Exportar instancia para uso global
window.AdminAPI = new AdminAPI();