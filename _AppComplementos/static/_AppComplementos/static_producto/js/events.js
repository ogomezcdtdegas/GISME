// events.js - Eventos específicos de productos
import { ProductosService, TipoCriticidadService, CriticidadService } from '../../../../static/js/global/api/index.js';
import { UI } from '../../../../static/js/global/utils/ui.js';

let currentPage = 1;
const DEFAULT_PER_PAGE = 10;

// Función para actualizar la tabla de productos
function actualizarTablaProductos(data) {
    const tbody = document.getElementById('prodTableBody');
    if (!tbody) return;

    tbody.innerHTML = '';
    
    if (!data || data.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="4" class="text-center">No hay productos registrados</td>
            </tr>`;
        return;
    }

    data.forEach(item => {
        const row = document.createElement('tr');
        const hasMultipleRelations = item.total_relations > 1;
        row.innerHTML = `
            <td>
                ${UI.utils.escapeHtml(item.producto_name)}
                ${hasMultipleRelations ? `<span class="badge bg-info ms-2" title="Este producto tiene ${item.total_relations} relaciones">${item.total_relations}</span>` : ''}
            </td>
            <td>${UI.utils.escapeHtml(item.tipo_criticidad_name)}</td>
            <td>${UI.utils.escapeHtml(item.criticidad_name)}</td>
            <td class="text-center">
                <div class="btn-group" role="group">
                    <button class="btn btn-primary btn-sm me-1" 
                        data-id="${item.producto_id}"
                        data-producto-name="${UI.utils.escapeHtml(item.producto_name)}"
                        data-tipo-criticidad-id="${item.tipo_criticidad_id}"
                        data-criticidad-id="${item.criticidad_id}"
                        onclick="window.openEditModal(this.dataset.id, this.dataset.productoName, this.dataset.tipoCriticidadId, this.dataset.criticidadId)"
                        style="white-space: nowrap;">
                        <i class="bi bi-pencil-square"></i>
                    </button>
                    <button class="btn btn-danger btn-sm" 
                        onclick="window.deleteProducto('${item.id}', '${item.producto_id}', '${UI.utils.escapeHtml(item.producto_name)}')"
                        title="${hasMultipleRelations ? 'Eliminar relación o producto completo' : 'Eliminar producto'}">
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
                loadProductos(newPage);
            }
        });
    });
}

async function loadProductos(page = currentPage, search = '') {
    try {
        UI.loading.show('prodTableBody');
        
        const perPage = parseInt(document.getElementById('recordsPerPage')?.value) || DEFAULT_PER_PAGE;
        const searchQuery = search || document.getElementById('searchInput')?.value || '';
        
        const response = await ProductosService.listarTodo(page, perPage, 'producto__name', searchQuery);
        
        if (response && response.results) {
            actualizarTablaProductos(response.results);
            actualizarPaginacion(response, page, perPage);
            currentPage = page;
            
            // Mostrar mensaje si no hay resultados en la búsqueda
            if (response.results.length === 0 && searchQuery) {
                const tbody = document.getElementById('prodTableBody');
                if (tbody) {
                    tbody.innerHTML = `
                        <tr>
                            <td colspan="4" class="text-center">
                                <i class="bi bi-search"></i>
                                No se encontraron productos que coincidan con "${searchQuery}"
                            </td>
                        </tr>`;
                }
            }
        } else {
            UI.toast.error("Error al cargar los productos");
        }
    } catch (error) {
        console.error("Error:", error);
        UI.toast.error("Error al cargar los datos");
    } finally {
        UI.loading.hide('prodTableBody');
    }
}

// Función para cargar los tipos de criticidad en el dropdown
async function cargarTiposCriticidad(dropdownId = 'tipocriticidadDropdown', selectedValue = null) {
    try {
        const response = await TipoCriticidadService.listarUnicos();
        const dropdown = document.getElementById(dropdownId);
        
        if (!dropdown || !response?.results) {
            console.error('Error al cargar tipos de criticidad:', response);
            return;
        }

        dropdown.innerHTML = '<option value="">Seleccione un tipo de criticidad</option>';
        
        // Los tipos ahora vienen únicos directamente del backend
        const sortedTipos = response.results.sort((a, b) => a.name.localeCompare(b.name));
        
        sortedTipos.forEach(tipo => {
            const option = document.createElement('option');
            option.value = tipo.id;
            option.textContent = tipo.name;
            if (selectedValue && String(tipo.id) === String(selectedValue)) {
                option.selected = true;
            }
            dropdown.appendChild(option);
        });
    } catch (error) {
        console.error('Error al cargar tipos de criticidad:', error);
        UI.toast.error('Error al cargar los tipos de criticidad');
    }
}

