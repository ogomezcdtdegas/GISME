import { UI } from '/static/js/global/utils/ui.js';
import { TipoEquipoService } from '/static/js/global/api/services/tipoEquipo.js';
import { BaseAPI } from '/static/js/global/api/base.js';

// Variables globales para el manejo de paginación
let currentPage = 1;
let perPage = 10;

// Función para cargar todos los tipos de equipo
async function loadTiposEquipo(page = currentPage, search = '') {
    try {
        UI.loading.show('tipoEquipoTableBody');
        
        const response = await TipoEquipoService.listar(page, perPage, search);
        
        if (response.success !== false) {
            currentPage = page;
            actualizarTablaTiposEquipo(response);
            actualizarPaginacion(response, page, perPage);
        } else {
            UI.showAlert(response.error || "Error al cargar los tipos de equipo", 'error');
        }
    } catch (error) {
        console.error("Error:", error);
        UI.showAlert("Error al cargar los datos", 'error');
    } finally {
        UI.loading.hide('tipoEquipoTableBody');
    }
}

// Función para actualizar la tabla de tipos de equipo con agrupación visual
function actualizarTablaTiposEquipo(response) {
    const tbody = document.getElementById('tipoEquipoTableBody');
    
    if (!tbody) return;
    
    // Extraer datos de la respuesta (response puede ser la respuesta directa del API o data)
    const data = response.results || response;
    
    if (data && data.length > 0) {
        // Agrupar por tipo_equipo_id
        const grupos = {};
        data.forEach(item => {
            const grupoId = item.tipo_equipo_id || 'sin_grupo';
            if (!grupos[grupoId]) {
                grupos[grupoId] = {
                    nombre: item.tipo_equipo_name || '',
                    items: []
                };
            }
            grupos[grupoId].items.push(item);
        });

        let htmlContent = '';
        let isOddGroup = true;

        Object.keys(grupos).forEach(grupoId => {
            const grupo = grupos[grupoId];
            const groupClass = isOddGroup ? 'group-odd' : 'group-even';
            const cantidadItems = grupo.items.length;
            
            // Badge: mismo color que en productos (bg-info)
            const badgeText = cantidadItems === 1 ? '1 combinación' : `${cantidadItems} combinaciones`;
            
            grupo.items.forEach((item, index) => {
                if (index === 0) {
                    // Primera fila del grupo: mostrar nombre con rowspan y badge (igual que productos)
                    htmlContent += `
                        <tr class="${groupClass}" data-group-id="${grupoId}">
                            <td class="align-middle main-name-cell" rowspan="${cantidadItems}">
                                <div class="name-container">
                                    <span class="main-name">${UI.utils.escapeHtml(grupo.nombre)}</span>
                                    <br><span class="badge bg-info mt-1" title="Este tipo de equipo tiene ${cantidadItems} ${cantidadItems === 1 ? 'combinación' : 'combinaciones'}">${badgeText}</span>
                                </div>
                            </td>
                            <td>${UI.utils.escapeHtml(item.producto_name || '')}</td>
                            <td>${UI.utils.escapeHtml(item.tipo_criticidad_name || '')}</td>
                            <td>${UI.utils.escapeHtml(item.criticidad_name || '')}</td>
                            <td class="text-center">
                                <div class="btn-group" role="group">
                                    <button class="btn btn-primary btn-sm me-1" 
                                        data-id="${item.id || ''}"
                                        data-tipo-equipo-name="${UI.utils.escapeHtml(item.tipo_equipo_name || '')}"
                                        data-producto-id="${item.producto_id || ''}"
                                        data-tipo-criticidad-id="${item.tipo_criticidad_id || ''}"
                                        data-criticidad-id="${item.criticidad_id || ''}"
                                        onclick="window.openEditModal(this.dataset.id, this.dataset.tipoEquipoName, this.dataset.productoId, this.dataset.tipoCriticidadId, this.dataset.criticidadId)"
                                        style="white-space: nowrap;">
                                        <i class="bi bi-pencil-square"></i>
                                    </button>
                                    <button class="btn btn-danger btn-sm" 
                                        onclick="window.deleteTipoEquipo('${item.id || ''}', '${item.tipo_equipo_id || ''}', '${UI.utils.escapeHtml(item.tipo_equipo_name || '')}')"
                                        title="${cantidadItems > 1 ? 'Eliminar esta combinación' : 'Eliminar tipo de equipo'}"
                                        style="white-space: nowrap;">
                                        <i class="bi bi-trash"></i>
                                    </button>
                                </div>
                            </td>
                        </tr>
                    `;
                } else {
                    // Filas adicionales del grupo: solo combinaciones
                    htmlContent += `
                        <tr class="${groupClass}" data-group-id="${grupoId}">
                            <td>${UI.utils.escapeHtml(item.producto_name || '')}</td>
                            <td>${UI.utils.escapeHtml(item.tipo_criticidad_name || '')}</td>
                            <td>${UI.utils.escapeHtml(item.criticidad_name || '')}</td>
                            <td class="text-center">
                                <div class="btn-group" role="group">
                                    <button class="btn btn-primary btn-sm me-1" 
                                        data-id="${item.id || ''}"
                                        data-tipo-equipo-name="${UI.utils.escapeHtml(item.tipo_equipo_name || '')}"
                                        data-producto-id="${item.producto_id || ''}"
                                        data-tipo-criticidad-id="${item.tipo_criticidad_id || ''}"
                                        data-criticidad-id="${item.criticidad_id || ''}"
                                        onclick="window.openEditModal(this.dataset.id, this.dataset.tipoEquipoName, this.dataset.productoId, this.dataset.tipoCriticidadId, this.dataset.criticidadId)"
                                        style="white-space: nowrap;">
                                        <i class="bi bi-pencil-square"></i>
                                    </button>
                                    <button class="btn btn-danger btn-sm" 
                                        onclick="window.deleteTipoEquipo('${item.id || ''}', '${item.tipo_equipo_id || ''}', '${UI.utils.escapeHtml(item.tipo_equipo_name || '')}')"
                                        title="Eliminar esta combinación"
                                        style="white-space: nowrap;">
                                        <i class="bi bi-trash"></i>
                                    </button>
                                </div>
                            </td>
                        </tr>
                    `;
                }
            });
            
            isOddGroup = !isOddGroup; // Alternar para el próximo grupo
        });

        tbody.innerHTML = htmlContent;
        
        // Aplicar efectos de hover por grupo
        aplicarEfectosHover();
    } else {
        const searchQuery = document.getElementById('searchInput')?.value;
        if (searchQuery && searchQuery.trim() !== '') {
            tbody.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center">
                        <i class="bi bi-search"></i><br>
                        No se encontraron tipos de equipo que coincidan con "${searchQuery}"
                    </td>
                </tr>`;
        } else {
            tbody.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center">
                        <i class="bi bi-inbox"></i><br>
                        No hay tipos de equipo registrados
                    </td>
                </tr>`;
        }
    }
}

