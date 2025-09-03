// events.js - Eventos específicos de criticidad
import { CriticidadService } from '../../../../static/js/global/api/index.js';
import { UI } from '../../../../static/js/global/utils/ui.js';

let currentPage = 1;
const DEFAULT_PER_PAGE = 10;

// Exponer la función deleteCriticidad al ámbito global primero
window.deleteCriticidad = async function(id, name) {
    try {
        // Primero, mostrar el diálogo de confirmación con advertencia
        const result = await Swal.fire({
            title: '¿Está seguro?',
            html: `<div class="text-start">
                <p>Va a eliminar la criticidad <strong>"${name}"</strong>.</p>
                <p class="text-danger"><i class="bi bi-exclamation-triangle-fill"></i> ADVERTENCIA:</p>
                <p>Esta acción también eliminará:</p>
                <ul>
                    <li>Todas las relaciones con tipos de criticidad</li>
                    <li>Todas las asignaciones en productos que usen esta criticidad</li>
                    <li>Todas las relaciones con tipos de equipo que dependan de esta criticidad</li>
                    <li>Todas las tecnologías que dependan de esta criticidad</li>
                </ul>
                <p class="text-warning"><i class="bi bi-info-circle-fill"></i> ADEMÁS:</p>
                <p>Si algún elemento queda sin relaciones después de esta eliminación, también será eliminado automáticamente:</p>
                <ul>
                    <li>Tipos de criticidad que solo tenían esta criticidad</li>
                    <li>Productos que solo usaban esta criticidad</li>
                    <li>Tipos de equipo que solo tenían productos con esta criticidad</li>
                    <li>Tecnologías que solo tenían tipos de equipo con esta criticidad</li>
                </ul>
                <p>Esta acción no se puede deshacer.</p>
            </div>`,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '#3085d6',
            confirmButtonText: 'Sí, eliminar todo',
            cancelButtonText: 'Cancelar',
            width: '42em'
        });

        if (result.isConfirmed) {
            const response = await CriticidadService.eliminar(id);
            
            if (response.success) {
                // Mostrar resumen de lo que se eliminó
                await Swal.fire({
                    title: '¡Eliminación Completada!',
                    html: `<div class="text-start">${response.message.replace(/\n/g, '<br>')}</div>`,
                    icon: 'success',
                    width: '42em'
                });
                await loadCriticidades(currentPage);
            } else {
                throw new Error(response.message || 'Error al eliminar');
            }
        }
    } catch (error) {
        if (error.response?.status === 400) {
            await Swal.fire({
                title: 'No se puede eliminar',
                html: error.response.data.message,
                icon: 'error',
                confirmButtonColor: '#3085d6'
            });
        } else {
            await Swal.fire({
                title: 'Error',
                text: error.message || 'Error al eliminar la criticidad',
                icon: 'error',
                confirmButtonColor: '#3085d6'
            });
        }
        console.error('Error:', error);
    }
}

// Función para actualizar la tabla de criticidades
function actualizarTablaCriticidades(data) {
    const tbody = document.getElementById('critTableBody');
    if (!tbody) return;

    tbody.innerHTML = '';
    
    if (data.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="2">No hay criticidades registradas</td>
            </tr>`;
        return;
    }

    data.forEach(criticidad => {
        const row = document.createElement('tr');
        // Escapar el nombre para usar en atributos HTML
        const nombreEscapado = criticidad.name.replace(/'/g, '&#39;');
        row.innerHTML = `
            <td>${UI.utils.escapeHtml(criticidad.name)}</td>
            <td>
                <div class="btn-group" role="group">
                    <button class="btn btn-primary btn-sm me-1" 
                        onclick="openEditModal('${criticidad.id}', '${nombreEscapado}')">
                        <i class="bi bi-pencil-square"></i>
                    </button>
                    <button class="btn btn-danger btn-sm" 
                        onclick="deleteCriticidad('${criticidad.id}', '${nombreEscapado}')">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function actualizarPaginacion(response, currentPage, perPage) {
    const paginationEl = document.querySelector('.pagination');
    if (!paginationEl) return;

    paginationEl.innerHTML = '';

    // Botón Previous
    const prevLi = document.createElement('li');
    prevLi.className = `page-item ${!response.has_previous ? 'disabled' : ''}`;
    if (response.has_previous) {
        prevLi.innerHTML = `<a class="page-link" href="#" data-page="${response.previous_page_number}">Anterior</a>`;
    } else {
        prevLi.innerHTML = `<span class="page-link">Anterior</span>`;
    }
    paginationEl.appendChild(prevLi);

    // Páginas numeradas
    for (let i = 1; i <= response.total_pages; i++) {
        const li = document.createElement('li');
        li.className = `page-item ${i === currentPage ? 'active' : ''}`;
        li.innerHTML = `<a class="page-link" href="#" data-page="${i}">${i}</a>`;
        paginationEl.appendChild(li);
    }

    // Botón Next
    const nextLi = document.createElement('li');
    nextLi.className = `page-item ${!response.has_next ? 'disabled' : ''}`;
    if (response.has_next) {
        nextLi.innerHTML = `<a class="page-link" href="#" data-page="${response.next_page_number}">Siguiente</a>`;
    } else {
        nextLi.innerHTML = `<span class="page-link">Siguiente</span>`;
    }
    paginationEl.appendChild(nextLi);

    // Event listeners para la paginación
    paginationEl.querySelectorAll('.page-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const newPage = parseInt(e.target.dataset.page);
            if (newPage && newPage !== currentPage && newPage > 0 && newPage <= response.total_pages) {
                loadCriticidades(newPage);
            }
        });
    });
}

