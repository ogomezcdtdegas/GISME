// _AppAdmin/js/events.js - Manejo de eventos para Admin Users (sin módulos ES6)

// Variable global para control de carga
let isLoading = false;

// AdminEvents - Manejo de eventos
window.AdminEvents = {
    
    // Función principal para cargar usuarios
    async loadUsers(page = 1, search = '', perPage = 10) {
        // Protección contra cargas múltiples
        if (isLoading) {
            console.log('⏳ Ya hay una carga en proceso, saltando...');
            return;
        }

        console.log(`� Cargando usuarios - Página: ${page}, Búsqueda: "${search}", Por página: ${perPage}`);
        
        isLoading = true;
        try {
            const response = await window.AdminAPI.users.listarPaginado(page, perPage, '-date_joined', search);

            if (response && response.results) {
                console.log(`✅ Usuarios cargados exitosamente - ${response.results.length} usuarios encontrados`);
                
                // Actualizar tabla
                window.AdminUI.table.updateUsers(response.results);
                
                // Actualizar paginación
                window.AdminUI.pagination.update(response);
                window.AdminUI.pagination.currentPage = page;
                
                // Mostrar total de registros
                this.updateRecordsInfo(response);
            } else {
                console.error('❌ Respuesta de API inválida:', response);
                this.showError('Error al cargar usuarios: Respuesta inválida del servidor');
            }
        } catch (error) {
            console.error('❌ Error al cargar usuarios:', error);
            this.showError('Error al cargar usuarios: ' + error.message);
        } finally {
            isLoading = false;
            console.log('✅ Carga completada - isLoading resetado');
        }
    },

    // Navegar a una página específica
    async goToPage(page) {
        const searchValue = document.getElementById('searchInput')?.value || '';
        const perPageValue = parseInt(document.getElementById('recordsPerPage')?.value) || 10;
        
        console.log(`📄 Navegando a página ${page}`);
        await this.loadUsers(page, searchValue, perPageValue);
    },

    // Cambiar registros por página
    async updatePerPage() {
        const recordsPerPage = document.getElementById('recordsPerPage');
        if (recordsPerPage) {
            const perPage = parseInt(recordsPerPage.value) || 10;
            const searchValue = document.getElementById('searchInput')?.value || '';
            
            console.log(`📊 Cambiando a ${perPage} registros por página`);
            await this.loadUsers(1, searchValue, perPage);
        }
    },

    // Realizar búsqueda
    async performSearch(searchTerm) {
        const perPageValue = parseInt(document.getElementById('recordsPerPage')?.value) || 10;
        
        console.log(`🔍 Realizando búsqueda: "${searchTerm}"`);
        await this.loadUsers(1, searchTerm, perPageValue);
    },

    // Limpiar búsqueda
    async clearSearch() {
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.value = '';
            const perPageValue = parseInt(document.getElementById('recordsPerPage')?.value) || 10;
            
            console.log('🧹 Limpiando búsqueda');
            await this.loadUsers(1, '', perPageValue);
        }
    },

    // Abrir modal de edición
    async openEditModal(userId) {
        console.log(`✏️ Abriendo modal de edición para usuario ${userId}`);
        // TODO: Implementar modal de edición
        alert(`Editar usuario ${userId} - Funcionalidad pendiente`);
    },

    // Abrir modal de eliminación
    async openDeleteModal(userId, userEmail) {
        console.log(`🗑️ Abriendo modal de eliminación para usuario ${userId} (${userEmail})`);
        
        if (confirm(`¿Está seguro de que desea eliminar al usuario "${userEmail}"?`)) {
            try {
                await window.AdminAPI.users.eliminar(userId);
                console.log(`✅ Usuario ${userId} eliminado exitosamente`);
                
                // Recargar usuarios
                const currentPage = window.AdminUI.pagination.currentPage || 1;
                const searchValue = document.getElementById('searchInput')?.value || '';
                const perPageValue = parseInt(document.getElementById('recordsPerPage')?.value) || 10;
                
                await this.loadUsers(currentPage, searchValue, perPageValue);
                
                this.showSuccess(`Usuario "${userEmail}" eliminado exitosamente`);
            } catch (error) {
                console.error('❌ Error al eliminar usuario:', error);
                this.showError('Error al eliminar usuario: ' + error.message);
            }
        }
    },

    // Crear nuevo usuario
    async createUser(userData) {
        console.log('➕ Creando nuevo usuario:', userData);
        
        try {
            const response = await window.AdminAPI.users.crear(userData);
            
            if (response && response.success) {
                console.log('✅ Usuario creado exitosamente:', response);
                
                // Cerrar modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('createUserModal'));
                if (modal) {
                    modal.hide();
                }
                
                // Limpiar formulario
                document.getElementById('createUserForm').reset();
                
                // Recargar usuarios
                const currentPage = window.AdminUI.pagination.currentPage || 1;
                const searchValue = document.getElementById('searchInput')?.value || '';
                const perPageValue = parseInt(document.getElementById('recordsPerPage')?.value) || 10;
                
                await this.loadUsers(currentPage, searchValue, perPageValue);
                
                this.showSuccess('Usuario creado exitosamente');
                return response;
            } else {
                console.error('❌ Error en respuesta de creación:', response);
                this.showError('Error al crear usuario: ' + (response.error || 'Error desconocido'));
                return null;
            }
        } catch (error) {
            console.error('❌ Error al crear usuario:', error);
            this.showError('Error al crear usuario: ' + error.message);
            return null;
        }
    },

    // Actualizar información de registros
    updateRecordsInfo(response) {
        const recordsInfo = document.getElementById('recordsInfo');
        if (recordsInfo && response) {
            const start = ((response.current_page - 1) * response.per_page) + 1;
            const end = Math.min(start + response.per_page - 1, response.total_count);
            recordsInfo.textContent = `Mostrando ${start}-${end} de ${response.total_count} registros`;
        }
    },

    // Mostrar mensaje de error
    showError(message) {
        // TODO: Implementar sistema de notificaciones más sofisticado
        console.error('❌', message);
        alert('Error: ' + message);
    },

    // Mostrar mensaje de éxito
    showSuccess(message) {
        // TODO: Implementar sistema de notificaciones más sofisticado
        console.log('✅', message);
        alert('Éxito: ' + message);
    },

    // Configurar todos los event listeners
    setupEventListeners() {
        console.log('🔧 Configurando event listeners...');

        // Búsqueda
        const searchInput = document.getElementById('searchInput');
        const clearSearchBtn = document.getElementById('clearSearch');
        
        if (searchInput) {
            let searchTimeout;
            searchInput.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    this.performSearch(e.target.value);
                }, 300); // Debounce de 300ms
            });
            
            searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    clearTimeout(searchTimeout);
                    this.performSearch(e.target.value);
                }
            });
        }
        
        if (clearSearchBtn) {
            clearSearchBtn.addEventListener('click', () => {
                this.clearSearch();
            });
        }

        // Selector de registros por página
        const recordsPerPage = document.getElementById('recordsPerPage');
        if (recordsPerPage) {
            recordsPerPage.addEventListener('change', () => {
                this.updatePerPage();
            });
        }

        // Formulario de creación de usuario
        const createUserForm = document.getElementById('createUserForm');
        if (createUserForm) {
            createUserForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                
                // Recopilar datos del formulario
                const formData = new FormData(createUserForm);
                const userData = {
                    email: formData.get('email'),
                    first_name: formData.get('first_name'),
                    last_name: formData.get('last_name'),
                    role: formData.get('role')
                };
                
                // Crear usuario
                await this.createUser(userData);
            });
        }

        console.log('✅ Event listeners configurados');
    },

    // Inicializar la página
    async init() {
        console.log('🚀 Inicializando AdminEvents...');
        
        // Configurar event listeners
        this.setupEventListeners();
        
        // Cargar usuarios iniciales
        await this.loadUsers(1, '', 10);
        
        console.log('✅ AdminEvents inicializado correctamente');
    }
};

// Función global para la paginación (para el template)
window.updatePagination = function() {
    window.AdminEvents.updatePerPage();
};

// Funciones globales para los botones (para el template)
window.openEditModal = function(userId) {
    window.AdminEvents.openEditModal(userId);
};

window.deleteUser = function(userId, userEmail) {
    window.AdminEvents.openDeleteModal(userId, userEmail);
};

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    console.log('📄 DOM cargado, inicializando AdminEvents...');
    
    // Esperar a que se carguen AdminAPI y AdminUI
    const checkDependencies = () => {
        if (window.AdminAPI && window.AdminUI) {
            window.AdminEvents.init();
        } else {
            console.log('⏳ Esperando a que se carguen las dependencias...');
            setTimeout(checkDependencies, 100);
        }
    };
    
    checkDependencies();
});

console.log('✅ AdminEvents cargado');