// Función para cargar las criticidades filtradas por tipo
async function cargarCriticidadesPorTipo(tipoId, dropdownId = 'criticidadDropdown', selectedValue = null) {
    try {
        const dropdown = document.getElementById(dropdownId);
        if (!dropdown) return;

        // Validar que tipoId no sea undefined, null o string vacío
        if (!tipoId || tipoId === 'undefined' || tipoId === 'null') {
            dropdown.innerHTML = '<option value="">Seleccione un tipo primero</option>';
            dropdown.disabled = true;
            return;
        }

        dropdown.disabled = true;
        dropdown.innerHTML = '<option value="">Cargando...</option>';

        const criticidades = await CriticidadService.listarPorTipo(tipoId);
        
        dropdown.innerHTML = '<option value="">Seleccione una criticidad</option>';
        
        if (criticidades && criticidades.length > 0) {
            const sortedCriticidades = criticidades.sort((a, b) => a.name.localeCompare(b.name));
            
            sortedCriticidades.forEach(criticidad => {
                const option = document.createElement('option');
                option.value = criticidad.id;
                option.textContent = criticidad.name;
                if (selectedValue && String(criticidad.id) === String(selectedValue)) {
                    option.selected = true;
                }
                dropdown.appendChild(option);
            });
            dropdown.disabled = false;
        } else {
            dropdown.innerHTML = '<option value="">No hay criticidades disponibles</option>';
            dropdown.disabled = true;
        }
    } catch (error) {
        console.error('Error al cargar criticidades:', error);
        const dropdown = document.getElementById(dropdownId);
        if (dropdown) {
            dropdown.innerHTML = '<option value="">Error al cargar</option>';
            dropdown.disabled = true;
        }
        UI.toast.error('Error al cargar las criticidades');
    }
}

