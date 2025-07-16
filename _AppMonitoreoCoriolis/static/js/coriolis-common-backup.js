/**
 * JavaScript básico para templates de Coriolis
 * Funcionalidades comunes y utilidades
 */

// Namespace para funciones comunes
window.CoriolisCommon = {
    init() {
        console.log('Coriolis Common iniciado');
        
        // Solo inicializar si no estamos en SPA
        if (!window.CoriolisSPA) {
            this.initBootstrapComponents();
        }
    },

    initBootstrapComponents() {
        // Inicializar tooltips de Bootstrap si existen
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
        
        // Inicializar popovers de Bootstrap si existen
        const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        const popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    },ásico para templates de Coriolis
 * Funcionalidades comunes y utilidades
 */

// Inicialización básica
document.addEventListener('DOMContentLoaded', function() {
    console.log('Página de Monitoreo Coriolis cargada');
    
    // Inicializar tooltips de Bootstrap si existen
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Inicializar popovers de Bootstrap si existen
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    const popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Funcionalidad de auto-refresh para métricas en tiempo real
    initAutoRefresh();
});

/**
 * Inicializar auto-refresh para páginas con métricas
 */
function initAutoRefresh() {
    const refreshElements = document.querySelectorAll('[data-auto-refresh]');
    
    refreshElements.forEach(element => {
        const interval = parseInt(element.dataset.autoRefresh) || 5000; // 5 segundos por defecto
        
        setInterval(() => {
            // Simular actualización de métricas
            updateRandomMetrics(element);
        }, interval);
    });
}

/**
 * Actualizar métricas con valores simulados
 * @param {HTMLElement} container - Contenedor de métricas
 */
function updateRandomMetrics(container) {
    const metricElements = container.querySelectorAll('[data-metric]');
    
    metricElements.forEach(element => {
        const metricType = element.dataset.metric;
        let newValue;
        
        switch (metricType) {
            case 'pressure':
                newValue = (Math.random() * 50 + 100).toFixed(1);
                break;
            case 'flow':
                newValue = (Math.random() * 30 + 70).toFixed(1);
                break;
            case 'temperature':
                newValue = (Math.random() * 15 + 20).toFixed(1);
                break;
            case 'density':
                newValue = (Math.random() * 0.2 + 0.7).toFixed(3);
                break;
            default:
                newValue = (Math.random() * 100).toFixed(1);
        }
        
        // Actualizar el valor con animación
        animateValueChange(element, newValue);
    });
}

/**
 * Animar cambio de valor en un elemento
 * @param {HTMLElement} element - Elemento a animar
 * @param {string} newValue - Nuevo valor
 */
function animateValueChange(element, newValue) {
    element.style.transition = 'color 0.3s ease';
    element.style.color = '#007bff';
    element.textContent = newValue;
    
    setTimeout(() => {
        element.style.color = '';
    }, 300);
}

/**
 * Mostrar notificación toast
 * @param {string} message - Mensaje a mostrar
 * @param {string} type - Tipo: success, error, warning, info
 */
function showToast(message, type = 'info') {
    // Crear toast si no existe el contenedor
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '9999';
        document.body.appendChild(toastContainer);
    }
    
    // Crear toast
    const toastId = 'toast-' + Date.now();
    const toastHtml = `
        <div id="${toastId}" class="toast align-items-center text-white bg-${getBootstrapColor(type)} border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    
    // Mostrar toast
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement);
    toast.show();
    
    // Limpiar después de que se oculte
    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}

/**
 * Convertir tipo de mensaje a color de Bootstrap
 * @param {string} type - Tipo de mensaje
 * @returns {string} - Clase de color de Bootstrap
 */
function getBootstrapColor(type) {
    const colors = {
        'success': 'success',
        'error': 'danger',
        'warning': 'warning',
        'info': 'info'
    };
    return colors[type] || 'info';
}

/**
 * Formatear número con separadores de miles
 * @param {number} num - Número a formatear
 * @returns {string} - Número formateado
 */
function formatNumber(num) {
    return new Intl.NumberFormat('es-CO').format(num);
}

/**
 * Formatear fecha en español
 * @param {Date} date - Fecha a formatear
 * @returns {string} - Fecha formateada
 */
function formatDate(date) {
    return new Intl.DateTimeFormat('es-CO', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    }).format(date);
}

/**
 * Validar si un elemento está visible en el viewport
 * @param {HTMLElement} element - Elemento a verificar
 * @returns {boolean} - Si el elemento está visible
 */
function isElementInViewport(element) {
    const rect = element.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

// Exportar funciones para uso global
window.CoriolisUtils = {
    showToast,
    formatNumber,
    formatDate,
    isElementInViewport,
    animateValueChange
};
