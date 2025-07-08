// events.js - Eventos específicos de tipo criticidad
import { TipoCriticidadService, CriticidadService } from '../../../../static/js/global/api/index.js';
import { UI } from '../../../../static/js/global/utils/ui.js';

let currentPage = 1;
const DEFAULT_PER_PAGE = 10;

// Función para actualizar la tabla de tipos de criticidad con agrupación
function actualizarTablaTipoCriticidades(data) {
    const tbody = document.getElementById('tipcritTableBody');
    if (!tbody) return;

    tbody.innerHTML = '';
    
    if (!data || data.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="3" class="text-center">No hay tipos de criticidad registrados</td>
            </tr>`;
        return;
    }

    // Agrupar datos por tipo_criticidad_id
    const groupedData = {};
    data.forEach(item => {
        if (!groupedData[item.tipo_criticidad_id]) {
            groupedData[item.tipo_criticidad_id] = {
                tipo_criticidad_name: item.tipo_criticidad_name,
                total_relations: item.total_relations,
                relations: []
            };
        }
        groupedData[item.tipo_criticidad_id].relations.push(item);
    });

    // Renderizar filas agrupadas
    Object.values(groupedData).forEach((tipoGroup, groupIndex) => {
        const firstRelation = tipoGroup.relations[0];
        const hasMultipleRelations = tipoGroup.total_relations > 1;
        const groupClass = groupIndex % 2 === 0 ? 'group-odd' : 'group-even';
        
        // Crear la primera fila con el nombre del tipo
        const firstRow = document.createElement('tr');
        firstRow.className = `${groupClass} ${hasMultipleRelations ? 'group-start' : ''}`;
        firstRow.innerHTML = `
            <td class="align-middle type-name-cell" ${hasMultipleRelations ? `rowspan="${tipoGroup.relations.length}"` : ''}>
                <div class="type-name-container">
                    <span class="type-name">${UI.utils.escapeHtml(tipoGroup.tipo_criticidad_name)}</span>
                    <br><span class="badge bg-info mt-1" title="Este tipo tiene ${tipoGroup.total_relations} ${tipoGroup.total_relations === 1 ? 'relación' : 'relaciones'}">${tipoGroup.total_relations} ${tipoGroup.total_relations === 1 ? 'relación' : 'relaciones'}</span>
                </div>
            </td>
            <td class="relation-cell">${UI.utils.escapeHtml(firstRelation.criticidad_name)}</td>
            <td class="text-center action-cell">
                <div class="btn-group" role="group">
                    <button class="btn btn-primary btn-sm me-1" 
                        data-id="${firstRelation.id}"
                        data-tipo-name="${UI.utils.escapeHtml(tipoGroup.tipo_criticidad_name)}"
                        data-criticidad-id="${String(firstRelation.criticidad_id || firstRelation.criticidad)}"
                        onclick="openEditModal(this.dataset.id, this.dataset.tipoName, this.dataset.criticidadId)"
                        title="Editar esta relación">
                        <i class="bi bi-pencil-square"></i>
                    </button>
                    <button class="btn btn-danger btn-sm" 
                        onclick="deleteTipoCriticidad('${firstRelation.tipo_criticidad_id}', '${UI.utils.escapeHtml(tipoGroup.tipo_criticidad_name)}', '${firstRelation.id}')"
                        title="${hasMultipleRelations ? 'Eliminar esta relación' : 'Eliminar tipo de criticidad'}">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(firstRow);

        // Crear filas adicionales para las demás relaciones
        for (let i = 1; i < tipoGroup.relations.length; i++) {
            const relation = tipoGroup.relations[i];
            const additionalRow = document.createElement('tr');
            additionalRow.className = `${groupClass} group-continuation`;
            additionalRow.innerHTML = `
                <td class="relation-cell">${UI.utils.escapeHtml(relation.criticidad_name)}</td>
                <td class="text-center action-cell">
                    <div class="btn-group" role="group">
                        <button class="btn btn-primary btn-sm me-1" 
                            data-id="${relation.id}"
                            data-tipo-name="${UI.utils.escapeHtml(tipoGroup.tipo_criticidad_name)}"
                            data-criticidad-id="${String(relation.criticidad_id || relation.criticidad)}"
                            onclick="openEditModal(this.dataset.id, this.dataset.tipoName, this.dataset.criticidadId)"
                            title="Editar esta relación">
                            <i class="bi bi-pencil-square"></i>
                        </button>
                        <button class="btn btn-danger btn-sm" 
                            onclick="deleteTipoCriticidad('${relation.tipo_criticidad_id}', '${UI.utils.escapeHtml(tipoGroup.tipo_criticidad_name)}', '${relation.id}')"
                            title="Eliminar esta relación">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </td>
            `;
            tbody.appendChild(additionalRow);
        }
    });
    
    // Agregar efecto hover para grupos completos
    aplicarEfectosHover();
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