// Función para aplicar efectos de hover por grupo
function aplicarEfectosHover() {
    const tbody = document.getElementById('tipoEquipoTableBody');
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

// Función para actualizar la paginación
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
            if (newPage && newPage !== currentPage) {
                loadTiposEquipo(newPage, document.getElementById('searchInput')?.value || '');
            }
        });
    });
}

// Función para cargar productos en el dropdown
async function cargarProductos(dropdownId = 'productoDropdown', selectedValue = null) {
    try {
        // Usar BaseAPI para hacer la petición con headers correctos
        const data = await BaseAPI.get('/complementos/listar-todo-productos/');
        
        const dropdown = document.getElementById(dropdownId);
        
        if (!dropdown || !data?.results) {
            console.error('Error al cargar productos:', data);
            return;
        }

        dropdown.innerHTML = '<option value="">Seleccione un producto</option>';
        
        // Obtener productos únicos
        const productosUnicos = data.results.reduce((acc, curr) => {
            if (!acc.some(p => p.producto_id === curr.producto_id)) {
                acc.push(curr);
            }
            return acc;
        }, []);

        // Ordenar por nombre
        const sortedProductos = productosUnicos.sort((a, b) => 
            a.producto_name.localeCompare(b.producto_name));

        sortedProductos.forEach(producto => {
            const option = document.createElement('option');
            option.value = producto.producto_id;
            option.textContent = producto.producto_name;
            if (selectedValue && String(producto.producto_id) === String(selectedValue)) {
                option.selected = true;
            }
            dropdown.appendChild(option);
        });
    } catch (error) {
        console.error('Error al cargar productos:', error);
        UI.showAlert('Error al cargar los productos', 'error');
    }
}