// Función para cargar las criticidades
async function loadCriticidades(page = currentPage, search = '') {
    try {
        UI.loading.show('critTableBody');
        
        const perPage = parseInt(document.getElementById('recordsPerPage')?.value) || DEFAULT_PER_PAGE;
        const searchQuery = search || document.getElementById('searchInput')?.value || '';
        
        const response = await CriticidadService.listarTodo(page, perPage, 'name', searchQuery);
        
        if (response && response.results) {
            actualizarTablaCriticidades(response.results);
            actualizarPaginacion(response, page, perPage);
            currentPage = page;
            
            // Mostrar mensaje si no hay resultados en la búsqueda
            if (response.results.length === 0 && searchQuery) {
                const tbody = document.getElementById('critTableBody');
                if (tbody) {
                    tbody.innerHTML = `
                        <tr>
                            <td colspan="2" class="text-center">
                                <i class="bi bi-search"></i>
                                No se encontraron criticidades que coincidan con "${searchQuery}"
                            </td>
                        </tr>`;
                }
            }
        } else {
            UI.showAlert("Error al cargar las criticidades", 'error');
        }
    } catch (error) {
        console.error("Error:", error);
        UI.showAlert("Error al cargar los datos", 'error');
    } finally {
        UI.loading.hide('critTableBody');
    }
}

// Función para abrir el modal de edición (la hacemos global)
window.openEditModal = function(id, name) {
    console.log('Abriendo modal de edición:', { id, name });
    UI.form.setValue('editCritId', id);
    UI.form.setValue('editName', name);
    const editModal = new bootstrap.Modal(document.getElementById('editModal'));
    editModal.show();
};

// Función global para actualizar paginación cuando cambia el selector
window.updatePagination = function() {
    loadCriticidades(1); // Ir a la primera página cuando cambia la cantidad de registros
};

// Funciones para la búsqueda
let searchTimeout;

function setupSearchFunctionality() {
    const searchInput = document.getElementById('searchInput');
    const clearSearchBtn = document.getElementById('clearSearch');
    
    if (searchInput) {
        // Búsqueda en tiempo real con debounce
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                currentPage = 1; // Resetear a la primera página al buscar
                loadCriticidades(1, this.value);
            }, 300); // Esperar 300ms después de que el usuario deje de escribir
        });
        
        // Limpiar búsqueda al presionar Enter
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                clearTimeout(searchTimeout);
                currentPage = 1;
                loadCriticidades(1, this.value);
            }
        });
    }
    
    if (clearSearchBtn) {
        // Botón para limpiar búsqueda
        clearSearchBtn.addEventListener('click', function() {
            if (searchInput) {
                searchInput.value = '';
                currentPage = 1;
                loadCriticidades(1, '');
            }
        });
    }
}

document.addEventListener("DOMContentLoaded", function () {
    console.log("🟢 Página de criticidades cargada - Inicializando...");
    loadCriticidades();
    setupSearchFunctionality(); // Inicializar funcionalidad de búsqueda

    // Event Listeners
    document.getElementById('recordsPerPage')?.addEventListener('change', () => {
        currentPage = 1;
        loadCriticidades();
    });

    document.getElementById('critForm')?.addEventListener('submit', async function(event) {
        event.preventDefault();
        const name = UI.form.getValue('name');

        const response = await CriticidadService.crear(name);
        if (response.success) {
            UI.showAlert(response.message || "Criticidad creada exitosamente", 'success');
            loadCriticidades();
            UI.form.reset('critForm');
        } else {
            UI.showAlert(response.error || "Error al registrar criticidad", 'error');
        }
    });

    document.getElementById("editCritForm")?.addEventListener("submit", async function(event) {
        event.preventDefault();
        const id = UI.form.getValue("editCritId");
        const name = UI.form.getValue("editName");

        const response = await CriticidadService.actualizar(id, name);
        if (response.success) {
            UI.showAlert("Criticidad actualizada correctamente", 'success');
            loadCriticidades();
            bootstrap.Modal.getInstance(document.getElementById('editModal')).hide();
        } else {
            UI.showAlert(response.error || "Error al actualizar la criticidad", 'error');
        }
    });

});