async function loadTipoCriticidades(page = currentPage, search = '') {
    try {
        UI.loading.show('tipcritTableBody');
        
        const perPage = parseInt(document.getElementById('recordsPerPage')?.value) || DEFAULT_PER_PAGE;
        const searchQuery = search || document.getElementById('searchInput')?.value || '';
        
        const response = await TipoCriticidadService.listarTodo(page, perPage, 'tipo_criticidad__name', searchQuery);
        
        if (response && response.results) {
            actualizarTablaTipoCriticidades(response.results);
            actualizarPaginacion(response, page, perPage);
            currentPage = page;
            
            // Mostrar mensaje si no hay resultados en la búsqueda
            if (response.results.length === 0 && searchQuery) {
                const tbody = document.getElementById('tipcritTableBody');
                if (tbody) {
                    tbody.innerHTML = `
                        <tr>
                            <td colspan="3" class="text-center">
                                <i class="bi bi-search"></i>
                                No se encontraron tipos de criticidad que coincidan con "${searchQuery}"
                            </td>
                        </tr>`;
                }
            }
        } else {
            UI.showAlert("Error al cargar los tipos de criticidad", 'error');
        }
    } catch (error) {
        console.error("Error:", error);
        UI.showAlert("Error al cargar los datos", 'error');
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
            criticidadId: typeof criticidadId
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
            UI.showAlert('Error al cargar los datos de criticidad', 'error');
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
        UI.showAlert('Error al cargar los datos para edición', 'error');
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
        UI.showAlert('Error al cargar las criticidades');
        return [];
    }
}

document.addEventListener("DOMContentLoaded", async function () {
    console.log("🟢 Página de tipos de criticidad cargada - Inicializando...");
    await loadTipoCriticidades();
    await cargarCriticidades();
    setupSearchFunctionality(); // Inicializar funcionalidad de búsqueda

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
            UI.showAlert("Debes seleccionar una criticidad");
            return;
        }
    
        const response = await TipoCriticidadService.crear(name, criticidadId);
        
        if (response.success) {
            UI.showAlert(response.message || "Tipo de criticidad creado exitosamente");
            loadTipoCriticidades();
            UI.form.reset('tipcritForm');
        } else {
            UI.showAlert(response.error || "Error al crear el tipo de criticidad");
        }
    });

    // Manejador del formulario de edición
    document.getElementById("edittipCritForm")?.addEventListener("submit", async function(event) {
        event.preventDefault();
    
        const id = UI.form.getValue("edittipCritId");
        const name = UI.form.getValue("editName");
        const criticidadId = UI.form.getValue("editCriticidad");

        if (!name || !criticidadId) {
            UI.showAlert("Todos los campos son obligatorios");
            return;
        }

        const response = await TipoCriticidadService.actualizar(id, {
            name,
            criticidad_id: criticidadId
        });
        
        if (response.success) {
            UI.showAlert(response.message || "Tipo de criticidad actualizado exitosamente");
            bootstrap.Modal.getInstance(document.getElementById('editModal')).hide();
            loadTipoCriticidades(currentPage);
        } else {
            UI.showAlert(response.error || "Error al actualizar el tipo de criticidad");
        }
    });

    // Función global para actualizar paginación cuando cambia el selector
    window.updatePagination = function() {
        loadTipoCriticidades(1); // Ir a la primera página cuando cambia la cantidad de registros
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
                    loadTipoCriticidades(1, this.value);
                }, 300); // Esperar 300ms después de que el usuario deje de escribir
            });
            
            // Limpiar búsqueda al presionar Enter
            searchInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    clearTimeout(searchTimeout);
                    currentPage = 1;
                    loadTipoCriticidades(1, this.value);
                }
            });
        }
        
        if (clearSearchBtn) {
            // Botón para limpiar búsqueda
            clearSearchBtn.addEventListener('click', function() {
                if (searchInput) {
                    searchInput.value = '';
                    currentPage = 1;
                    loadTipoCriticidades(1, '');
                }
            });
        }
    }

    setupSearchFunctionality();
});

