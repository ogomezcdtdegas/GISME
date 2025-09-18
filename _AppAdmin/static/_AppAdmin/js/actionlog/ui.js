/**
 * UI functions para action logs
 * Renderizado de tabla, paginación y elementos de interfaz
 */

/**
 * Renderizar logs de acciones en la tabla
 * @param {Array} logs - Array de logs de acciones
 */
export function renderActionLogs(logs) {
    const tbody = document.getElementById('actionLogsTableBody');
    if (!tbody) {
        console.error('❌ No se encontró el elemento actionLogsTableBody');
        return;
    }

    if (!logs || logs.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="4" class="text-center">
                    <i class="bi bi-info-circle"></i>
                    No hay registros de acciones disponibles
                </td>
            </tr>`;
        return;
    }

    tbody.innerHTML = logs.map(log => `
        <tr>
            <td>
                <strong>${escapeHtml(log.usuario || log.email)}</strong>
                <br>
                <small class="text-muted">${escapeHtml(log.email)}</small>
            </td>
            <td>
                <span class="badge ${getActionBadgeClass(log.action)}">${escapeHtml(log.accion_display)}</span>
            </td>
            <td>
                ${formatDateTime(log.action_datetime)}
            </td>
            <td>
                <span class="badge bg-info">${escapeHtml(log.tipo_display)}</span>
                <br>
                <small class="text-muted">${escapeHtml(log.affected_value)}</small>
            </td>
        </tr>
    `).join('');
}

/**
 * Obtener clase CSS para el badge de acción
 * @param {string} action - Acción realizada
 * @returns {string} - Clase CSS para el badge
 */
function getActionBadgeClass(action) {
    const actionClasses = {
        'crear': 'bg-success',
        'editar': 'bg-warning',
        'inactivar': 'bg-danger',
        'activar': 'bg-primary'
    };
    return actionClasses[action] || 'bg-secondary';
}

/**
 * Renderizar controles de paginación
 * @param {Object} paginationData - Datos de paginación del backend
 */
export function renderPagination(paginationData) {
    const paginationContainer = document.querySelector('.pagination');
    if (!paginationContainer) return;

    // Limpiar contenido previo completamente
    paginationContainer.innerHTML = '';
    
    // Crear nuevo container para evitar event listeners múltiples
    const newContainer = paginationContainer.cloneNode(false);
    paginationContainer.parentNode.replaceChild(newContainer, paginationContainer);
    
    // Usar el nuevo container para el resto de la función
    const activeContainer = document.querySelector('.pagination');

    // Si es un array simple o no hay datos de paginación, no mostrar controles
    if (Array.isArray(paginationData) || !paginationData || !paginationData.total_count) {
        return;
    }

    const count = paginationData.total_count || 0;
    const currentPage = paginationData.current_page || 1;
    const totalPages = paginationData.total_pages || 1;
    const hasPrevious = paginationData.has_previous || false;
    const hasNext = paginationData.has_next || false;
    
    // No mostrar paginación si solo hay una página
    if (totalPages <= 1) {
        return;
    }

    // Botón Previous
    const prevLi = document.createElement('li');
    prevLi.className = `page-item ${!hasPrevious ? 'disabled' : ''}`;
    if (hasPrevious) {
        prevLi.innerHTML = `<a class="page-link" href="#" data-page="${currentPage - 1}">Anterior</a>`;
    } else {
        prevLi.innerHTML = `<span class="page-link">Anterior</span>`;
    }
    activeContainer.appendChild(prevLi);

    // Información de página actual
    const currentLi = document.createElement('li');
    currentLi.className = 'page-item disabled';
    currentLi.innerHTML = `<span class="page-link">Página ${currentPage} de ${totalPages}</span>`;
    activeContainer.appendChild(currentLi);

    // Botón Next
    const nextLi = document.createElement('li');
    nextLi.className = `page-item ${!hasNext ? 'disabled' : ''}`;
    if (hasNext) {
        nextLi.innerHTML = `<a class="page-link" href="#" data-page="${currentPage + 1}">Siguiente</a>`;
    } else {
        nextLi.innerHTML = `<span class="page-link">Siguiente</span>`;
    }
    activeContainer.appendChild(nextLi);

    // Agregar event listener único
    activeContainer.addEventListener('click', function(e) {
        e.preventDefault();
        const page = e.target.dataset.page;
        if (page && !e.target.closest('.disabled')) {
            // Importar y usar goToPage desde events
            import('./events.js').then(({ goToPage }) => {
                goToPage(parseInt(page));
            });
        }
    });
}

/**
 * Actualizar información de registros
 * @param {Object} paginationData - Datos de paginación
 */
export function updateRecordsInfo(paginationData) {
    const recordsInfo = document.getElementById('recordsInfo');
    if (!recordsInfo) return;

    // Si es un array simple, mostrar información básica
    if (Array.isArray(paginationData)) {
        recordsInfo.textContent = `Mostrando ${paginationData.length} registros`;
        return;
    }

    // Si es objeto de paginación con BaseListView
    if (paginationData && typeof paginationData === 'object') {
        const count = paginationData.total_count || 0;
        const currentPage = paginationData.current_page || 1;
        const totalPages = paginationData.total_pages || 1;
        
        // Calcular registros por página basado en los datos reales
        const recordsPerPage = Math.ceil(count / totalPages) || 10;
        
        if (count > 0) {
            const start = ((currentPage - 1) * recordsPerPage) + 1;
            const end = Math.min(currentPage * recordsPerPage, count);
            recordsInfo.textContent = `Mostrando ${start} a ${end} de ${count} registros`;
        } else {
            recordsInfo.textContent = 'No hay registros disponibles';
        }
    } else {
        recordsInfo.textContent = 'Cargando...';
    }
}

/**
 * Formatear fecha y hora para mostrar
 * @param {string} dateTimeString - String de fecha ISO
 * @returns {string} - Fecha formateada
 */
function formatDateTime(dateTimeString) {
    if (!dateTimeString) return '-';
    
    try {
        const date = new Date(dateTimeString);
        return date.toLocaleString('es-ES', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    } catch (error) {
        console.error('Error formatting date:', error);
        return dateTimeString;
    }
}

/**
 * Escapar HTML para prevenir XSS
 * @param {string} text - Texto a escapar
 * @returns {string} - Texto escapado
 */
function escapeHtml(text) {
    if (!text) return '';
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}