// Función para cargar tipos de criticidad basados en el producto seleccionado
async function cargarTiposCriticidadPorProducto(productoId, dropdownId = 'tipoCriticidadDropdown', selectedValue = null) {
    try {
        const data = await BaseAPI.get('/complementos/listar-todo-productos/');
        
        const dropdown = document.getElementById(dropdownId);
        
        if (!dropdown || !data?.results) {
            console.error('Error al cargar tipos de criticidad');
            return;
        }

        dropdown.innerHTML = '<option value="">Seleccione un tipo</option>';
        
        // Filtrar tipos de criticidad para el producto seleccionado
        const tiposCriticidad = data.results
            .filter(item => String(item.producto_id) === String(productoId))
            .reduce((acc, curr) => {
                if (!acc.some(t => t.tipo_criticidad_id === curr.tipo_criticidad_id)) {
                    acc.push({
                        tipo_criticidad_id: curr.tipo_criticidad_id,
                        tipo_criticidad_name: curr.tipo_criticidad_name
                    });
                }
                return acc;
            }, []);

        // Ordenar por nombre
        const sortedTipos = tiposCriticidad.sort((a, b) => 
            a.tipo_criticidad_name.localeCompare(b.tipo_criticidad_name));

        sortedTipos.forEach(tipo => {
            const option = document.createElement('option');
            option.value = tipo.tipo_criticidad_id;
            option.textContent = tipo.tipo_criticidad_name;
            if (selectedValue && String(tipo.tipo_criticidad_id) === String(selectedValue)) {
                option.selected = true;
            }
            dropdown.appendChild(option);
        });
        
        // Habilitar el dropdown
        dropdown.disabled = false;
    } catch (error) {
        console.error('Error al cargar tipos de criticidad:', error);
        UI.showAlert('Error al cargar los tipos de criticidad', 'error');
    }
}

// Función para cargar criticidades basadas en el tipo de criticidad seleccionado
async function cargarCriticidadesPorTipo(tipoCriticidadId, dropdownId = 'criticidadDropdown', selectedValue = null) {
    try {
        const data = await BaseAPI.get('/complementos/listar-todo-productos/');
        
        const dropdown = document.getElementById(dropdownId);
        
        if (!dropdown || !data?.results) {
            console.error('Error al cargar criticidades');
            return;
        }

        dropdown.innerHTML = '<option value="">Seleccione una criticidad</option>';
        
        // Filtrar criticidades para el tipo de criticidad seleccionado
        const criticidades = data.results
            .filter(item => String(item.tipo_criticidad_id) === String(tipoCriticidadId))
            .reduce((acc, curr) => {
                if (!acc.some(c => c.criticidad_id === curr.criticidad_id)) {
                    acc.push({
                        criticidad_id: curr.criticidad_id,
                        criticidad_name: curr.criticidad_name
                    });
                }
                return acc;
            }, []);

        // Ordenar por nombre
        const sortedCriticidades = criticidades.sort((a, b) => 
            a.criticidad_name.localeCompare(b.criticidad_name));

        sortedCriticidades.forEach(criticidad => {
            const option = document.createElement('option');
            option.value = criticidad.criticidad_id;
            option.textContent = criticidad.criticidad_name;
            if (selectedValue && String(criticidad.criticidad_id) === String(selectedValue)) {
                option.selected = true;
            }
            dropdown.appendChild(option);
        });
        
        // Habilitar el dropdown
        dropdown.disabled = false;
    } catch (error) {
        console.error('Error al cargar criticidades:', error);
        UI.showAlert('Error al cargar las criticidades', 'error');
    }
}

// Función global para abrir el modal de edición
window.openEditModal = async function(id, name, productoId, tipoCriticidadId, criticidadId) {
    try {
        console.log('Abriendo modal con:', { id, name, productoId, tipoCriticidadId, criticidadId });
        
        const modalElement = document.getElementById('editModal');
        
        // Configurar valores básicos del formulario
        UI.form.setValue('editTipoEquipoId', id);
        UI.form.setValue('editName', name);
        
        // Cargar productos y seleccionar el correcto
        await cargarProductos('editProducto', productoId);
        
        // Cargar tipos de criticidad para el producto seleccionado
        if (productoId) {
            await cargarTiposCriticidadPorProducto(productoId, 'editTipoCriticidad', tipoCriticidadId);
        }
        
        // Cargar criticidades para el tipo seleccionado
        if (tipoCriticidadId) {
            await cargarCriticidadesPorTipo(tipoCriticidadId, 'editCriticidad', criticidadId);
        }
        
        const modal = new bootstrap.Modal(modalElement);
        modal.show();
    } catch (error) {
        console.error('Error al abrir el modal:', error);
        UI.showAlert('Error al cargar los datos para edición', 'error');
    }
};

// Función global para actualizar paginación cuando cambia el selector
window.updatePagination = function() {
    loadTiposEquipo(1); // Ir a la primera página cuando cambia la cantidad de registros
};

