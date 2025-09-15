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

    paginationContainer.innerHTML = '';

    // Si es un array simple o no hay datos de paginación, no mostrar controles
    if (Array.isArray(paginationData) || !paginationData || !paginationData.count) {
        return;
    }

    const count = paginationData.count || 0;
    const pageSize = paginationData.page_size || 10;
    const currentPage = paginationData.current_page || 1;
    const totalPages = Math.ceil(count / pageSize);
    
    // No mostrar paginación si solo hay una página
    if (totalPages <= 1) {
        return;
    }

    const hasPrevious = paginationData.previous !== null;
    const hasNext = paginationData.next !== null;

    // Botón Previous
    const prevLi = document.createElement('li');
    prevLi.className = `page-item ${!hasPrevious ? 'disabled' : ''}`;
    if (hasPrevious) {
        prevLi.innerHTML = `<a class="page-link" href="#" data-page="${currentPage - 1}">Anterior</a>`;
    } else {
        prevLi.innerHTML = `<span class="page-link">Anterior</span>`;
    }
    paginationContainer.appendChild(prevLi);

    // Información de página actual
    const currentLi = document.createElement('li');
    currentLi.className = 'page-item disabled';
    currentLi.innerHTML = `<span class="page-link">Página ${currentPage} de ${totalPages}</span>`;
    paginationContainer.appendChild(currentLi);

    // Botón Next
    const nextLi = document.createElement('li');
    nextLi.className = `page-item ${!hasNext ? 'disabled' : ''}`;
    if (hasNext) {
        nextLi.innerHTML = `<a class="page-link" href="#" data-page="${currentPage + 1}">Siguiente</a>`;
    } else {
        nextLi.innerHTML = `<span class="page-link">Siguiente</span>`;
    }
    paginationContainer.appendChild(nextLi);

    // Agregar event listeners a los enlaces de paginación
    paginationContainer.addEventListener('click', function(e) {
        e.preventDefault();
        const page = e.target.dataset.page;
        if (page && !e.target.closest('.disabled')) {
            window.ActionLogEvents.goToPage(parseInt(page));
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

    // Si es objeto de paginación
    if (paginationData && typeof paginationData === 'object') {
        const count = paginationData.count || 0;
        const pageSize = paginationData.page_size || 10;
        const currentPage = paginationData.current_page || 1;
        
        if (count > 0) {
            const start = ((currentPage - 1) * pageSize) + 1;
            const end = Math.min(currentPage * pageSize, count);
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