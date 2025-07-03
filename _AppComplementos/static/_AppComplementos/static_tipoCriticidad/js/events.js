// events.js - Eventos específicos de tipo criticidad
import { TipoCriticidadService, CriticidadService } from '../../../../static/js/global/api/index.js';
import { UI } from '../../../../static/js/global/utils/ui.js';

let currentPage = 1;
const DEFAULT_PER_PAGE = 10;

// Función para actualizar la tabla de tipos de criticidad
function actualizarTablaTipoCriticidades(data) {
    const tbody = document.getElementById('tipcritTableBody');
    if (!tbody) return;

    tbody.innerHTML = '';
    
    if (!data || data.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="4" class="text-center">No hay tipos de criticidad registrados</td>
            </tr>`;
        return;
    }

    data.forEach(item => {
        const row = document.createElement('tr');
        // Mantener los IDs como strings (UUIDs)
        const criticidadId = String(item.criticidad_id || item.criticidad);
        
        row.innerHTML = `
            <td>${UI.utils.escapeHtml(item.tipo_criticidad_name)}</td>
            <td>${UI.utils.escapeHtml(item.criticidad_name)}</td>
            <td>${UI.utils.formatDate(item.created_at)}</td>
            <td class="text-center">
                <button class="btn btn-primary btn-sm d-inline-block" 
                    data-id="${item.id}"
                    data-tipo-name="${UI.utils.escapeHtml(item.tipo_criticidad_name)}"
                    data-criticidad-id="${criticidadId}"
                    onclick="window.openEditModal(this.dataset.id, this.dataset.tipoName, this.dataset.criticidadId)"
                    style="white-space: nowrap;">
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
                loadTipoCriticidades(newPage);
            }
        });
    });
}

async function loadTipoCriticidades(page = currentPage) {
    try {
        UI.loading.show('tipcritTableBody');
        
        const perPage = parseInt(document.getElementById('recordsPerPage')?.value) || DEFAULT_PER_PAGE;
        const response = await TipoCriticidadService.listarTodo(page, perPage);
        
        if (response && response.results) {
            actualizarTablaTipoCriticidades(response.results);
            actualizarPaginacion(response, page, perPage);
            currentPage = page;
        } else {
            UI.toast.error("Error al cargar los tipos de criticidad");
        }
    } catch (error) {
        console.error("Error:", error);
        UI.toast.error("Error al cargar los datos");
    } finally {
        UI.loading.hide('tipcritTableBody');
    }
}

// Función global para abrir el modal de edición
window.openEditModal = async function(id, name, criticidadId) {
    try {
        console.log('Valores recibidos en openEditModal:', {
            id: id,
            name: name,
            criticidadId: criticidadId,
            criticidadIdType: typeof criticidadId
        });

        const modalElement = document.getElementById('editModal');
        const dropdown = document.getElementById('editCriticidad');
        
        // Configurar valores del formulario
        UI.form.setValue('edittipCritId', id);
        UI.form.setValue('editName', name);
        
        // Mantener criticidadId como string (UUID)
        const cleanCriticidadId = String(criticidadId).trim();
        
        if (!cleanCriticidadId || cleanCriticidadId === 'undefined' || cleanCriticidadId === 'null') {
            console.error('ID de criticidad inválido:', { original: criticidadId, converted: cleanCriticidadId });
            UI.toast.error('Error al cargar los datos de criticidad');
            return;
        }
        
        console.log('ID de criticidad como string:', cleanCriticidadId);
        
        // Deshabilitar el dropdown mientras se cargan los datos
        if (dropdown) {
            dropdown.disabled = true;
        }
        
        // Cargar las criticidades antes de mostrar el modal
        await cargarCriticidades('editCriticidad', cleanCriticidadId);
        
        // Habilitar el dropdown y mostrar el modal
        if (dropdown) {
            dropdown.disabled = false;
        }
        
        const modal = new bootstrap.Modal(modalElement);
        modal.show();
    } catch (error) {
        console.error('Error al abrir el modal:', error);
        UI.toast.error('Error al cargar los datos para edición');
    }
};