// Función para manejar la eliminación de tipos de criticidad
window.deleteTipoCriticidad = async function(tipoId, tipoName, relacionId) {
    try {
        let deleteType;

        // Obtener el total de relaciones del tipo
        const tipoDetails = await TipoCriticidadService.listarTodo(1, 1000);
        const tipoInfo = tipoDetails.results.find(t => String(t.tipo_criticidad_id) === String(tipoId));
        const hasMultipleRelations = tipoInfo?.total_relations > 1;

        if (hasMultipleRelations) {
            // Si tiene múltiples relaciones, mostrar diálogo con opciones
            const result = await Swal.fire({
                title: `¿Qué desea eliminar?`,
                html: `
                    <div class="text-start">
                        <p>El tipo de criticidad "${tipoName}" tiene ${tipoInfo.total_relations} relaciones.</p>
                        <p class="text-warning">
                            <i class="bi bi-exclamation-triangle"></i> 
                            Nota: Los productos que solo usen este tipo de criticidad serán eliminados automáticamente.
                        </p>
                        <div class="form-check">
                            <input class="form-check-input" type="radio" name="deleteType" id="deleteRelation" value="relation" checked>
                            <label class="form-check-label" for="deleteRelation">
                                Solo eliminar esta relación
                            </label>
                        </div>
                        <div class="form-check mt-2">
                            <input class="form-check-input" type="radio" name="deleteType" id="deleteTipo" value="tipo">
                            <label class="form-check-label" for="deleteTipo">
                                Eliminar el tipo y todas sus relaciones
                            </label>
                        </div>
                    </div>
                `,
                showCancelButton: true,
                confirmButtonText: 'Eliminar',
                cancelButtonText: 'Cancelar',
                preConfirm: () => {
                    return document.querySelector('input[name="deleteType"]:checked')?.value;
                }
            });

            if (result.isDismissed) return;
            deleteType = result.value;
        } else {
            // Si solo tiene una relación, confirmar la eliminación simple
            const result = await Swal.fire({
                title: '¿Está seguro?',
                html: `
                    <div class="text-start">
                        <p>Esta es la última relación del tipo "${tipoName}".</p>
                        <p>El tipo de criticidad será eliminado completamente.</p>
                        <p class="text-warning">
                            <i class="bi bi-exclamation-triangle"></i> 
                            Nota: Los productos que solo usen este tipo de criticidad serán eliminados automáticamente.
                        </p>
                    </div>
                `,
                icon: 'warning',
                showCancelButton: true,
                confirmButtonText: 'Sí, eliminar',
                cancelButtonText: 'Cancelar'
            });

            if (result.isDismissed) return;
            deleteType = 'relation'; // Para una sola relación, usamos DeleteRelacionCommand
        }

        UI.loading.show();

        let response;
        if (deleteType === 'tipo') {
            response = await TipoCriticidadService.eliminarTipo(tipoId);
        } else {
            response = await TipoCriticidadService.eliminarRelacion(relacionId);
        }

        if (response?.success) {
            UI.showAlert(response.message);
            
            // Si se eliminaron productos o es eliminación completa del tipo, actualizar tabla de productos
            if (deleteType === 'tipo' || response.detalles?.productos_eliminados?.length > 0) {
                const productosTabla = document.getElementById('prodTableBody');
                if (productosTabla) {
                    // Intentar recargar la tabla de productos si existe
                    try {
                        window.loadProductos?.();
                    } catch (error) {
                        console.log('La tabla de productos no está disponible en esta vista');
                    }
                }
                
                // Actualizar dropdowns de productos si existen
                const productosDropdowns = document.querySelectorAll('[id^=productoDropdown]');
                productosDropdowns.forEach(dropdown => {
                    try {
                        window.cargarProductos?.(dropdown.id);
                    } catch (error) {
                        console.log('Error al actualizar dropdown de productos:', error);
                    }
                });
            }
            
            // Si era la última relación o se eliminó el tipo completo, actualizar las listas
            if (response.was_last_relation || deleteType === 'tipo') {
                // Recargar los dropdowns de tipos si están presentes
                const dropdowns = document.querySelectorAll('[id^=tipocriticidadDropdown]');
                for (const dropdown of dropdowns) {
                    await cargarTiposCriticidad(dropdown.id);
                }
            }

            // Recargar la tabla de tipos de criticidad
            await loadTipoCriticidades(currentPage);
        } else {
            UI.showAlert(response?.message || 'Error al eliminar el tipo de criticidad');
        }
    } catch (error) {
        console.error('Error:', error);
        UI.showAlert('Error al procesar la solicitud');
    } finally {
        UI.loading.hide();
    }
};

// Función para aplicar efectos de hover por grupo
function aplicarEfectosHover() {
    const tbody = document.getElementById('tipoCriticidadTableBody');
    if (!tbody) return;

    const rows = tbody.querySelectorAll('tr[data-group-id]');
    
    rows.forEach(row => {
        const groupId = row.dataset.groupId;
        
        row.addEventListener('mouseenter', () => {
            // Resaltar todas las filas del mismo grupo
            const groupRows = tbody.querySelectorAll(`tr[data-group-id="${groupId}"]`);
            groupRows.forEach(groupRow => {
                groupRow.classList.add('group-hover');
            });
        });
        
        row.addEventListener('mouseleave', () => {
            // Quitar resaltado de todas las filas del mismo grupo
            const groupRows = tbody.querySelectorAll(`tr[data-group-id="${groupId}"]`);
            groupRows.forEach(groupRow => {
                groupRow.classList.remove('group-hover');
            });
        });
    });
}
