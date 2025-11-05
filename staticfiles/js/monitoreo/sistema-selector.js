// sistema-selector.js - Selector de sistemas para monitoreo
import { SistemaAPI } from '../../../static/js/global/api/services/sistemas.js';

class SistemaSelectorManager {
    constructor() {
        this.apiService = SistemaAPI;
        this.sistemas = [];
        this.currentPage = 1;
        this.recordsPerPage = 10;
        this.filteredData = [];
        this.sortField = null;
        this.sortDirection = 'asc';
        
        this.initEventListeners();
        this.loadSistemas();
    }

    initEventListeners() {
        // Búsqueda
        const searchInput = document.getElementById('searchInput');
        const clearSearch = document.getElementById('clearSearch');

        if (searchInput) {
            searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.performSearch();
                }
            });
            
            // Búsqueda en tiempo real
            searchInput.addEventListener('input', () => {
                this.performSearch();
            });
        }

        if (clearSearch) {
            clearSearch.addEventListener('click', () => this.clearSearch());
        }
    }

    async loadSistemas() {
        try {
            console.log('🔄 Cargando sistemas para selección...');
            const response = await this.apiService.list({ page_size: 100 });
            
            if (response && (response.results || response.data?.results)) {
                this.sistemas = response.results || response.data.results;
                this.filteredData = [...this.sistemas];
                this.updateTable();
                this.updatePagination();
                console.log('✅ Sistemas cargados exitosamente:', this.sistemas.length);
            } else if (response.success && response.data) {
                this.sistemas = response.data.results || response.data;
                this.filteredData = [...this.sistemas];
                this.updateTable();
                this.updatePagination();
                console.log('✅ Sistemas cargados exitosamente:', this.sistemas.length);
            } else {
                console.error('❌ Estructura de respuesta inesperada:', response);
                this.showNoData();
            }
        } catch (error) {
            console.error('❌ Error al cargar sistemas:', error);
            this.showError('Error al cargar sistemas');
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
            this.showNoData();
            return;
        }

        pageData.forEach(sistema => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><strong>${sistema.tag}</strong></td>
                <td>${sistema.sistema_id}</td>
                <td>${sistema.ubicacion_nombre}</td>
                <td><small class="text-muted">${sistema.ubicacion_coordenadas}</small></td>
                <td>
                    <button class="btn btn-primary btn-sm" onclick="sistemaSelector.selectSistema('${sistema.id}', '${sistema.tag}', '${sistema.sistema_id}')">
                        <i class="bi bi-play-circle"></i> Monitorear
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    showNoData() {
        const tbody = document.getElementById('sistemasTableBody');
        if (!tbody) return;
        
        tbody.innerHTML = `
            <tr>
                <td colspan="5" class="text-center py-4">
                    <div class="text-muted">
                        <i class="bi bi-inbox" style="font-size: 2rem;"></i>
                        <p class="mt-2 mb-0">No se encontraron sistemas</p>
                        <small>Intenta con otros términos de búsqueda</small>
                    </div>
                </td>
            </tr>
        `;
    }

    showError(message) {
        const tbody = document.getElementById('sistemasTableBody');
        if (!tbody) return;
        
        tbody.innerHTML = `
            <tr>
                <td colspan="5" class="text-center py-4">
                    <div class="text-danger">
                        <i class="bi bi-exclamation-triangle" style="font-size: 2rem;"></i>
                        <p class="mt-2 mb-0">${message}</p>
                        <button class="btn btn-outline-primary btn-sm mt-2" onclick="sistemaSelector.loadSistemas()">
                            <i class="bi bi-arrow-clockwise"></i> Reintentar
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }

    selectSistema(sistemaId, tag, sistemaIdText) {
        console.log(`🎯 Sistema seleccionado: ${tag} ${sistemaIdText} (ID: ${sistemaId})`);
        
        // Mostrar confirmación
        Swal.fire({
            title: 'Iniciar Monitoreo',
            text: `¿Desea iniciar el monitoreo del sistema "${tag} ${sistemaIdText}"?`,
            icon: 'question',
            showCancelButton: true,
            confirmButtonColor: '#0d6efd',
            cancelButtonColor: '#6c757d',
            confirmButtonText: '<i class="bi bi-play-circle"></i> Iniciar Monitoreo',
            cancelButtonText: 'Cancelar'
        }).then((result) => {
            if (result.isConfirmed) {
                // Redirigir a la página de monitoreo con el sistema seleccionado
                window.location.href = `/monitoreo/${sistemaId}/`;
            }
        });
    }

    updatePagination() {
        const totalPages = Math.ceil(this.filteredData.length / this.recordsPerPage);
        const paginationContainer = document.getElementById('pagination');
        
        if (!paginationContainer) return;

        if (totalPages <= 1) {
            paginationContainer.innerHTML = '';
            return;
        }

        let paginationHTML = '<nav><ul class="pagination justify-content-center">';

        // Botón anterior
        paginationHTML += `
            <li class="page-item ${this.currentPage === 1 ? 'disabled' : ''}">
                <a class="page-link" href="#" onclick="sistemaSelector.goToPage(${this.currentPage - 1})">Anterior</a>
            </li>
        `;

        // Números de página
        const startPage = Math.max(1, this.currentPage - 2);
        const endPage = Math.min(totalPages, this.currentPage + 2);

        if (startPage > 1) {
            paginationHTML += `<li class="page-item"><a class="page-link" href="#" onclick="sistemaSelector.goToPage(1)">1</a></li>`;
            if (startPage > 2) {
                paginationHTML += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
            }
        }

        for (let i = startPage; i <= endPage; i++) {
            if (i === this.currentPage) {
                paginationHTML += `<li class="page-item active"><span class="page-link">${i}</span></li>`;
            } else {
                paginationHTML += `<li class="page-item"><a class="page-link" href="#" onclick="sistemaSelector.goToPage(${i})">${i}</a></li>`;
            }
        }

        if (endPage < totalPages) {
            if (endPage < totalPages - 1) {
                paginationHTML += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
            }
            paginationHTML += `<li class="page-item"><a class="page-link" href="#" onclick="sistemaSelector.goToPage(${totalPages})">${totalPages}</a></li>`;
        }

        // Botón siguiente
        paginationHTML += `
            <li class="page-item ${this.currentPage === totalPages ? 'disabled' : ''}">
                <a class="page-link" href="#" onclick="sistemaSelector.goToPage(${this.currentPage + 1})">Siguiente</a>
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
}

// Función global para ordenamiento
window.sortTable = function(field) {
    if (window.sistemaSelector) {
        window.sistemaSelector.sortTable(field);
    }
};

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    window.sistemaSelector = new SistemaSelectorManager();
});

// También exportar para uso como módulo
export default SistemaSelectorManager;
