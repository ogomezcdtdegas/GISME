/**
 * Event handlers para login logs
 * Manejo de eventos de la interfaz y coordinación de acciones
 */

import { fetchLoginLogs } from './api.js';
import { renderLoginLogs, renderPagination, updateRecordsInfo } from './ui.js';

// Estado global
let currentPage = 1;
let currentEmail = '';
let currentPerPage = 10;

/**
 * Cargar logs de login con parámetros actuales
 */
export async function loadLoginLogs(page = currentPage, email = currentEmail, perPage = currentPerPage) {
    try {
        // Mostrar loading
        showLoading();
        
        const data = await fetchLoginLogs(page, email, perPage);
        
        // Actualizar estado
        currentPage = page;
        currentEmail = email;
        currentPerPage = perPage;
        
        // Manejar respuesta: si es array directo o objeto paginado
        const logs = data.results || data || [];
        
        // Renderizar datos
        renderLoginLogs(logs);
        renderPagination(data);
        updateRecordsInfo(data);
        
    } catch (error) {
        console.error('Error loading login logs:', error);
        showError('Error al cargar los registros de login');
    }
}

/**
 * Ir a una página específica
 * @param {number} page - Número de página
 */
export function goToPage(page) {
    if (page !== currentPage) {
        loadLoginLogs(page, currentEmail, currentPerPage);
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
            loadLoginLogs(1, email, currentPerPage); // Resetear a página 1 al buscar
        }, 500); // Esperar 500ms después del último keystroke
    });
    
    // Botón limpiar búsqueda
    if (clearButton) {
        clearButton.addEventListener('click', function() {
            searchInput.value = '';
            loadLoginLogs(1, '', currentPerPage);
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
            loadLoginLogs(1, currentEmail, perPage); // Resetear a página 1 al cambiar tamaño
        });
    }
}

/**
 * Mostrar indicador de carga
 */
function showLoading() {
    const tbody = document.getElementById('loginLogsTableBody');
    if (tbody) {
        tbody.innerHTML = `
            <tr>
                <td colspan="3" class="text-center">
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
    const tbody = document.getElementById('loginLogsTableBody');
    if (tbody) {
        tbody.innerHTML = `
            <tr>
                <td colspan="3" class="text-center text-danger">
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
window.LoginLogEvents = {
    loadLoginLogs,
    goToPage,
    setupSearch,
    setupPagination
};