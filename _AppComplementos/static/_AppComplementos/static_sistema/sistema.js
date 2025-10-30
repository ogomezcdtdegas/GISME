// sistema.js - Gestión de sistemas
import { SistemaAPI } from '../../../../../static/js/global/api/services/sistemas.js';
import { UbicacionAPI } from '../../../../../static/js/global/api/services/ubicaciones.js';

class SistemaManager {
    constructor() {
        this.sistemaAPI = SistemaAPI;
        this.ubicacionAPI = UbicacionAPI;
        this.sistemas = [];
        this.ubicaciones = [];
        this.currentPage = 1;
        this.recordsPerPage = 10;
        this.filteredData = [];
        this.sortField = null;
        this.sortDirection = 'asc';
        
        this.initEventListeners();
        this.loadUbicaciones();
        this.loadSistemas();
    }

    initEventListeners() {
        // Formulario de registro
        const form = document.getElementById('sistemaForm');
        if (form) {
            form.addEventListener('submit', (e) => this.handleSubmit(e));
        }

        // Búsqueda
        const searchBtn = document.getElementById('searchBtn');
        const searchInput = document.getElementById('searchInput');
        const clearSearch = document.getElementById('clearSearch');

        if (searchBtn) {
            searchBtn.addEventListener('click', () => this.performSearch());
        }

        if (searchInput) {
            searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.performSearch();
                }
            });
        }

        if (clearSearch) {
            clearSearch.addEventListener('click', () => this.clearSearch());
        }
    }

    async loadUbicaciones() {
        try {
            //console.log('🔄 Cargando ubicaciones para el selector...');
            //console.log('📍 Servicio ubicaciones disponible:', this.ubicacionAPI);
            
            // Usar el método list() con page_size grande (mismo que usa ubicacion.js)
            const response = await this.ubicacionAPI.list({ page: 1, page_size: 1000 });
            //console.log('📦 Respuesta completa de ubicaciones:', response);
            
            if (response && response.success && response.data && response.data.results) {
                this.ubicaciones = response.data.results;
                //console.log('📍 Ubicaciones extraídas:', this.ubicaciones);
                this.populateUbicacionSelect();
                //console.log('✅ Ubicaciones cargadas para selector:', this.ubicaciones.length);
            } else if (response && response.results) {
                this.ubicaciones = response.results;
                //console.log('📍 Ubicaciones extraídas (directo):', this.ubicaciones);
                this.populateUbicacionSelect();
                //console.log('✅ Ubicaciones cargadas para selector:', this.ubicaciones.length);
            } else {
                //console.error('❌ Error al cargar ubicaciones para selector - respuesta:', response);
                this.showAlert('Error al cargar ubicaciones: No se encontraron datos', 'error');
            }
        } catch (error) {
            //console.error('❌ Error al cargar ubicaciones:', error);
            this.showAlert('Error al cargar ubicaciones: ' + error.message, 'error');
        }
    }

    populateUbicacionSelect() {
        const select = document.getElementById('ubicacion');
        if (!select) return;

        // Limpiar opciones existentes (excepto la primera)
        select.innerHTML = '<option value="">Seleccione una ubicación...</option>';

        // Agregar opciones de ubicaciones
        this.ubicaciones.forEach(ubicacion => {
            const option = document.createElement('option');
            option.value = ubicacion.id;
            option.textContent = ubicacion.nombre; // Solo mostrar el nombre
            select.appendChild(option);
        });
    }

    async loadSistemas() {
        try {
            //console.log('🔄 Cargando sistemas...');
            const response = await this.sistemaAPI.list({ page_size: 100 });
            
            //console.log('📦 Respuesta recibida:', response);
            
            if (response && (response.results || response.data?.results)) {
                this.sistemas = response.results || response.data.results;
                this.filteredData = [...this.sistemas];
                this.updateTable();
                this.updatePagination();
                //console.log('✅ Sistemas cargados exitosamente:', this.sistemas.length);
            } else if (response.success && response.data) {
                this.sistemas = response.data.results || response.data;
                this.filteredData = [...this.sistemas];
                this.updateTable();
                this.updatePagination();
                //console.log('✅ Sistemas cargados exitosamente:', this.sistemas.length);
            } else {
                //console.error('❌ Estructura de respuesta inesperada:', response);
                this.showAlert('Error al cargar sistemas: Respuesta inesperada', 'error');
            }
        } catch (error) {
            //console.error('❌ Error al cargar sistemas:', error);
            this.showAlert('Error al cargar sistemas', 'error');
        }
    }

    async handleSubmit(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const data = {
            tag: formData.get('tag'),
            sistema_id: formData.get('sistema_id'),
            identificacion_medidor: formData.get('identificacion_medidor'),
            ubicacion: formData.get('ubicacion')
        };

        // Validaciones
        if (!data.tag || !data.sistema_id || !data.identificacion_medidor || !data.ubicacion) {
            this.showAlert('Todos los campos son obligatorios', 'error');
            return;
        }

        try {
            //console.log('📤 Enviando datos:', data);
            const response = await this.sistemaAPI.create(data);
            
            if (response.success) {
                this.showAlert('Sistema creado exitosamente', 'success');
                e.target.reset();
                await this.loadSistemas();
            } else {
                console.error('❌ Error del servidor:', response);
                // Mostrar error específico del backend
                const errorMsg = response.error || 'Error al crear sistema';
                this.showAlert(errorMsg, 'error');
            }
        } catch (error) {
            //console.error('❌ Error al crear sistema:', error);
            this.showAlert('Error de conexión con el servidor', 'error');
        }
    }

    async deleteSistema(id) {
        const result = await Swal.fire({
            title: '¿Estás seguro?',
            text: "Esta acción no se puede deshacer",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '#3085d6',
            confirmButtonText: 'Sí, eliminar',
            cancelButtonText: 'Cancelar'
        });

        if (result.isConfirmed) {
            try {
                const response = await this.sistemaAPI.delete(id);
                if (response.success) {
                    this.showAlert('Sistema eliminado exitosamente', 'success');
                    await this.loadSistemas();
                } else {
                    //console.error('❌ Error del servidor:', response);
                    const errorMsg = response.error || 'Error al eliminar sistema';
                    this.showAlert(errorMsg, 'error');
                }
            } catch (error) {
                //console.error('Error al eliminar:', error);
                this.showAlert('Error de conexión con el servidor', 'error');
            }
        }
    }

    async editSistema(id) {
        const sistema = this.sistemas.find(s => s.id === id);
        if (!sistema) return;

        // Crear las opciones para el select de ubicaciones
        const ubicacionOptions = this.ubicaciones.map(ubicacion => 
            `<option value="${ubicacion.id}" ${ubicacion.id === sistema.ubicacion ? 'selected' : ''}>${ubicacion.nombre}</option>`
        ).join('');

        const { value: formValues } = await Swal.fire({
            title: 'Editar Sistema',
            html: `
                <div class="mb-3">
                    <label for="swal-tag" class="form-label">Nombre:</label>
                    <input type="text" id="swal-tag" class="form-control" value="${sistema.tag}">
                </div>
                <div class="mb-3">
                    <label for="swal-sistema-id" class="form-label">MAC Gateway:</label>
                    <input type="text" id="swal-sistema-id" class="form-control" value="${sistema.sistema_id}">
                </div>
                <div class="mb-3">
                    <label for="swal-identificacion-medidor" class="form-label">Identificación del Medidor:</label>
                    <input type="text" id="swal-identificacion-medidor" class="form-control" value="${sistema.identificacion_medidor || ''}">
                </div>
                <div class="mb-3">
                    <label for="swal-ubicacion" class="form-label">Ubicación:</label>
                    <select id="swal-ubicacion" class="form-control">
                        <option value="">Seleccione una ubicación...</option>
                        ${ubicacionOptions}
                    </select>
                </div>
            `,
            focusConfirm: false,
            showCancelButton: true,
            confirmButtonText: 'Actualizar',
            cancelButtonText: 'Cancelar',
            preConfirm: () => {
                const tag = document.getElementById('swal-tag').value;
                const sistemaId = document.getElementById('swal-sistema-id').value;
                const identificacionMedidor = document.getElementById('swal-identificacion-medidor').value;
                const ubicacion = document.getElementById('swal-ubicacion').value;

                if (!tag || !sistemaId || !identificacionMedidor || !ubicacion) {
                    Swal.showValidationMessage('Todos los campos son obligatorios');
                    return false;
                }

                return { tag, sistema_id: sistemaId, identificacion_medidor: identificacionMedidor, ubicacion };
            }
        });

        if (formValues) {
            try {
                const response = await this.sistemaAPI.update(id, formValues);
                if (response.success) {
                    this.showAlert('Sistema actualizado exitosamente', 'success');
                    await this.loadSistemas();
                } else {
                    //console.error('❌ Error del servidor:', response);
                    // Mostrar error específico del backend
                    const errorMsg = response.error || 'Error al actualizar sistema';
                    this.showAlert(errorMsg, 'error');
                }
            } catch (error) {
                //console.error('Error al actualizar:', error);
                this.showAlert('Error de conexión con el servidor', 'error');
            }
        }
    }

    updateTable() {
        const tbody = document.getElementById('sistemasTableBody');
        if (!tbody) return;

        tbody.innerHTML = '';

        const start = (this.currentPage - 1) * this.recordsPerPage;
        const end = start + this.recordsPerPage;
        const pageData = this.filteredData.slice(start, end);

        if (pageData.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center">No se encontraron sistemas</td>
                </tr>
            `;
            return;
        }

        pageData.forEach(sistema => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${sistema.tag}</td>
                <td>${sistema.sistema_id}</td>
                <td>${sistema.identificacion_medidor || 'N/A'}</td>
                <td>${sistema.ubicacion_nombre}</td>
                <td>${sistema.ubicacion_coordenadas}</td>
                <td>
                    <button class="btn btn-sm btn-warning me-1" onclick="sistemaManager.editSistema('${sistema.id}')">
                        <i class="bi bi-pencil"></i>
                    </button>
                    ${window.IS_SUPERUSER ? `
                    <button class="btn btn-sm btn-danger" onclick="sistemaManager.deleteSistema('${sistema.id}')">
                        <i class="bi bi-trash"></i>
                    </button>` : ''}
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    updatePagination() {
        const totalPages = Math.ceil(this.filteredData.length / this.recordsPerPage);
        const paginationContainer = document.getElementById('pagination');
        
        if (!paginationContainer) return;

        let paginationHTML = '<nav><ul class="pagination justify-content-center">';

        // Botón anterior
        paginationHTML += `
            <li class="page-item ${this.currentPage === 1 ? 'disabled' : ''}">
                <a class="page-link" href="#" onclick="sistemaManager.goToPage(${this.currentPage - 1})">Anterior</a>
            </li>
        `;

        // Números de página
        for (let i = 1; i <= totalPages; i++) {
            if (i === this.currentPage) {
                paginationHTML += `<li class="page-item active"><span class="page-link">${i}</span></li>`;
            } else {
                paginationHTML += `<li class="page-item"><a class="page-link" href="#" onclick="sistemaManager.goToPage(${i})">${i}</a></li>`;
            }
        }

        // Botón siguiente
        paginationHTML += `
            <li class="page-item ${this.currentPage === totalPages ? 'disabled' : ''}">
                <a class="page-link" href="#" onclick="sistemaManager.goToPage(${this.currentPage + 1})">Siguiente</a>
            </li>
        `;

        paginationHTML += '</ul></nav>';
        paginationContainer.innerHTML = paginationHTML;
    }

    goToPage(page) {
        const totalPages = Math.ceil(this.filteredData.length / this.recordsPerPage);
        if (page < 1 || page > totalPages) return;
        
        this.currentPage = page;
        this.updateTable();
        this.updatePagination();
    }

    performSearch() {
        const searchTerm = document.getElementById('searchInput').value.toLowerCase().trim();
        
        if (searchTerm === '') {
            this.filteredData = [...this.sistemas];
        } else {
            this.filteredData = this.sistemas.filter(sistema => 
                sistema.tag.toLowerCase().includes(searchTerm) ||
                sistema.sistema_id.toLowerCase().includes(searchTerm) ||
                sistema.ubicacion_nombre.toLowerCase().includes(searchTerm)
            );
        }
        
        this.currentPage = 1;
        this.updateTable();
        this.updatePagination();
    }

    clearSearch() {
        document.getElementById('searchInput').value = '';
        this.filteredData = [...this.sistemas];
        this.currentPage = 1;
        this.updateTable();
        this.updatePagination();
    }

    sortTable(field) {
        if (this.sortField === field) {
            this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            this.sortField = field;
            this.sortDirection = 'asc';
        }

        this.filteredData.sort((a, b) => {
            let aVal = a[field];
            let bVal = b[field];

            if (this.sortDirection === 'asc') {
                return aVal > bVal ? 1 : -1;
            } else {
                return aVal < bVal ? 1 : -1;
            }
        });

        this.updateSortIcons(field);
        this.updateTable();
    }

    updateSortIcons(field) {
        document.querySelectorAll('[id$="-sort-icon"]').forEach(icon => {
            icon.className = 'bi bi-arrow-up-down ms-1';
        });

        const icon = document.getElementById(`${field}-sort-icon`);
        if (icon) {
            icon.className = this.sortDirection === 'asc' ? 
                'bi bi-arrow-up ms-1' : 'bi bi-arrow-down ms-1';
        }
    }

    showAlert(message, type = 'info') {
        const alertClass = {
            'success': 'alert-success',
            'error': 'alert-danger',
            'warning': 'alert-warning',
            'info': 'alert-info'
        }[type];

        Swal.fire({
            title: type === 'error' ? 'Error' : type === 'success' ? 'Éxito' : 'Información',
            text: message,
            icon: type === 'error' ? 'error' : type === 'success' ? 'success' : 'info',
            confirmButtonText: 'OK'
        });
    }
}

// Función global para cambiar registros por página
window.updatePagination = function() {
    const select = document.getElementById('recordsPerPage');
    if (select && window.sistemaManager) {
        window.sistemaManager.recordsPerPage = parseInt(select.value);
        window.sistemaManager.currentPage = 1;
        window.sistemaManager.updateTable();
        window.sistemaManager.updatePagination();
    }
};

// Función global para ordenamiento
window.sortTable = function(field) {
    if (window.sistemaManager) {
        window.sistemaManager.sortTable(field);
    }
};

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    window.sistemaManager = new SistemaManager();
});

// También exportar para uso como módulo
export default SistemaManager;