// Función para cargar las criticidades en el dropdown
async function cargarCriticidades(dropdownId = 'criticidadDropdown', selectedValue = null) {
    try {
        console.log('Cargando criticidades con ID seleccionado:', selectedValue);
        const response = await CriticidadService.listarTodosSinPaginacion();
        const dropdown = document.getElementById(dropdownId);
        
        if (!dropdown || !response?.results) {
            console.error(!dropdown ? 'Dropdown no encontrado:' : 'Respuesta inválida:', !dropdown ? dropdownId : response);
            return [];
        }

        // Limpiar el dropdown
        dropdown.innerHTML = '';
        
        // Manejar el valor seleccionado como string (UUID)
        const selVal = selectedValue ? String(selectedValue).trim() : '';
        console.log('Valor seleccionado (como string):', selVal);
        
        // Ordenar las criticidades por nombre
        const sortedCriticidades = response.results.sort((a, b) => a.name.localeCompare(b.name));
        
        // Agregar opción por defecto solo si no hay valor seleccionado válido
        if (!selVal) {
            const defaultOption = document.createElement('option');
            defaultOption.value = '';
            defaultOption.textContent = 'Seleccione una criticidad';
            dropdown.appendChild(defaultOption);
        }
        
        // Agregar todas las opciones
        sortedCriticidades.forEach(criticidad => {
            const option = document.createElement('option');
            const critId = String(criticidad.id); // Mantener como string UUID
            option.value = critId;
            option.textContent = criticidad.name;
            
            // Marcar como seleccionado si coincide el ID
            if (selVal && critId === selVal) {
                console.log('Coincidencia encontrada:', {
                    id: critId,
                    name: criticidad.name,
                    selectedValue: selVal
                });
                option.selected = true;
            }
            dropdown.appendChild(option);
        });
        
        // Verificar la selección final
        const selectedOption = dropdown.options[dropdown.selectedIndex];
        console.log('Estado final del dropdown:', {
            selectedValue: dropdown.value,
            selectedText: selectedOption ? selectedOption.textContent : null,
            expectedValue: selVal
        });
        
        return response.results;
    } catch (error) {
        console.error('Error al cargar criticidades:', error);
        UI.toast.error('Error al cargar las criticidades');
        return [];
    }
}

document.addEventListener("DOMContentLoaded", async function () {
    console.log("🟢 Página de tipos de criticidad cargada - Inicializando...");
    await loadTipoCriticidades();
    await cargarCriticidades();

    // Event Listeners
    document.getElementById('recordsPerPage')?.addEventListener('change', () => {
        currentPage = 1;
        loadTipoCriticidades();
    });

    document.getElementById('tipcritForm')?.addEventListener('submit', async function(event) {
        event.preventDefault();
        
        const name = UI.form.getValue('name');
        const criticidadId = UI.form.getValue('criticidadDropdown');
    
        if (!criticidadId) {
            UI.toast.warning("Debes seleccionar una criticidad");
            return;
        }
    
        const response = await TipoCriticidadService.crear(name, criticidadId);
        
        if (response.success) {
            UI.toast.success(response.message || "Tipo de criticidad creado exitosamente");
            loadTipoCriticidades();
            UI.form.reset('tipcritForm');
        } else {
            UI.toast.error(response.error || "Error al crear el tipo de criticidad");
        }
    });

    // Manejador del formulario de edición
    document.getElementById("edittipCritForm")?.addEventListener("submit", async function(event) {
        event.preventDefault();
    
        const id = UI.form.getValue("edittipCritId");
        const name = UI.form.getValue("editName");
        const criticidadId = UI.form.getValue("editCriticidad");

        if (!name || !criticidadId) {
            UI.toast.warning("Todos los campos son obligatorios");
            return;
        }

        const response = await TipoCriticidadService.actualizar(id, {
            name,
            criticidad_id: criticidadId
        });
        
        if (response.success) {
            UI.toast.success(response.message || "Tipo de criticidad actualizado exitosamente");
            bootstrap.Modal.getInstance(document.getElementById('editModal')).hide();
            loadTipoCriticidades(currentPage);
        } else {
            UI.toast.error(response.error || "Error al actualizar el tipo de criticidad");
        }
    });

    // Función global para actualizar paginación cuando cambia el selector
    window.updatePagination = function() {
        loadTipoCriticidades(1); // Ir a la primera página cuando cambia la cantidad de registros
    };
});
