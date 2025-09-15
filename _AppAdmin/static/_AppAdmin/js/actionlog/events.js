/**
 * Event handlers para action logs
 * Manejo de eventos de la interfaz y coordinación de acciones
 */

import { fetchActionLogs } from './api.js';
import { renderActionLogs, renderPagination, updateRecordsInfo } from './ui.js';

// Estado global
let currentPage = 1;
let currentEmail = '';
let currentAction = '';
let currentAffectedType = '';
let currentAffectedValue = '';
let currentPerPage = 10;

/**
 * Cargar logs de acciones con parámetros actuales
 */
export async function loadActionLogs(page = currentPage, email = currentEmail, action = currentAction, 
                                   affectedType = currentAffectedType, affectedValue = currentAffectedValue, 
                                   perPage = currentPerPage) {
    try {
        // Mostrar loading
        showLoading();
        
        const data = await fetchActionLogs(page, email, action, affectedType, affectedValue, perPage);
        
        // Actualizar estado
        currentPage = page;
        currentEmail = email;
        currentAction = action;
        currentAffectedType = affectedType;
        currentAffectedValue = affectedValue;
        currentPerPage = perPage;
        
        // Manejar respuesta: si es array directo o objeto paginado
        const logs = data.results || data || [];
        
        // Renderizar datos
        renderActionLogs(logs);
        renderPagination(data);
        updateRecordsInfo(data);
        
    } catch (error) {
        console.error('Error loading action logs:', error);
        showError('Error al cargar los registros de acciones');
    }
}

/**
 * Ir a una página específica
 * @param {number} page - Número de página
 */
export function goToPage(page) {
    if (page !== currentPage) {
        loadActionLogs(page, currentEmail, currentAction, currentAffectedType, currentAffectedValue, currentPerPage);
    }
}

/**
 * Configurar búsqueda por email
 */
export function setupSearch() {
    const searchInput = document.getElementById('searchInput');
    const clearButton = document.getElementById('clearSearch');
    
    if (!searchInput) return;

    let searchTimeout;
    
    // Búsqueda con debounce
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            const email = searchInput.value.trim();
            loadActionLogs(1, email, currentAction, currentAffectedType, currentAffectedValue, currentPerPage);
        }, 500); // Esperar 500ms después del último keystroke
    });
    
    // Botón limpiar búsqueda
    if (clearButton) {
        clearButton.addEventListener('click', function() {
            searchInput.value = '';
            loadActionLogs(1, '', currentAction, currentAffectedType, currentAffectedValue, currentPerPage);
        });
    }
}

/**
 * Configurar filtros adicionales
 */
export function setupFilters() {
    const actionFilter = document.getElementById('actionFilter');
    const typeFilter = document.getElementById('typeFilter');
    const clearFilters = document.getElementById('clearFilters');
    
    // Filtro por acción
    if (actionFilter) {
        actionFilter.addEventListener('change', function() {
            const action = actionFilter.value;
            loadActionLogs(1, currentEmail, action, currentAffectedType, currentAffectedValue, currentPerPage);
        });
    }
    
    // Filtro por tipo
    if (typeFilter) {
        typeFilter.addEventListener('change', function() {
            const type = typeFilter.value;
            loadActionLogs(1, currentEmail, currentAction, type, currentAffectedValue, currentPerPage);
        });
    }
    
    // Limpiar todos los filtros
    if (clearFilters) {
        clearFilters.addEventListener('click', function() {
            // Resetear todos los campos
            document.getElementById('searchInput').value = '';
            if (actionFilter) actionFilter.value = '';
            if (typeFilter) typeFilter.value = '';
            
            // Cargar datos sin filtros
            loadActionLogs(1, '', '', '', '', currentPerPage);
        });
    }
}

/**
 * Configurar selector de registros por página
 */
export function setupPagination() {
    const recordsSelect = document.getElementById('recordsPerPage');
    
    if (recordsSelect) {
        recordsSelect.addEventListener('change', function() {
            const perPage = parseInt(recordsSelect.value) || 10;
            loadActionLogs(1, currentEmail, currentAction, currentAffectedType, currentAffectedValue, perPage);
        });
    }
}

/**
 * Mostrar indicador de carga
 */
function showLoading() {
    const tbody = document.getElementById('actionLogsTableBody');
    if (tbody) {
        tbody.innerHTML = `
            <tr>
                <td colspan="4" class="text-center">
                    <div class="spinner-border spinner-border-sm" role="status">
                        <span class="visually-hidden">Cargando...</span>
                    </div>
                    Cargando registros...
                </td>
            </tr>`;
    }
}

/**
 * Mostrar mensaje de error
 * @param {string} message - Mensaje de error
 */
function showError(message) {
    const tbody = document.getElementById('actionLogsTableBody');
    if (tbody) {
        tbody.innerHTML = `
            <tr>
                <td colspan="4" class="text-center text-danger">
                    <i class="bi bi-exclamation-triangle"></i>
                    ${message}
                </td>
            </tr>`;
    }
    
    // También mostrar con SweetAlert2 si está disponible
    if (typeof Swal !== 'undefined') {
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: message,
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 3000
        });
    }
}

// Exportar funciones para uso global
window.ActionLogEvents = {
    loadActionLogs,
    goToPage,
    setupSearch,
    setupFilters,
    setupPagination
};