// Función para cargar productos en un dropdown
async function cargarProductos(dropdownId = 'productoDropdown', selectedValue = null) {
    try {
        const response = await ProductosService.listarTodo(1, 1000); // Get all products for dropdown
        const dropdown = document.getElementById(dropdownId);
        
        if (!dropdown || !response?.results) {
            console.error('Error al cargar productos:', response);
            return;
        }

        dropdown.innerHTML = '<option value="">Seleccione un producto</option>';
        
        // Obtener productos únicos (usar el primer tipo_criticidad encontrado para cada producto)
        const productosUnicos = response.results.reduce((acc, curr) => {
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
        UI.toast.error('Error al cargar los productos');
    }
}

// Función global para abrir el modal de edición
window.openEditModal = async function(id, name, tipoCriticidadId, criticidadId) {
    try {
        console.log('Abriendo modal con:', { id, name, tipoCriticidadId, criticidadId });
        
        const modalElement = document.getElementById('editModal');
        
        // Configurar valores básicos del formulario
        UI.form.setValue('editprodId', id);
        UI.form.setValue('editprodName', name);
        
        // Cargar tipos de criticidad primero
        await cargarTiposCriticidad('editTipoCriticidad', tipoCriticidadId);
        
        // Luego cargar criticidades para ese tipo y seleccionar la correcta
        if (tipoCriticidadId) {
            await cargarCriticidadesPorTipo(tipoCriticidadId, 'editCriticidad', criticidadId);
        }
        
        const modal = new bootstrap.Modal(modalElement);
        modal.show();
    } catch (error) {
        console.error('Error al abrir el modal:', error);
        UI.toast.error('Error al cargar los datos para edición');
    }
};

// Función global para actualizar paginación cuando cambia el selector
window.updatePagination = function() {
    loadProductos(1); // Ir a la primera página cuando cambia la cantidad de registros
};

// Función para manejar la eliminación de productos
window.deleteProducto = async function(relacionId, productoId, productoName) {
    try {
        let deleteType;

        // Obtener el total de relaciones del producto
        const productoDetails = await ProductosService.listarTodo(1, 1000); // Temporal: Get all to count relations
        const productoInfo = productoDetails.results.find(p => String(p.producto_id) === String(productoId));
        const hasMultipleRelations = productoInfo?.total_relations > 1;

        if (hasMultipleRelations) {
            // Si tiene múltiples relaciones, mostrar diálogo con opciones
            const result = await Swal.fire({
                title: `¿Qué desea eliminar?`,
                html: `
                    <div class="text-start">
                        <p>El producto "${productoName}" tiene ${productoInfo.total_relations} relaciones.</p>
                        <div class="form-check">
                            <input class="form-check-input" type="radio" name="deleteType" id="deleteRelation" value="relation" checked>
                            <label class="form-check-label" for="deleteRelation">
                                Solo eliminar esta relación
                            </label>
                        </div>
                        <div class="form-check mt-2">
                            <input class="form-check-input" type="radio" name="deleteType" id="deleteProduct" value="product">
                            <label class="form-check-label" for="deleteProduct">
                                Eliminar el producto y todas sus relaciones
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
                html: `Esta es la última relación del producto "${productoName}".<br>El producto será eliminado completamente.`,
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
        if (deleteType === 'product') {
            response = await ProductosService.eliminarProducto(productoId);
        } else {
            response = await ProductosService.eliminarRelacion(relacionId);
        }

        if (response?.success) {
            UI.toast.success(response.message);
            
            // Si era la última relación o se eliminó el producto completo, actualizar las listas
            if (response.was_last_relation || deleteType === 'product') {
                // Recargar los dropdowns de productos si están presentes
                const dropdowns = document.querySelectorAll('[id^=productoDropdown]');
                for (const dropdown of dropdowns) {
                    await cargarProductos(dropdown.id);
                }
            }

            // Recargar la tabla de productos
            await loadProductos(currentPage);
        } else {
            UI.toast.error(response?.message || 'Error al eliminar el producto');
        }
    } catch (error) {
        console.error('Error:', error);
        UI.toast.error('Error al procesar la solicitud');
    } finally {
        UI.loading.hide();
    }
};

document.addEventListener("DOMContentLoaded", async function () {
    console.log("🟢 Página de productos cargada - Inicializando...");
    await loadProductos();
    await cargarTiposCriticidad();

    // Event Listeners
    document.getElementById('recordsPerPage')?.addEventListener('change', () => {
        currentPage = 1;
        loadProductos();
    });

    // Event listeners para búsqueda
    let searchTimeout;
    const searchInput = document.getElementById('searchInput');
    const clearButton = document.getElementById('clearSearch');

    if (searchInput) {
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                currentPage = 1;
                loadProductos(1, this.value);
            }, 300); // Debounce de 300ms
        });
    }

    if (clearButton) {
        clearButton.addEventListener('click', function() {
            if (searchInput) {
                searchInput.value = '';
                currentPage = 1;
                loadProductos(1, '');
            }
        });
    }

    // Event listener para el cambio de tipo de criticidad
    ['tipocriticidadDropdown', 'editTipoCriticidad'].forEach(dropdownId => {
        document.getElementById(dropdownId)?.addEventListener('change', async function(event) {
            const targetDropdownId = dropdownId === 'tipocriticidadDropdown' ? 'criticidadDropdown' : 'editCriticidad';
            await cargarCriticidadesPorTipo(event.target.value, targetDropdownId);
        });
    });

    document.getElementById('prodForm')?.addEventListener('submit', async function(event) {
        event.preventDefault();
        
        const name = UI.form.getValue('name');
        const tipoId = UI.form.getValue('tipocriticidadDropdown');
        const criticidadId = UI.form.getValue('criticidadDropdown');
        
        if (!name || !tipoId || !criticidadId) {
            UI.toast.warning("Todos los campos son obligatorios");
            return;
        }
        
        const response = await ProductosService.crear(name, tipoId, criticidadId);
        
        if (response.success) {
            UI.toast.success(response.message || "Producto creado exitosamente");
            loadProductos();
            UI.form.reset('prodForm');
            document.getElementById('criticidadDropdown').disabled = true;
            document.getElementById('criticidadDropdown').innerHTML = '<option value="">Seleccione un tipo primero</option>';
        } else {
            UI.toast.error(response.error || "Error al crear el producto");
        }
    });

    document.getElementById("editprodForm")?.addEventListener("submit", async function(event) {
        event.preventDefault();
        
        const id = UI.form.getValue("editprodId");
        const name = UI.form.getValue("editprodName");
        const tipoCriticidadId = UI.form.getValue("editTipoCriticidad");
        const criticidadId = UI.form.getValue("editCriticidad");
        
        if (!name || !tipoCriticidadId || !criticidadId) {
            UI.toast.warning("Todos los campos son obligatorios");
            return;
        }
        
        const response = await ProductosService.actualizar(id, {
            name,
            tipo_criticidad_id: tipoCriticidadId,
            criticidad_id: criticidadId
        });
        
        if (response.success) {
            UI.toast.success(response.message || "Producto actualizado exitosamente");
            bootstrap.Modal.getInstance(document.getElementById('editModal')).hide();
            loadProductos(currentPage);
        } else {
            UI.toast.error(response.error || "Error al actualizar el producto");
        }
    });
});
