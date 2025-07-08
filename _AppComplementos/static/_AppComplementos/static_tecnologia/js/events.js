// events.js - Eventos específicos de tecnología
import { TecnologiaService, TipoEquipoService, ProductosService, TipoCriticidadService, CriticidadService } from '../../../../static/js/global/api/index.js';
import { UI } from '../../../../static/js/global/utils/ui.js';

let currentPage = 1;
const DEFAULT_PER_PAGE = 10;

// Función para actualizar la tabla de tecnologías con agrupación visual
function actualizarTablaTecnologias(data) {
    const tbody = document.getElementById('tecnologiaTableBody');
    if (!tbody) return;

    tbody.innerHTML = '';
    
    if (!data || data.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center">No hay tecnologías registradas</td>
            </tr>`;
        return;
    }

    // Agrupar por tecnologia_id
    const grupos = {};
    data.forEach(item => {
        const grupoId = item.tecnologia_id || 'sin_grupo';
        if (!grupos[grupoId]) {
            grupos[grupoId] = {
                nombre: item.tecnologia_name || '',
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
                                <span class="main-name">${item.tecnologia_name}</span>
                                <br><span class="badge bg-info mt-1" title="Esta tecnología tiene ${cantidadItems} ${cantidadItems === 1 ? 'combinación' : 'combinaciones'}">${badgeText}</span>
                            </div>
                        </td>
                        <td>${item.tipo_equipo_name}</td>
                        <td>${item.producto_name}</td>
                        <td>${item.tipo_criticidad_name}</td>
                        <td>${item.criticidad_name}</td>
                        <td>
                            <button class="btn btn-primary btn-sm me-1" 
                                    onclick="openEditTecnologiaModal('${item.id}')">
                                <i class="bi bi-pencil-square"></i>
                            </button>
                            <button class="btn btn-danger btn-sm" 
                                    onclick="deleteTecnologia('${item.id}')">
                                <i class="bi bi-trash"></i>
                            </button>
                        </td>
                    </tr>
                `;
            } else {
                // Filas adicionales del grupo: solo combinaciones
                htmlContent += `
                    <tr class="${groupClass}" data-group-id="${grupoId}">
                        <td>${item.tipo_equipo_name}</td>
                        <td>${item.producto_name}</td>
                        <td>${item.tipo_criticidad_name}</td>
                        <td>${item.criticidad_name}</td>
                        <td>
                            <button class="btn btn-primary btn-sm me-1" 
                                    onclick="openEditTecnologiaModal('${item.id}')">
                                <i class="bi bi-pencil-square"></i>
                            </button>
                            <button class="btn btn-danger btn-sm" 
                                    onclick="deleteTecnologia('${item.id}')">
                                <i class="bi bi-trash"></i>
                            </button>
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
}

// Función para aplicar efectos de hover por grupo
function aplicarEfectosHover() {
    const tbody = document.getElementById('tecnologiaTableBody');
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

// Función para cargar datos de tecnologías
async function cargarTecnologias(page = 1, perPage = DEFAULT_PER_PAGE, search = '') {
    try {
        const response = await TecnologiaService.getAll(page, perPage, search);
        
        if (response.success !== false) {
            actualizarTablaTecnologias(response.results || response);
            updatePaginationInfo(response);
        } else {
            console.error('Error al cargar tecnologías:', response.error);
        }
    } catch (error) {
        console.error('Error al cargar tecnologías:', error);
    }
}

// Función para actualizar información de paginación
function updatePaginationInfo(response) {
    const pagination = document.querySelector('.pagination');
    if (!pagination) return;

    pagination.innerHTML = '';
    
    if (response.total_pages && response.total_pages > 1) {
        // Botón anterior
        if (response.has_previous) {
            pagination.innerHTML += `
                <li class="page-item">
                    <a class="page-link" href="#" onclick="changePage(${response.previous_page_number})">&laquo; Anterior</a>
                </li>`;
        }

        // Números de página
        for (let i = 1; i <= response.total_pages; i++) {
            const isActive = i === response.current_page ? 'active' : '';
            pagination.innerHTML += `
                <li class="page-item ${isActive}">
                    <a class="page-link" href="#" onclick="changePage(${i})">${i}</a>
                </li>`;
        }

        // Botón siguiente
        if (response.has_next) {
            pagination.innerHTML += `
                <li class="page-item">
                    <a class="page-link" href="#" onclick="changePage(${response.next_page_number})">Siguiente &raquo;</a>
                </li>`;
        }
    }
}

// Función para cambiar página
window.changePage = function(page) {
    currentPage = page;
    const perPage = document.getElementById('recordsPerPage').value;
    const search = document.getElementById('searchInput').value;
    cargarTecnologias(page, perPage, search);
};

// Función para actualizar paginación
window.updatePagination = function() {
    const perPage = document.getElementById('recordsPerPage').value;
    const search = document.getElementById('searchInput').value;
    currentPage = 1;
    cargarTecnologias(currentPage, perPage, search);
};

// Función para cargar dropdowns encadenados
async function cargarTiposEquipo() {
    try {
        const response = await TecnologiaService.getTiposEquipoUnicos();
        const select = document.getElementById('tipoEquipoDropdown');
        const editSelect = document.getElementById('editTipoEquipoDropdown');
        
        [select, editSelect].forEach(dropdown => {
            if (dropdown) {
                dropdown.innerHTML = '<option value="">Seleccione un tipo de equipo</option>';
                response.results.forEach(tipo => {
                    dropdown.innerHTML += `<option value="${tipo.id}">${tipo.name}</option>`;
                });
            }
        });
    } catch (error) {
        console.error('Error al cargar tipos de equipo:', error);
    }
}

async function cargarProductosPorTipoEquipo(tipoEquipoId, targetSelectId) {
    try {
        const response = await TecnologiaService.getProductosPorTipoEquipo(tipoEquipoId);
        const select = document.getElementById(targetSelectId);
        
        if (select) {
            select.innerHTML = '<option value="">Seleccione un producto</option>';
            select.disabled = false;
            
            response.results.forEach(producto => {
                select.innerHTML += `<option value="${producto.id}">${producto.name}</option>`;
            });
        }
    } catch (error) {
        console.error('Error al cargar productos:', error);
    }
}

async function cargarTiposCriticidadPorProducto(productoId, targetSelectId) {
    try {
        const response = await TecnologiaService.getTiposCriticidadPorProducto(productoId);
        const select = document.getElementById(targetSelectId);
        
        if (select) {
            select.innerHTML = '<option value="">Seleccione un tipo de criticidad</option>';
            select.disabled = false;
            
            response.results.forEach(tipo => {
                select.innerHTML += `<option value="${tipo.id}">${tipo.name}</option>`;
            });
        }
    } catch (error) {
        console.error('Error al cargar tipos de criticidad:', error);
    }
}

async function cargarCriticidadesPorTipo(tipoCriticidadId, targetSelectId) {
    try {
        const response = await TecnologiaService.getCriticidadesPorTipo(tipoCriticidadId);
        const select = document.getElementById(targetSelectId);
        
        if (select) {
            select.innerHTML = '<option value="">Seleccione una criticidad</option>';
            select.disabled = false;
            
            response.results.forEach(criticidad => {
                select.innerHTML += `<option value="${criticidad.id}">${criticidad.name}</option>`;
            });
        }
    } catch (error) {
        console.error('Error al cargar criticidades:', error);
    }
}

// Función para abrir modal de edición
window.openEditTecnologiaModal = async function(tecnologiaId) {
    try {
        const response = await TecnologiaService.getById(tecnologiaId);
        
        if (response.success !== false) {
            const tecnologia = response.data || response;
            
            // Llenar los campos del modal
            document.getElementById('editTecnologiaId').value = tecnologia.id;
            document.getElementById('editName').value = tecnologia.tecnologia_name;
            
            // Cargar y seleccionar tipo de equipo
            await cargarTiposEquipo();
            document.getElementById('editTipoEquipoDropdown').value = tecnologia.tipo_equipo_id;
            
            // Cargar y seleccionar producto
            await cargarProductosPorTipoEquipo(tecnologia.tipo_equipo_id, 'editProductoDropdown');
            document.getElementById('editProductoDropdown').value = tecnologia.producto_id;
            
            // Cargar y seleccionar tipo de criticidad
            await cargarTiposCriticidadPorProducto(tecnologia.producto_id, 'editTipoCriticidadDropdown');
            document.getElementById('editTipoCriticidadDropdown').value = tecnologia.tipo_criticidad_id;
            
            // Cargar y seleccionar criticidad
            await cargarCriticidadesPorTipo(tecnologia.tipo_criticidad_id, 'editCriticidadDropdown');
            document.getElementById('editCriticidadDropdown').value = tecnologia.criticidad_id;
            
            // Mostrar modal
            const modal = new bootstrap.Modal(document.getElementById('editTecnologiaModal'));
            modal.show();
        }
    } catch (error) {
        console.error('Error al cargar datos de tecnología:', error);
        UI.showAlert('Error al cargar los datos de la tecnología', 'error');
    }
};

// Función para eliminar tecnología
window.deleteTecnologia = async function(tecnologiaId) {
    if (confirm('¿Está seguro de que desea eliminar esta tecnología?')) {
        try {
            const response = await TecnologiaService.delete(tecnologiaId);
            
            if (response.success) {
                UI.showAlert(response.message, 'success');
                cargarTecnologias(currentPage);
            } else {
                UI.showAlert(response.error || 'Error al eliminar la tecnología', 'error');
            }
        } catch (error) {
            console.error('Error al eliminar tecnología:', error);
            UI.showAlert('Error al eliminar la tecnología', 'error');
        }
    }
};

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    // Cargar datos iniciales
    cargarTecnologias();
    cargarTiposEquipo();

    // Form de registro
    const form = document.getElementById('tecnologiaForm');
    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(form);
            const data = {
                name: formData.get('name'),
                tipo_equipo_id: document.getElementById('tipoEquipoDropdown').value,
                producto_id: document.getElementById('productoDropdown').value,
                tipo_criticidad_id: document.getElementById('tipoCriticidadDropdown').value,
                criticidad_id: document.getElementById('criticidadDropdown').value
            };

            try {
                const response = await TecnologiaService.create(data);
                
                if (response.success) {
                    UI.showAlert(response.message, 'success');
                    form.reset();
                    // Resetear dropdowns
                    ['productoDropdown', 'tipoCriticidadDropdown', 'criticidadDropdown'].forEach(id => {
                        const select = document.getElementById(id);
                        if (select) {
                            select.innerHTML = '<option value="">Seleccione...</option>';
                            select.disabled = true;
                        }
                    });
                    cargarTecnologias(currentPage);
                } else {
                    UI.showAlert(response.error || 'Error al registrar la tecnología', 'error');
                }
            } catch (error) {
                console.error('Error al registrar tecnología:', error);
                UI.showAlert('Error al registrar la tecnología', 'error');
            }
        });
    }

    // Form de edición
    const saveBtn = document.getElementById('saveTecnologiaBtn');
    if (saveBtn) {
        saveBtn.addEventListener('click', async function() {
            const tecnologiaId = document.getElementById('editTecnologiaId').value;
            const data = {
                name: document.getElementById('editName').value,
                tipo_equipo_id: document.getElementById('editTipoEquipoDropdown').value,
                producto_id: document.getElementById('editProductoDropdown').value,
                tipo_criticidad_id: document.getElementById('editTipoCriticidadDropdown').value,
                criticidad_id: document.getElementById('editCriticidadDropdown').value
            };

            try {
                const response = await TecnologiaService.update(tecnologiaId, data);
                
                if (response.success) {
                    UI.showAlert(response.message, 'success');
                    const modal = bootstrap.Modal.getInstance(document.getElementById('editTecnologiaModal'));
                    modal.hide();
                    cargarTecnologias(currentPage);
                } else {
                    UI.showAlert(response.error || 'Error al actualizar la tecnología', 'error');
                }
            } catch (error) {
                console.error('Error al actualizar tecnología:', error);
                UI.showAlert('Error al actualizar la tecnología', 'error');
            }
        });
    }

    // Búsqueda
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                const search = this.value;
                const perPage = document.getElementById('recordsPerPage').value;
                currentPage = 1;
                cargarTecnologias(currentPage, perPage, search);
            }, 300);
        });
    }

    // Limpiar búsqueda
    const clearSearch = document.getElementById('clearSearch');
    if (clearSearch) {
        clearSearch.addEventListener('click', function() {
            document.getElementById('searchInput').value = '';
            const perPage = document.getElementById('recordsPerPage').value;
            currentPage = 1;
            cargarTecnologias(currentPage, perPage, '');
        });
    }

    // Dropdowns encadenados - Formulario principal
    const tipoEquipoDropdown = document.getElementById('tipoEquipoDropdown');
    if (tipoEquipoDropdown) {
        tipoEquipoDropdown.addEventListener('change', function() {
            const tipoEquipoId = this.value;
            const productoDropdown = document.getElementById('productoDropdown');
            const tipoCriticidadDropdown = document.getElementById('tipoCriticidadDropdown');
            const criticidadDropdown = document.getElementById('criticidadDropdown');
            
            // Reset dropdowns dependientes
            [tipoCriticidadDropdown, criticidadDropdown].forEach(dropdown => {
                if (dropdown) {
                    dropdown.innerHTML = '<option value="">Seleccione...</option>';
                    dropdown.disabled = true;
                }
            });
            
            if (tipoEquipoId) {
                cargarProductosPorTipoEquipo(tipoEquipoId, 'productoDropdown');
            } else {
                productoDropdown.innerHTML = '<option value="">Seleccione un producto</option>';
                productoDropdown.disabled = true;
            }
        });
    }

    const productoDropdown = document.getElementById('productoDropdown');
    if (productoDropdown) {
        productoDropdown.addEventListener('change', function() {
            const productoId = this.value;
            const criticidadDropdown = document.getElementById('criticidadDropdown');
            
            // Reset dropdown dependiente
            criticidadDropdown.innerHTML = '<option value="">Seleccione una criticidad</option>';
            criticidadDropdown.disabled = true;
            
            if (productoId) {
                cargarTiposCriticidadPorProducto(productoId, 'tipoCriticidadDropdown');
            } else {
                document.getElementById('tipoCriticidadDropdown').innerHTML = '<option value="">Seleccione un tipo de criticidad</option>';
                document.getElementById('tipoCriticidadDropdown').disabled = true;
            }
        });
    }

    const tipoCriticidadDropdown = document.getElementById('tipoCriticidadDropdown');
    if (tipoCriticidadDropdown) {
        tipoCriticidadDropdown.addEventListener('change', function() {
            const tipoCriticidadId = this.value;
            
            if (tipoCriticidadId) {
                cargarCriticidadesPorTipo(tipoCriticidadId, 'criticidadDropdown');
            } else {
                document.getElementById('criticidadDropdown').innerHTML = '<option value="">Seleccione una criticidad</option>';
                document.getElementById('criticidadDropdown').disabled = true;
            }
        });
    }

    // Dropdowns encadenados - Modal de edición
    const editTipoEquipoDropdown = document.getElementById('editTipoEquipoDropdown');
    if (editTipoEquipoDropdown) {
        editTipoEquipoDropdown.addEventListener('change', function() {
            const tipoEquipoId = this.value;
            const editProductoDropdown = document.getElementById('editProductoDropdown');
            const editTipoCriticidadDropdown = document.getElementById('editTipoCriticidadDropdown');
            const editCriticidadDropdown = document.getElementById('editCriticidadDropdown');
            
            // Reset dropdowns dependientes
            [editTipoCriticidadDropdown, editCriticidadDropdown].forEach(dropdown => {
                if (dropdown) {
                    dropdown.innerHTML = '<option value="">Seleccione...</option>';
                    dropdown.disabled = true;
                }
            });
            
            if (tipoEquipoId) {
                cargarProductosPorTipoEquipo(tipoEquipoId, 'editProductoDropdown');
            } else {
                editProductoDropdown.innerHTML = '<option value="">Seleccione un producto</option>';
                editProductoDropdown.disabled = true;
            }
        });
    }

    const editProductoDropdown = document.getElementById('editProductoDropdown');
    if (editProductoDropdown) {
        editProductoDropdown.addEventListener('change', function() {
            const productoId = this.value;
            const editCriticidadDropdown = document.getElementById('editCriticidadDropdown');
            
            // Reset dropdown dependiente
            editCriticidadDropdown.innerHTML = '<option value="">Seleccione una criticidad</option>';
            editCriticidadDropdown.disabled = true;
            
            if (productoId) {
                cargarTiposCriticidadPorProducto(productoId, 'editTipoCriticidadDropdown');
            } else {
                document.getElementById('editTipoCriticidadDropdown').innerHTML = '<option value="">Seleccione un tipo de criticidad</option>';
                document.getElementById('editTipoCriticidadDropdown').disabled = true;
            }
        });
    }

    const editTipoCriticidadDropdown = document.getElementById('editTipoCriticidadDropdown');
    if (editTipoCriticidadDropdown) {
        editTipoCriticidadDropdown.addEventListener('change', function() {
            const tipoCriticidadId = this.value;
            
            if (tipoCriticidadId) {
                cargarCriticidadesPorTipo(tipoCriticidadId, 'editCriticidadDropdown');
            } else {
                document.getElementById('editCriticidadDropdown').innerHTML = '<option value="">Seleccione una criticidad</option>';
                document.getElementById('editCriticidadDropdown').disabled = true;
            }
        });
    }

    // Cargar datos iniciales
    cargarTecnologias(currentPage);
    cargarTiposEquipo();
});
