// _AppAdmin/js/ui.js - Funciones de interfaz de usuario para Admin Users (sin módulos ES6)

// AdminUI - Funciones de interfaz
window.AdminUI = {
    // Configuración de paginación
    pagination: {
        currentPage: 1,
        perPage: 10,
        
        // Actualizar controles de paginación
        update(response) {
            const paginationEl = document.querySelector('.pagination');
            if (!paginationEl) return;

            paginationEl.innerHTML = '';

            if (response.total_pages <= 1) {
                return; // No mostrar paginación si solo hay una página
            }

            // Botón Previous
            const prevLi = document.createElement('li');
            prevLi.className = `page-item ${!response.has_previous ? 'disabled' : ''}`;
            if (response.has_previous) {
                prevLi.innerHTML = `<a class="page-link" href="#" data-page="${response.previous_page_number}">Anterior</a>`;
            } else {
                prevLi.innerHTML = `<span class="page-link">Anterior</span>`;
            }
            paginationEl.appendChild(prevLi);

            // Información de página actual
            const currentLi = document.createElement('li');
            currentLi.className = 'page-item disabled';
            currentLi.innerHTML = `<span class="page-link">Página ${response.current_page} de ${response.total_pages}</span>`;
            paginationEl.appendChild(currentLi);

            // Botón Next
            const nextLi = document.createElement('li');
            nextLi.className = `page-item ${!response.has_next ? 'disabled' : ''}`;
            if (response.has_next) {
                nextLi.innerHTML = `<a class="page-link" href="#" data-page="${response.next_page_number}">Siguiente</a>`;
            } else {
                nextLi.innerHTML = `<span class="page-link">Siguiente</span>`;
            }
            paginationEl.appendChild(nextLi);

            // Agregar event listeners a los enlaces de paginación
            paginationEl.addEventListener('click', function(e) {
                e.preventDefault();
                const page = e.target.dataset.page;
                if (page && !e.target.closest('.disabled')) {
                    window.AdminEvents.goToPage(parseInt(page));
                }
            });
        }
    },

    // Funciones de tabla
    table: {
        // Actualizar contenido de la tabla
        updateUsers(users) {
            const tbody = document.getElementById('usersTableBody');
            if (!tbody) return;

            if (!users || users.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="5" class="text-center">
                            <i class="bi bi-person-x"></i>
                            No hay usuarios registrados
                        </td>
                    </tr>`;
                return;
            }

            tbody.innerHTML = users.map(user => `
                <tr>
                    <td>
                        <strong>${user.email}</strong>
                        ${user.first_name && user.last_name ? `<br><small>${user.first_name} ${user.last_name}</small>` : ''}
                    </td>
                    <td>
                        <span class="badge ${this.getRoleBadgeClass(user.role)}">${this.getRoleDisplayName(user.role)}</span>
                    </td>
                    <td>
                        <small>${this.formatDate(user.date_joined)}</small>
                    </td>
                    <td>
                        <span class="badge ${user.is_active ? 'bg-success' : 'bg-secondary'}">
                            ${user.is_active ? 'Activo' : 'Inactivo'}
                        </span>
                    </td>
                    <td>
                        <button class="btn btn-primary btn-sm me-1" 
                                onclick="AdminEvents.openEditModal(${user.id})" 
                                title="Editar usuario">
                            <i class="bi bi-pencil-square"></i>
                        </button>
                        <button class="btn btn-danger btn-sm" 
                                onclick="AdminEvents.openDeleteModal(${user.id}, '${user.email}')" 
                                title="Eliminar usuario">
                            <i class="bi bi-trash"></i>
                        </button>
                    </td>
                </tr>
            `).join('');
        },

        // Obtener clase CSS para el badge del rol
        getRoleBadgeClass(role) {
            const roleClasses = {
                'AdministradorPrincipal': 'bg-danger',
                'Administrador': 'bg-warning',
                'Supervisor': 'bg-primary',
                'Usuario': 'bg-info'
            };
            return roleClasses[role] || 'bg-secondary';
        },

        // Obtener nombre de visualización del rol
        getRoleDisplayName(role) {
            const roleNames = {
                'AdministradorPrincipal': 'Administrador Principal',
                'Administrador': 'Administrador',
                'Supervisor': 'Supervisor',
                'Usuario': 'Usuario'
            };
            return roleNames[role] || role;
        },

        // Formatear fecha
        formatDate(dateString) {
            if (!dateString) return '';
            const date = new Date(dateString);
            return date.toLocaleDateString('es-ES', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
            });
        }
    }
};

console.log('✅ AdminUI cargado');