// Función para manejar la eliminación de tipos de equipo
window.deleteTipoEquipo = async function(relacionId, tipoEquipoId, tipoEquipoName) {
    try {
        let deleteType;

        // Obtener el total de relaciones del tipo de equipo
        const tipoEquipoDetails = await TipoEquipoService.listar(1, 1000); // Temporal: Get all to count relations
        const tipoEquipoInfo = tipoEquipoDetails.results?.find(t => String(t.tipo_equipo_id) === String(tipoEquipoId));
        const hasMultipleRelations = tipoEquipoInfo?.total_relations > 1;

        if (hasMultipleRelations) {
            // Si tiene múltiples relaciones, mostrar diálogo con opciones
            const result = await Swal.fire({
                title: `¿Qué desea eliminar?`,
                html: `
                    <div class="text-start">
                        <p>El tipo de equipo "${tipoEquipoName}" tiene ${tipoEquipoInfo.total_relations} relaciones.</p>
                        <p class="text-warning">
                            <i class="bi bi-exclamation-triangle"></i> 
                            Nota: Esta acción eliminará en cascada todas las tecnologías que dependan únicamente de este tipo de equipo.
                        </p>
                        <div class="form-check">
                            <input class="form-check-input" type="radio" name="deleteType" id="deleteRelation" value="relation" checked>
                            <label class="form-check-label" for="deleteRelation">
                                Solo eliminar esta relación
                            </label>
                        </div>
                        <div class="form-check mt-2">
                            <input class="form-check-input" type="radio" name="deleteType" id="deleteTipoEquipo" value="tipoEquipo">
                            <label class="form-check-label" for="deleteTipoEquipo">
                                Eliminar el tipo de equipo y todas sus relaciones
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
                        <p>Esta es la última relación del tipo de equipo "${tipoEquipoName}".</p>
                        <p>El tipo de equipo será eliminado completamente.</p>
                        <p class="text-warning">
                            <i class="bi bi-exclamation-triangle"></i> 
                            Nota: También se eliminarán en cascada todas las tecnologías que dependan únicamente de este tipo de equipo.
                        </p>
                    </div>
                `,
                icon: 'warning',
                showCancelButton: true,
                confirmButtonText: 'Sí, eliminar',
                cancelButtonText: 'Cancelar'
            });

            if (result.isDismissed) return;
            deleteType = 'relation'; // For single relation, we use DeleteRelacionCommand and let backend handle it
        }

        UI.loading.show();

        let response;
        if (deleteType === 'tipoEquipo') {
            response = await TipoEquipoService.eliminarTipoEquipo(tipoEquipoId);
        } else {
            response = await TipoEquipoService.eliminarRelacion(relacionId);
        }

        if (response?.success) {
            UI.showAlert(response.message, 'success');
            
            // Si era la última relación o se eliminó el tipo de equipo completo, actualizar las listas
            if (response.was_last_relation || deleteType === 'tipoEquipo') {
                // Recargar los dropdowns de tipos de equipo si están presentes
                const dropdowns = document.querySelectorAll('[id^=tipoEquipoDropdown]');
                for (const dropdown of dropdowns) {
                    await cargarTiposEquipo(dropdown.id);
                }
            }

            // Recargar la tabla de tipos de equipo
            await loadTiposEquipo(currentPage);
        } else {
            UI.showAlert(response?.message || 'Error al eliminar el tipo de equipo', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        UI.showAlert('Error al procesar la solicitud', 'error');
    } finally {
        UI.loading.hide();
    }
};

// Funciones para la búsqueda
let searchTimeout;

function setupSearchFunctionality() {
    const searchInput = document.getElementById('searchInput');
    const clearButton = document.getElementById('clearSearch');

    if (searchInput) {
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                currentPage = 1;
                loadTiposEquipo(1, this.value);
            }, 300); // Debounce de 300ms
        });
    }

    if (clearButton) {
        clearButton.addEventListener('click', function() {
            if (searchInput) {
                searchInput.value = '';
                currentPage = 1;
                loadTiposEquipo(1, '');
            }
        });
    }
}

