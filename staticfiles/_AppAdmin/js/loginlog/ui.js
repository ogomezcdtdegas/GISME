/**
 * UI functions para login logs
 * Renderizado de tabla, paginación y elementos de interfaz
 */

/**
 * Renderizar logs de login en la tabla
 * @param {Array} logs - Array de logs de login
 */
export function renderLoginLogs(logs) {
    const tbody = document.getElementById('loginLogsTableBody');
    if (!tbody) {
        console.error('❌ No se encontró el elemento loginLogsTableBody');
        return;
    }

    if (!logs || logs.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="3" class="text-center">
                    <i class="bi bi-info-circle"></i>
                    No hay registros de login disponibles
                </td>
            </tr>`;
        return;
    }

    tbody.innerHTML = logs.map(log => `
        <tr>
            <td>
                <strong>${escapeHtml(log.email)}</strong>
            </td>
            <td>
                ${formatDateTime(log.login_datetime)}
            </td>
            <td>
                <span class="badge bg-secondary">${escapeHtml(log.ip_address)}</span>
            </td>
        </tr>
    `).join('');
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
            window.LoginLogEvents.goToPage(parseInt(page));
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