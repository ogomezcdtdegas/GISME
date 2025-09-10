// _AppAdmin/js/ui.js - Manipulación de interfaz y filtros
class AdminUI {
    constructor() {
        this.searchInput = null;
        this.roleFilter = null;
        this.userRows = [];
        this.modals = {};
    }

    // Inicializar elementos de UI
    init() {
        this.searchInput = document.getElementById('searchInput');
        this.roleFilter = document.getElementById('roleFilter');
        this.userRows = document.querySelectorAll('.user-row');
        
        // Inicializar modales
        this.modals = {
            create: document.getElementById('createUserModal'),
            edit: document.getElementById('editUserModal'),
            delete: document.getElementById('deleteModal'),
            accessDenied: document.getElementById('accessDeniedModal')
        };
    }

    // Filtrar usuarios en tiempo real
    filterUsers() {
        if (!this.searchInput || !this.roleFilter) return;

        const searchTerm = this.searchInput.value.toLowerCase();
        const selectedRole = this.roleFilter.value;

        this.userRows.forEach(row => {
            const email = row.dataset.email || '';
            const name = row.dataset.name || '';
            const role = row.dataset.role || '';

            const matchesSearch = email.includes(searchTerm) || name.includes(searchTerm);
            const matchesRole = selectedRole === '' || role === selectedRole;

            row.style.display = (matchesSearch && matchesRole) ? '' : 'none';
        });
    }

    // Llenar modal de edición con datos del usuario
    fillEditModal(userId) {
        const button = event.target.closest('button');
        const userRow = button.closest('tr');
        
        // Extraer datos de la fila
        const email = userRow.querySelector('td:nth-child(1) strong').textContent;
        const fullName = userRow.querySelector('td:nth-child(2)').textContent.trim();
        const nameParts = fullName.split(' ');
        const firstName = nameParts[0] || '';
        const lastName = nameParts.slice(1).join(' ') || '';
        
        // Obtener el rol del badge
        const roleBadge = userRow.querySelector('td:nth-child(3) .badge');
        let role = 'supervisor';
        if (roleBadge) {
            const roleText = roleBadge.textContent.trim();
            if (roleText === 'AdministradorPrincipal') role = 'admin_principal';
            else if (roleText === 'Administrador') role = 'admin';
            else if (roleText === 'Supervisor') role = 'supervisor';
        }
        
        // Llenar el modal de edición
        document.getElementById('editUserId').value = userId;
        document.getElementById('editEmail').value = email;
        document.getElementById('editFirstName').value = firstName;
        document.getElementById('editLastName').value = lastName;
        document.getElementById('editRole').value = role;
    }

    // Preparar modal de eliminación
    prepareDeleteModal(userId, userEmail) {
        window.userIdToDelete = userId;
        document.getElementById('userToDelete').textContent = userEmail;
    }

    // Limpiar errores de formularios
    clearFormErrors(form) {
        const inputs = form.querySelectorAll('input, select');
        inputs.forEach(input => {
            input.classList.remove('is-invalid');
        });
    }

    // Mostrar errores en formularios
    showFormErrors(form, errors) {
        for (const [fieldName, errorList] of Object.entries(errors)) {
            const input = form.querySelector(`[name="${fieldName}"]`);
            if (input) {
                input.classList.add('is-invalid');
                let feedback = input.nextElementSibling;
                if (!feedback || !feedback.classList.contains('invalid-feedback')) {
                    feedback = document.createElement('div');
                    feedback.className = 'invalid-feedback';
                    input.parentNode.appendChild(feedback);
                }
                feedback.textContent = errorList[0];
            }
        }
    }

    // Mostrar mensaje de éxito
    showSuccessMessage(message) {
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-success alert-dismissible fade show';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.querySelector('.container').insertBefore(alertDiv, document.querySelector('.row'));
        
        // Auto-remove después de 5 segundos
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }

    // Mostrar modales
    showModal(modalType, options = {}) {
        const modal = this.modals[modalType];
        if (modal) {
            if (modalType === 'edit' && options.userId) {
                this.fillEditModal(options.userId);
            }
            if (modalType === 'delete' && options.userId && options.userEmail) {
                this.prepareDeleteModal(options.userId, options.userEmail);
            }
            new bootstrap.Modal(modal).show();
        }
    }

    // Cerrar modales
    hideModal(modalType) {
        const modal = this.modals[modalType];
        if (modal) {
            const bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) {
                bsModal.hide();
            }
        }
    }

    // Recargar página después de operación exitosa
    reloadAfterDelay(delay = 1000) {
        setTimeout(() => location.reload(), delay);
    }
}

// Exportar instancia para uso global
window.AdminUI = new AdminUI();