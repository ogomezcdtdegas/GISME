// _AppAdmin/js/api.js - Manejo de APIs y llamadas AJAX refactorizado
class AdminAPI {
    constructor() {
        this.baseUrl = '/admin_panel/api/';
        this.csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }

    // Obtener lista de usuarios
    async getUsers(page = 1, search = '', ordering = '-date_joined') {
        try {
            const params = new URLSearchParams({
                page: page,
                search: search,
                ordering: ordering
            });

            const response = await fetch(`${this.baseUrl}users/?${params}`, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                }
            });

            return await response.json();
        } catch (error) {
            console.error('Error en getUsers:', error);
            throw error;
        }
    }

    // Crear usuario
    async createUser(userData) {
        try {
            const response = await fetch(`${this.baseUrl}users/create/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': this.csrfToken
                },
                body: JSON.stringify(userData)
            });

            return await response.json();
        } catch (error) {
            console.error('Error en createUser:', error);
            throw error;
        }
    }

    // Obtener usuario específico
    async getUser(userId) {
        try {
            const response = await fetch(`${this.baseUrl}users/${userId}/`, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                }
            });

            return await response.json();
        } catch (error) {
            console.error('Error en getUser:', error);
            throw error;
        }
    }

    // Editar usuario
    async updateUser(userId, userData) {
        try {
            const response = await fetch(`${this.baseUrl}users/${userId}/`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': this.csrfToken
                },
                body: JSON.stringify(userData)
            });

            return await response.json();
        } catch (error) {
            console.error('Error en updateUser:', error);
            throw error;
        }
    }

    // Eliminar usuario
    async deleteUser(userId) {
        try {
            const response = await fetch(`${this.baseUrl}users/${userId}/delete/`, {
                method: 'DELETE',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': this.csrfToken
                }
            });

            return await response.json();
        } catch (error) {
            console.error('Error en deleteUser:', error);
            throw error;
        }
    }

    // Obtener roles disponibles
    async getRoles() {
        try {
            const response = await fetch(`${this.baseUrl}roles/`, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                }
            });

            return await response.json();
        } catch (error) {
            console.error('Error en getRoles:', error);
            throw error;
        }
    }
}

// Exportar instancia para uso global
window.AdminAPI = new AdminAPI();