// Inicialización cuando se carga la página
document.addEventListener("DOMContentLoaded", async function () {
    console.log("🟢 Página de tipos de equipo cargada - Inicializando...");
    await loadTiposEquipo();
    await cargarProductos();
    setupSearchFunctionality();

    // Event Listeners
    document.getElementById('recordsPerPage')?.addEventListener('change', function() {
        perPage = parseInt(this.value);
        currentPage = 1;
        loadTiposEquipo();
    });

    // Eventos para los dropdowns encadenados
    document.getElementById('productoDropdown')?.addEventListener('change', function() {
        const productoId = this.value;
        const tipoCriticidadDropdown = document.getElementById('tipoCriticidadDropdown');
        const criticidadDropdown = document.getElementById('criticidadDropdown');
        
        if (productoId) {
            cargarTiposCriticidadPorProducto(productoId);
        } else {
            // Limpiar y deshabilitar los dropdowns siguientes
            tipoCriticidadDropdown.innerHTML = '<option value="">Seleccione tipo</option>';
            tipoCriticidadDropdown.disabled = true;
            criticidadDropdown.innerHTML = '<option value="">Seleccione criticidad</option>';
            criticidadDropdown.disabled = true;
        }
    });

    document.getElementById('tipoCriticidadDropdown')?.addEventListener('change', function() {
        const tipoCriticidadId = this.value;
        const criticidadDropdown = document.getElementById('criticidadDropdown');
        
        if (tipoCriticidadId) {
            cargarCriticidadesPorTipo(tipoCriticidadId);
        } else {
            criticidadDropdown.innerHTML = '<option value="">Seleccione criticidad</option>';
            criticidadDropdown.disabled = true;
        }
    });

    // Evento para el formulario de registro
    document.getElementById('tipoEquipoForm')?.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const name = UI.form.getValue('name');
        const productoId = UI.form.getValue('productoDropdown');
        const tipoCriticidadId = UI.form.getValue('tipoCriticidadDropdown');
        const criticidadId = UI.form.getValue('criticidadDropdown');

        if (!name || !productoId || !tipoCriticidadId || !criticidadId) {
            UI.showAlert("Todos los campos son obligatorios", 'warning');
            return;
        }

        const response = await TipoEquipoService.crear({
            name,
            producto_id: productoId,
            tipo_criticidad_id: tipoCriticidadId,
            criticidad_id: criticidadId
        });
        
        if (response.success) {
            UI.showAlert(response.message || "Tipo de equipo registrado exitosamente", 'success');
            this.reset();
            
            // Resetear dropdowns
            document.getElementById('tipoCriticidadDropdown').disabled = true;
            document.getElementById('criticidadDropdown').disabled = true;
            
            loadTiposEquipo(currentPage);
        } else {
            UI.showAlert(response.error || "Error al registrar el tipo de equipo", 'error');
        }
    });

    // Evento para el formulario de edición
    document.getElementById('editTipoEquipoForm')?.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const id = UI.form.getValue('editTipoEquipoId');
        const name = UI.form.getValue('editName');
        const productoId = UI.form.getValue('editProducto');
        const tipoCriticidadId = UI.form.getValue('editTipoCriticidad');
        const criticidadId = UI.form.getValue('editCriticidad');

        if (!name || !productoId || !tipoCriticidadId || !criticidadId) {
            UI.showAlert("Todos los campos son obligatorios", 'warning');
            return;
        }

        const response = await TipoEquipoService.actualizar(id, {
            name,
            producto_id: productoId,
            tipo_criticidad_id: tipoCriticidadId,
            criticidad_id: criticidadId
        });
        
        if (response.success) {
            UI.showAlert(response.message || "Tipo de equipo actualizado exitosamente", 'success');
            bootstrap.Modal.getInstance(document.getElementById('editModal')).hide();
            loadTiposEquipo(currentPage);
        } else {
            UI.showAlert(response.error || "Error al actualizar el tipo de equipo", 'error');
        }
    });

    // Eventos para los dropdowns del modal de edición
    document.getElementById('editProducto')?.addEventListener('change', function() {
        const productoId = this.value;
        const tipoCriticidadDropdown = document.getElementById('editTipoCriticidad');
        const criticidadDropdown = document.getElementById('editCriticidad');
        
        if (productoId) {
            cargarTiposCriticidadPorProducto(productoId, 'editTipoCriticidad');
        } else {
            tipoCriticidadDropdown.innerHTML = '<option value="">Seleccione tipo</option>';
            tipoCriticidadDropdown.disabled = true;
            criticidadDropdown.innerHTML = '<option value="">Seleccione criticidad</option>';
            criticidadDropdown.disabled = true;
        }
    });

    document.getElementById('editTipoCriticidad')?.addEventListener('change', function() {
        const tipoCriticidadId = this.value;
        const criticidadDropdown = document.getElementById('editCriticidad');
        
        if (tipoCriticidadId) {
            cargarCriticidadesPorTipo(tipoCriticidadId, 'editCriticidad');
        } else {
            criticidadDropdown.innerHTML = '<option value="">Seleccione criticidad</option>';
            criticidadDropdown.disabled = true;
        }
    });
});
