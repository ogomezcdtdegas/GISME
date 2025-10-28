// ubicacion.js - Versión original funcional
import { UbicacionAPI } from '../../../../../static/js/global/api/services/ubicaciones.js';

class UbicacionManager {
    constructor() {
        this.apiService = UbicacionAPI;
        this.ubicaciones = [];
        this.currentPage = 1;
        this.recordsPerPage = 10;
        this.filteredData = [];
        this.sortField = null;
        this.sortDirection = 'asc';
        this.map = null;
        this.markers = [];
        
        this.initEventListeners();
        this.loadUbicaciones();
    }

    initEventListeners() {
        // Formulario de registro
        const form = document.getElementById('ubicacionForm');
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

        // Botón de mapa
        const showMapBtn = document.getElementById('showMapBtn');
        if (showMapBtn) {
            showMapBtn.addEventListener('click', () => this.showMap());
        }
    }

    async loadUbicaciones() {
        try {
            console.log('🔄 Cargando ubicaciones...');
            const response = await this.apiService.list({ page_size: 100 }); // Cargar muchas para mostrar todas
            
            console.log('📦 Respuesta recibida:', response);
            
            // La respuesta puede venir directamente con results o envuelta en success
            if (response && (response.results || response.data?.results)) {
                this.ubicaciones = response.results || response.data.results;
                this.filteredData = [...this.ubicaciones];
                this.updateTable();
                this.updatePagination();
                console.log('✅ Ubicaciones cargadas exitosamente:', this.ubicaciones.length);
            } else if (response.success && response.data) {
                // Si viene en formato success/data
                this.ubicaciones = response.data.results || response.data;
                this.filteredData = [...this.ubicaciones];
                this.updateTable();
                this.updatePagination();
                console.log('✅ Ubicaciones cargadas exitosamente:', this.ubicaciones.length);
            } else {
                console.error('❌ Estructura de respuesta inesperada:', response);
                this.showAlert('Error al cargar ubicaciones: Respuesta inesperada', 'error');
            }
        } catch (error) {
            console.error('❌ Error al cargar ubicaciones:', error);
            this.showAlert('Error al cargar ubicaciones', 'error');
        }
    }

    async handleSubmit(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const data = {
            nombre: formData.get('nombre'),
            latitud: parseFloat(formData.get('latitud')),
            longitud: parseFloat(formData.get('longitud'))
        };

        // Validaciones
        if (!data.nombre || !data.latitud || !data.longitud) {
            this.showAlert('Todos los campos son obligatorios', 'error');
            return;
        }

        if (data.latitud < -90 || data.latitud > 90) {
            this.showAlert('La latitud debe estar entre -90 y 90 grados', 'error');
            return;
        }

        if (data.longitud < -180 || data.longitud > 180) {
            this.showAlert('La longitud debe estar entre -180 y 180 grados', 'error');
            return;
        }

        try {
            console.log('📤 Enviando datos:', data);
            const response = await this.apiService.create(data);
            
            if (response.success) {
                this.showAlert('Ubicación creada exitosamente', 'success');
                e.target.reset();
                await this.loadUbicaciones();
            } else {
                console.error('❌ Error del servidor:', response.error);
                this.showAlert('Error al crear ubicación: ' + response.error, 'error');
            }
        } catch (error) {
            console.error('❌ Error al crear ubicación:', error);
            this.showAlert('Error al crear ubicación', 'error');
        }
    }

