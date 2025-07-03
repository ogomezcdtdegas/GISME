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
        row.innerHTML = `
            <td>${UI.utils.escapeHtml(item.producto_name)}</td>
            <td>${UI.utils.escapeHtml(item.tipo_criticidad_name)}</td>
            <td>${UI.utils.escapeHtml(item.criticidad_name)}</td>
            <td class="text-center">
                <button class="btn btn-primary btn-sm d-inline-block" 
                    data-id="${item.id}"
                    data-producto-name="${UI.utils.escapeHtml(item.producto_name)}"
                    data-tipo-criticidad-id="${item.tipo_criticidad_id}"
                    data-criticidad-id="${item.criticidad_id}"
                    onclick="window.openEditModal(this.dataset.id, this.dataset.productoName, this.dataset.tipoCriticidadId, this.dataset.criticidadId)"
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
                loadProductos(newPage);
            }
        });
    });
}

async function loadProductos(page = currentPage) {
    try {
        UI.loading.show('prodTableBody');
        
        const perPage = parseInt(document.getElementById('recordsPerPage')?.value) || DEFAULT_PER_PAGE;
        const response = await ProductosService.listarTodo(page, perPage);
        
        if (response && response.results) {
            actualizarTablaProductos(response.results);
            actualizarPaginacion(response, page, perPage);
            currentPage = page;
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

document.addEventListener("DOMContentLoaded", async function () {
    console.log("🟢 Página de productos cargada - Inicializando...");
    await loadProductos();
    await cargarTiposCriticidad();

    // Event Listeners
    document.getElementById('recordsPerPage')?.addEventListener('change', () => {
        currentPage = 1;
        loadProductos();
    });

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
