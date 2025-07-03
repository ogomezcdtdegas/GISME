// events.js - Eventos específicos de criticidad
import { CriticidadService } from '../../../../static/js/global/api/index.js';
import { UI } from '../../../../static/js/global/utils/ui.js';

let currentPage = 1;
const DEFAULT_PER_PAGE = 10;

// Función para actualizar la tabla de criticidades
function actualizarTablaCriticidades(data) {
    const tbody = document.getElementById('critTableBody');
    if (!tbody) return;

    tbody.innerHTML = '';
    
    if (data.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="3">No hay criticidades registradas</td>
            </tr>`;
        return;
    }

    data.forEach(criticidad => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${criticidad.name}</td>
            <td>${criticidad.created_at}</td>
            <td>
                <button class="btn btn-primary btn-sm" onclick="openEditModal('${criticidad.id}', '${criticidad.name}')">
                    <i class="bi bi-pencil-square"></i>
                </button>
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
async function loadCriticidades(page = currentPage) {
    try {
        UI.loading.show('critTableBody');
        
        const perPage = parseInt(document.getElementById('recordsPerPage')?.value) || DEFAULT_PER_PAGE;
        const response = await CriticidadService.listarTodo(page, perPage);
        
        if (response && response.results) {
            actualizarTablaCriticidades(response.results);
            actualizarPaginacion(response, page, perPage);
            currentPage = page;
        } else {
            UI.toast.error("Error al cargar las criticidades");
        }
    } catch (error) {
        console.error("Error:", error);
        UI.toast.error("Error al cargar los datos");
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

document.addEventListener("DOMContentLoaded", function () {
    console.log("🟢 Página de criticidades cargada - Inicializando...");
    loadCriticidades();

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
            UI.toast.success(response.message || "Criticidad creada exitosamente");
            loadCriticidades();
            UI.form.reset('critForm');
        } else {
            UI.toast.error(response.error || "Error al registrar criticidad");
        }
    });

    document.getElementById("editCritForm")?.addEventListener("submit", async function(event) {
        event.preventDefault();
        const id = UI.form.getValue("editCritId");
        const name = UI.form.getValue("editName");

        const response = await CriticidadService.actualizar(id, name);
        if (response.success) {
            UI.toast.success("Criticidad actualizada correctamente");
            loadCriticidades();
            bootstrap.Modal.getInstance(document.getElementById('editModal')).hide();
        } else {
            UI.toast.error(response.error || "Error al actualizar la criticidad");
        }
    });

});
