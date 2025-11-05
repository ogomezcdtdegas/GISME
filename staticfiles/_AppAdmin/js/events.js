// _AppAdmin/js/events.js - Manejo de eventos para Admin Users (sin módulos ES6)

// Variable global para control de carga
let isLoading = false;

// AdminEvents - Manejo de eventos
window.AdminEvents = {
    
    // Función helper para extraer mensajes de error de la respuesta
    extractErrorMessage(errorResponse, defaultMessage = 'Error desconocido') {
        if (!errorResponse) return defaultMessage;
        
        if (typeof errorResponse === 'string') {
            return errorResponse;
        }
        
        if (typeof errorResponse === 'object') {
            // Buscar errores de email primero (más común)
            if (errorResponse.email) {
                const emailError = errorResponse.email;
                return Array.isArray(emailError) ? emailError[0] : emailError;
            }
            
            // Si no hay error de email, buscar el primer error disponible
            const firstErrorKey = Object.keys(errorResponse)[0];
            if (firstErrorKey && errorResponse[firstErrorKey]) {
                const firstError = errorResponse[firstErrorKey];
                return Array.isArray(firstError) ? firstError[0] : firstError;
            }
        }
        
        return defaultMessage;
    },
    
    // Función principal para cargar usuarios
    async loadUsers(page = 1, search = '', perPage = 10) {
        // Protección contra cargas múltiples
        if (isLoading) {
            //console.log('⏳ Ya hay una carga en proceso, saltando...');
            return;
        }

        //console.log(`� Cargando usuarios - Página: ${page}, Búsqueda: "${search}", Por página: ${perPage}`);
        
        isLoading = true;
        try {
            const response = await window.AdminAPI.users.listarPaginado(page, perPage, '-date_joined', search);

            if (response && response.results) {
                //console.log(`✅ Usuarios cargados exitosamente - ${response.results.length} usuarios encontrados`);
                //console.log('📊 Respuesta completa:', response);  // Debug log
                
                // Actualizar tabla
                window.AdminUI.table.updateUsers(response.results);
                
                // Actualizar paginación
                window.AdminUI.pagination.update(response);
                window.AdminUI.pagination.currentPage = page;
                
                // Mostrar total de registros
                this.updateRecordsInfo(response);
            } else {
                //console.error('❌ Respuesta de API inválida:', response);
                this.showError('Error al cargar usuarios: Respuesta inválida del servidor');
            }
        } catch (error) {
            //console.error('❌ Error al cargar usuarios:', error);
            this.showError('Error al cargar usuarios: ' + error.message);
        } finally {
            isLoading = false;
            //console.log('✅ Carga completada - isLoading resetado');
        }
    },

    // Navegar a una página específica
    async goToPage(page) {
        const searchValue = document.getElementById('searchInput')?.value || '';
        const perPageValue = parseInt(document.getElementById('recordsPerPage')?.value) || 10;
        
        //console.log(`📄 Navegando a página ${page}`);
        await this.loadUsers(page, searchValue, perPageValue);
    },

    // Cambiar registros por página
    async updatePerPage() {
        const recordsPerPage = document.getElementById('recordsPerPage');
        if (recordsPerPage) {
            const perPage = parseInt(recordsPerPage.value) || 10;
            const searchValue = document.getElementById('searchInput')?.value || '';
            
            //console.log(`📊 Cambiando a ${perPage} registros por página`);
            await this.loadUsers(1, searchValue, perPage);
        }
    },

    // Realizar búsqueda
    async performSearch(searchTerm) {
        const perPageValue = parseInt(document.getElementById('recordsPerPage')?.value) || 10;
        
        //console.log(`🔍 Realizando búsqueda: "${searchTerm}"`);
        await this.loadUsers(1, searchTerm, perPageValue);
    },

    // Limpiar búsqueda
    async clearSearch() {
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.value = '';
            const perPageValue = parseInt(document.getElementById('recordsPerPage')?.value) || 10;
            
            //console.log('🧹 Limpiando búsqueda');
            await this.loadUsers(1, '', perPageValue);
        }
    },

    // Abrir modal de edición
    async openEditModal(userId) {
        //console.log(`✏️ Abriendo modal de edición para usuario ${userId}`);
        
        // Validar que tenemos un ID válido
        if (!userId || userId === 'undefined') {
            //console.error('❌ ID de usuario no válido:', userId);
            this.showError('Error: ID de usuario no válido');
            return;
        }
        
        try {
            // Obtener datos del usuario
            const response = await window.AdminAPI.users.obtenerPorId(userId);
            
            if (response && response.success) {
                const user = response.data;
                //console.log('✅ Datos del usuario obtenidos:', user);
                
                // Llenar formulario de edición
                document.getElementById('editUserId').value = user.id;
                document.getElementById('editEmail').value = user.email;
                document.getElementById('editFirstName').value = user.first_name || '';
                document.getElementById('editLastName').value = user.last_name || '';
                document.getElementById('editRole').value = user.role || '';
                
                // Establecer el estado is_active correctamente
                const isActiveCheckbox = document.getElementById('editIsActive');
                if (isActiveCheckbox) {
                    isActiveCheckbox.checked = user.is_active === true;
                    //console.log('🔍 Estado del usuario:', user.is_active, '→ Checkbox marcado:', isActiveCheckbox.checked);
                }
                
                // Verificar que el ID se estableció correctamente
                const setId = document.getElementById('editUserId').value;
                //console.log('🔍 ID establecido en el formulario:', setId);
                
                // Mostrar modal
                const modal = new bootstrap.Modal(document.getElementById('editUserModal'));
                modal.show();
            } else {
                //console.error('❌ Error obteniendo datos del usuario:', response);
                this.showError('Error al obtener datos del usuario');
            }
        } catch (error) {
            //console.error('❌ Error al cargar usuario para edición:', error);
            this.showError('Error al cargar usuario: ' + error.message);
        }
    },

    // Abrir modal de eliminación
    async openDeleteModal(userId, userEmail) {
        //console.log(`🗑️ Abriendo modal de eliminación para usuario ${userId} (${userEmail})`);
        
        // Usar SweetAlert2 para confirmación de eliminación
        const result = await Swal.fire({
            title: '¿Está seguro?',
            text: `Va a eliminar al usuario "${userEmail}"`,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '#6c757d',
            confirmButtonText: 'Sí, eliminar',
            cancelButtonText: 'Cancelar',
            reverseButtons: true
        });

        if (result.isConfirmed) {
            try {
                await window.AdminAPI.users.eliminar(userId);
                //console.log(`✅ Usuario ${userId} eliminado exitosamente`);
                
                // Recargar usuarios
                const currentPage = window.AdminUI.pagination.currentPage || 1;
                const searchValue = document.getElementById('searchInput')?.value || '';
                const perPageValue = parseInt(document.getElementById('recordsPerPage')?.value) || 10;
                
                await this.loadUsers(currentPage, searchValue, perPageValue);
                
                // Mostrar alerta de éxito
                Swal.fire({
                    title: '¡Éxito!',
                    text: `Usuario "${userEmail}" eliminado exitosamente`,
                    icon: 'success',
                    confirmButtonText: 'OK',
                    confirmButtonColor: '#28a745'
                });
            } catch (error) {
                //console.error('❌ Error al eliminar usuario:', error);
                // Mostrar alerta de error
                Swal.fire({
                    title: 'Error',
                    text: 'Error al eliminar usuario: ' + error.message,
                    icon: 'error',
                    confirmButtonText: 'OK',
                    confirmButtonColor: '#dc3545'
                });
            }
        }
    },

    // Crear nuevo usuario
    async createUser(userData) {
        //console.log('➕ Creando nuevo usuario:', userData);
        
        try {
            const response = await window.AdminAPI.users.crear(userData);
            
            if (response && response.success) {
                //console.log('✅ Usuario creado exitosamente:', response);
                
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
                
                // Mostrar alerta de éxito
                Swal.fire({
                    title: '¡Éxito!',
                    text: 'Usuario creado exitosamente',
                    icon: 'success',
                    confirmButtonText: 'OK',
                    confirmButtonColor: '#28a745'
                });
                return response;
            } else {
                //console.error('❌ Error en respuesta de creación:', response);
                
                // Extraer mensaje específico del error usando helper
                const errorMessage = this.extractErrorMessage(response.error);
                
                // Mostrar alerta de error con mensaje específico
                Swal.fire({
                    title: 'Error al crear usuario',
                    text: errorMessage,
                    icon: 'error',
                    confirmButtonText: 'OK',
                    confirmButtonColor: '#dc3545'
                });
                return null;
            }
        } catch (error) {
            //console.error('❌ Error al crear usuario:', error);
            // Mostrar alerta de error
            Swal.fire({
                title: 'Error',
                text: 'Error al crear usuario: ' + error.message,
                icon: 'error',
                confirmButtonText: 'OK',
                confirmButtonColor: '#dc3545'
            });
            return null;
        }
    },

    // Actualizar usuario existente
    async updateUser(userData) {
        //console.log('📝 Actualizando usuario:', userData);
        
        try {
            const response = await window.AdminAPI.users.actualizar(userData.id, userData);
            
            if (response && response.success) {
                //console.log('✅ Usuario actualizado exitosamente:', response);
                
                // Cerrar modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('editUserModal'));
                if (modal) {
                    modal.hide();
                }
                
                // Recargar usuarios
                const currentPage = window.AdminUI.pagination.currentPage || 1;
                const searchValue = document.getElementById('searchInput')?.value || '';
                const perPageValue = parseInt(document.getElementById('recordsPerPage')?.value) || 10;
                
                await this.loadUsers(currentPage, searchValue, perPageValue);
                
                // Mostrar alerta de éxito
                Swal.fire({
                    title: '¡Éxito!',
                    text: 'Usuario actualizado exitosamente',
                    icon: 'success',
                    confirmButtonText: 'OK',
                    confirmButtonColor: '#28a745'
                });
                return response;
            } else {
                //console.error('❌ Error en respuesta de actualización:', response);
                
                // Extraer mensaje específico del error usando helper
                const errorMessage = this.extractErrorMessage(response.error);
                
                // Mostrar alerta de error con mensaje específico
                Swal.fire({
                    title: 'Error al actualizar usuario',
                    text: errorMessage,
                    icon: 'error',
                    confirmButtonText: 'OK',
                    confirmButtonColor: '#dc3545'
                });
                return null;
            }
        } catch (error) {
            //console.error('❌ Error al actualizar usuario:', error);
            // Mostrar alerta de error
            Swal.fire({
                title: 'Error',
                text: 'Error al actualizar usuario: ' + error.message,
                icon: 'error',
                confirmButtonText: 'OK',
                confirmButtonColor: '#dc3545'
            });
            return null;
        }
    },

    // Actualizar información de registros
    updateRecordsInfo(response) {
        const recordsInfo = document.getElementById('recordsInfo');
        if (recordsInfo && response) {
            // Calcular per_page basado en la cantidad de resultados o usar el valor del selector
            const perPageElement = document.getElementById('recordsPerPage');
            const perPage = perPageElement ? parseInt(perPageElement.value) || 10 : 10;
            
            const currentPage = parseInt(response.current_page) || 1;
            const totalCount = parseInt(response.total_count) || 0;
            
            //console.log(`📊 Actualizando info: página ${currentPage}, total ${totalCount}, por página ${perPage}`);
            
            if (totalCount === 0) {
                recordsInfo.textContent = 'No hay registros para mostrar';
                return;
            }
            
            const start = ((currentPage - 1) * perPage) + 1;
            const end = Math.min(currentPage * perPage, totalCount);
            
            // Verificar que los valores sean válidos
            if (isNaN(start) || isNaN(end) || isNaN(totalCount)) {
                //console.error('❌ Valores inválidos para el conteo:', { start, end, totalCount, currentPage, perPage });
                recordsInfo.textContent = `Mostrando registros (total: ${totalCount})`;
                return;
            }
            
            recordsInfo.textContent = `Mostrando ${start}-${end} de ${totalCount} registros`;
            //console.log(`✅ Info actualizada: Mostrando ${start}-${end} de ${totalCount} registros`);
        }
    },

    // Mostrar mensaje de error
    showError(message) {
        //console.error('❌', message);
        Swal.fire({
            title: 'Error',
            text: message,
            icon: 'error',
            confirmButtonText: 'OK',
            confirmButtonColor: '#dc3545'
        });
    },

    // Mostrar mensaje de éxito
    showSuccess(message) {
        //console.log('✅', message);
        Swal.fire({
            title: '¡Éxito!',
            text: message,
            icon: 'success',
            confirmButtonText: 'OK',
            confirmButtonColor: '#28a745'
        });
    },

    // Configurar todos los event listeners
    setupEventListeners() {
        //console.log('🔧 Configurando event listeners...');

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

        // Formulario de edición de usuario
        const editUserForm = document.getElementById('editUserForm');
        if (editUserForm) {
            editUserForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                
                // Recopilar datos del formulario - obtener ID directamente del campo
                const userId = document.getElementById('editUserId').value;
                
                // Validar que tenemos un ID
                if (!userId || userId === 'undefined') {
                    //console.error('❌ ID de usuario no válido:', userId);
                    this.showError('Error: ID de usuario no válido');
                    return;
                }
                
                // Recopilar datos manualmente para asegurar que is_active se incluya siempre
                const isActiveElement = document.getElementById('editIsActive');
                const userData = {
                    id: userId,
                    email: document.getElementById('editEmail').value,
                    first_name: document.getElementById('editFirstName').value,
                    last_name: document.getElementById('editLastName').value,
                    role_update: document.getElementById('editRole').value,
                    is_active: isActiveElement ? isActiveElement.checked : true
                };
                
                //console.log('📝 Datos de usuario para actualización:', userData);
                //console.log('🔍 Estado is_active específico:', userData.is_active, typeof userData.is_active);
                
                // Actualizar usuario
                await this.updateUser(userData);
            });
        }

        //console.log('✅ Event listeners configurados');
    },

    // Inicializar la página
    async init() {
        //console.log('🚀 Inicializando AdminEvents...');
        
        // Configurar event listeners
        this.setupEventListeners();
        
        // Cargar usuarios iniciales
        await this.loadUsers(1, '', 10);
        
        //console.log('✅ AdminEvents inicializado correctamente');
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
    //console.log('📄 DOM cargado, inicializando AdminEvents...');
    
    // Esperar a que se carguen AdminAPI y AdminUI
    const checkDependencies = () => {
        if (window.AdminAPI && window.AdminUI) {
            window.AdminEvents.init();
        } else {
            //console.log('⏳ Esperando a que se carguen las dependencias...');
            setTimeout(checkDependencies, 100);
        }
    };
    
    checkDependencies();
});

//console.log('✅ AdminEvents cargado');