    async deleteUbicacion(id) {
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
                const response = await this.apiService.delete(id);
                if (response.success) {
                    this.showAlert('Ubicación eliminada exitosamente', 'success');
                    await this.loadUbicaciones();
                } else {
                    this.showAlert('Error al eliminar ubicación: ' + response.error, 'error');
                }
            } catch (error) {
                console.error('Error al eliminar:', error);
                this.showAlert('Error al eliminar ubicación', 'error');
            }
        }
    }

    async editUbicacion(id) {
        const ubicacion = this.ubicaciones.find(u => u.id === id);
        if (!ubicacion) return;

        const { value: formValues } = await Swal.fire({
            title: 'Editar Ubicación',
            html: `
                <div class="mb-3">
                    <label for="swal-nombre" class="form-label">Nombre:</label>
                    <input type="text" id="swal-nombre" class="form-control" value="${ubicacion.nombre}">
                </div>
                <div class="mb-3">
                    <label for="swal-latitud" class="form-label">Latitud:</label>
                    <input type="number" step="0.0000001" id="swal-latitud" class="form-control" value="${ubicacion.latitud}">
                </div>
                <div class="mb-3">
                    <label for="swal-longitud" class="form-label">Longitud:</label>
                    <input type="number" step="0.0000001" id="swal-longitud" class="form-control" value="${ubicacion.longitud}">
                </div>
            `,
            focusConfirm: false,
            showCancelButton: true,
            confirmButtonText: 'Actualizar',
            cancelButtonText: 'Cancelar',
            preConfirm: () => {
                const nombre = document.getElementById('swal-nombre').value;
                const latitud = parseFloat(document.getElementById('swal-latitud').value);
                const longitud = parseFloat(document.getElementById('swal-longitud').value);

                if (!nombre || isNaN(latitud) || isNaN(longitud)) {
                    Swal.showValidationMessage('Todos los campos son obligatorios');
                    return false;
                }

                if (latitud < -90 || latitud > 90) {
                    Swal.showValidationMessage('La latitud debe estar entre -90 y 90 grados');
                    return false;
                }

                if (longitud < -180 || longitud > 180) {
                    Swal.showValidationMessage('La longitud debe estar entre -180 y 180 grados');
                    return false;
                }

                return { nombre, latitud, longitud };
            }
        });

        if (formValues) {
            try {
                const response = await this.apiService.update(id, formValues);
                if (response.success) {
                    this.showAlert('Ubicación actualizada exitosamente', 'success');
                    await this.loadUbicaciones();
                } else {
                    this.showAlert('Error al actualizar ubicación: ' + response.error, 'error');
                }
            } catch (error) {
                console.error('Error al actualizar:', error);
                this.showAlert('Error al actualizar ubicación', 'error');
            }
        }
    }

    updateTable() {
        const tbody = document.getElementById('ubicacionesTableBody');
        if (!tbody) return;

        tbody.innerHTML = '';

        const start = (this.currentPage - 1) * this.recordsPerPage;
        const end = start + this.recordsPerPage;
        const pageData = this.filteredData.slice(start, end);

        if (pageData.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="4" class="text-center">No se encontraron ubicaciones</td>
                </tr>
            `;
            return;
        }

        pageData.forEach(ubicacion => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${ubicacion.nombre}</td>
                <td>${parseFloat(ubicacion.latitud).toFixed(6)}°</td>
                <td>${parseFloat(ubicacion.longitud).toFixed(6)}°</td>
                <td>
                    <button class="btn btn-sm btn-warning me-1" onclick="ubicacionManager.editUbicacion('${ubicacion.id}')">
                        <i class="bi bi-pencil"></i>
                    </button>
                    ${window.IS_SUPERUSER ? `
                    <button class="btn btn-sm btn-danger" onclick="ubicacionManager.deleteUbicacion('${ubicacion.id}')">
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
                <a class="page-link" href="#" onclick="ubicacionManager.goToPage(${this.currentPage - 1})">Anterior</a>
            </li>
        `;

        // Números de página
        for (let i = 1; i <= totalPages; i++) {
            if (i === this.currentPage) {
                paginationHTML += `<li class="page-item active"><span class="page-link">${i}</span></li>`;
            } else {
                paginationHTML += `<li class="page-item"><a class="page-link" href="#" onclick="ubicacionManager.goToPage(${i})">${i}</a></li>`;
            }
        }

        // Botón siguiente
        paginationHTML += `
            <li class="page-item ${this.currentPage === totalPages ? 'disabled' : ''}">
                <a class="page-link" href="#" onclick="ubicacionManager.goToPage(${this.currentPage + 1})">Siguiente</a>
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
            this.filteredData = [...this.ubicaciones];
        } else {
            this.filteredData = this.ubicaciones.filter(ubicacion => 
                ubicacion.nombre.toLowerCase().includes(searchTerm) ||
                ubicacion.latitud.toString().includes(searchTerm) ||
                ubicacion.longitud.toString().includes(searchTerm)
            );
        }
        
        this.currentPage = 1;
        this.updateTable();
        this.updatePagination();
    }

    clearSearch() {
        document.getElementById('searchInput').value = '';
        this.filteredData = [...this.ubicaciones];
        this.currentPage = 1;
        this.updateTable();
        this.updatePagination();
    }

    showMap() {
        // Mostrar el modal
        const mapModal = new bootstrap.Modal(document.getElementById('mapModal'));
        const modalElement = document.getElementById('mapModal');
        
        // Añadir listener para cuando se cierre el modal
        modalElement.addEventListener('hidden.bs.modal', () => {
            if (this.map) {
                this.map.remove();
                this.map = null;
                this.markers = [];
            }
        }, { once: true });
        
        mapModal.show();

        // Inicializar el mapa después de que el modal se muestre
        setTimeout(() => {
            this.initMap();
        }, 300);
    }

    initMap() {
        const mapContainer = document.getElementById('map');
        if (!mapContainer) return;

        // Destruir el mapa anterior si existe
        if (this.map) {
            this.map.remove();
            this.map = null;
            this.markers = [];
        }

        // Limpiar el contenedor del mapa
        mapContainer.innerHTML = '';

        // Crear el mapa nuevo
        this.map = L.map('map').setView([4.6097102, -74.0817500], 6);

        // Añadir capa de tiles
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(this.map);

        // Añadir marcadores para cada ubicación
        this.ubicaciones.forEach(ubicacion => {
            const marker = L.marker([ubicacion.latitud, ubicacion.longitud])
                .addTo(this.map)
                .bindPopup(`
                    <strong>${ubicacion.nombre}</strong><br>
                    Lat: ${parseFloat(ubicacion.latitud).toFixed(6)}°<br>
                    Lng: ${parseFloat(ubicacion.longitud).toFixed(6)}°
                `);
            this.markers.push(marker);
        });

        // Ajustar la vista para mostrar todos los marcadores
        if (this.markers.length > 0) {
            const group = new L.featureGroup(this.markers);
            this.map.fitBounds(group.getBounds().pad(0.1));
        }
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

            if (field === 'latitud' || field === 'longitud') {
                aVal = parseFloat(aVal);
                bVal = parseFloat(bVal);
            }

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
    if (select && window.ubicacionManager) {
        window.ubicacionManager.recordsPerPage = parseInt(select.value);
        window.ubicacionManager.currentPage = 1;
        window.ubicacionManager.updateTable();
        window.ubicacionManager.updatePagination();
    }
};

// Función global para ordenamiento
window.sortTable = function(field) {
    if (window.ubicacionManager) {
        window.ubicacionManager.sortTable(field);
    }
};

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    window.ubicacionManager = new UbicacionManager();
});

// También exportar para uso como módulo
export default UbicacionManager;
