// _AppAdmin/js/events.js - Manejo de eventos y listeners
class AdminEvents {
    constructor() {
        this.ui = window.AdminUI;
        this.api = window.AdminAPI;
    }

    // Inicializar todos los event listeners
    init() {
        this.setupFilterEvents();
        this.setupFormEvents();
        this.setupModalEvents();
        this.setupGlobalFunctions();
    }

    // Event listeners para filtros
    setupFilterEvents() {
        // Búsqueda en tiempo real
        if (this.ui.searchInput) {
            this.ui.searchInput.addEventListener('input', () => {
                this.ui.filterUsers();
            });
        }

        // Filtro por rol
        if (this.ui.roleFilter) {
            this.ui.roleFilter.addEventListener('change', () => {
                this.ui.filterUsers();
            });
        }
    }

    // Event listeners para formularios
    setupFormEvents() {
        // Formulario de creación
        const createForm = document.getElementById('createUserForm');
        if (createForm) {
            createForm.addEventListener('submit', (e) => {
                this.handleCreateUser(e);
            });
        }

        // Formulario de edición
        const editForm = document.getElementById('editUserForm');
        if (editForm) {
            editForm.addEventListener('submit', (e) => {
                this.handleEditUser(e);
            });
        }
    }

    // Event listeners para modales
    setupModalEvents() {
        // Modal de acceso denegado (auto-mostrar)
        const accessDeniedModal = document.getElementById('accessDeniedModal');
        if (accessDeniedModal) {
            new bootstrap.Modal(accessDeniedModal).show();
        }
    }

    // Configurar funciones globales (para compatibilidad con onclick)
    setupGlobalFunctions() {
        // Función global para editar usuario
        window.editarUsuario = (userId) => {
            this.ui.showModal('edit', { userId });
        };

        // Función global para eliminar usuario
        window.eliminarUsuario = (userId, userEmail) => {
            this.ui.showModal('delete', { userId, userEmail });
        };

        // Función global para confirmar eliminación
        window.confirmarEliminacion = () => {
            this.handleDeleteUser();
        };
    }

    // Manejar creación de usuario
    async handleCreateUser(event) {
        event.preventDefault();
        
        const form = event.target;
        this.ui.clearFormErrors(form);
        
        try {
            const formData = new FormData(form);
            const result = await this.api.createUser(formData);
            
            if (result.success) {
                this.ui.hideModal('create');
                this.ui.showSuccessMessage(result.message);
                this.ui.reloadAfterDelay();
                form.reset();
            } else {
                if (result.errors) {
                    this.ui.showFormErrors(form, result.errors);
                } else {
                    alert('Error: ' + (result.message || 'Error desconocido'));
                }
            }
        } catch (error) {
            console.error('Error al crear usuario:', error);
            alert('Error al crear usuario: ' + error.message);
        }
    }

    // Manejar edición de usuario
    async handleEditUser(event) {
        event.preventDefault();
        
        const form = event.target;
        this.ui.clearFormErrors(form);
        
        try {
            const formData = new FormData(form);
            const userId = document.getElementById('editUserId').value;
            const result = await this.api.updateUser(userId, formData);
            
            if (result.success) {
                this.ui.hideModal('edit');
                this.ui.showSuccessMessage(result.message);
                this.ui.reloadAfterDelay();
            } else {
                if (result.errors) {
                    this.ui.showFormErrors(form, result.errors);
                } else {
                    alert('Error: ' + (result.message || 'Error desconocido'));
                }
            }
        } catch (error) {
            console.error('Error al actualizar usuario:', error);
            alert('Error al actualizar usuario: ' + error.message);
        }
    }

    // Manejar eliminación de usuario
    async handleDeleteUser() {
        const userId = window.userIdToDelete;
        if (!userId) return;
        
        try {
            const result = await this.api.deleteUser(userId);
            
            if (result.success) {
                this.ui.hideModal('delete');
                this.ui.showSuccessMessage('Usuario eliminado exitosamente');
                this.ui.reloadAfterDelay();
            } else {
                alert('Error: ' + (result.message || 'Error al eliminar usuario'));
            }
        } catch (error) {
            console.error('Error al eliminar usuario:', error);
            alert('Error al eliminar usuario: ' + error.message);
        }
        
        // Limpiar variable global
        window.userIdToDelete = null;
    }
}

// Exportar instancia para uso global
window.AdminEvents = new AdminEvents();