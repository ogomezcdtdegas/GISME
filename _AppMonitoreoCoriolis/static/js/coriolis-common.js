/**
 * JavaScript básico para templates de Coriolis
 * Funcionalidades comunes y utilidades
 */

// Namespace para funciones comunes
window.CoriolisCommon = {
    init() {
        console.log('Coriolis Common iniciado');
        this.initBootstrapComponents();
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
    },

    // Función utilitaria para obtener CSRF token (versión robusta)
    getCSRFToken() {
        // Primero intentar obtener del input hidden
        let token = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        
        // Si no se encuentra, intentar obtener de las cookies
        if (!token) {
            const name = 'csrftoken';
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            token = cookieValue;
        }
        
        // Validar que el token tenga el formato correcto (debería tener 64 caracteres)
        if (token && token.length !== 64) {
            console.warn('⚠️ Token CSRF con longitud incorrecta:', token.length, 'caracteres. Esperados: 64');
        }
        
        console.log('🔐 Token CSRF obtenido:', token ? `✅ Válido (${token.length} chars)` : '❌ No encontrado');
        return token || '';
    },

    // Función para mostrar notificaciones
    showNotification(message, type = 'info') {
        const toastContainer = this.getOrCreateToastContainer();
        
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="bi bi-info-circle"></i> ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        toastContainer.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Remover después de que se oculte
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    },

    getOrCreateToastContainer() {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            container.style.zIndex = '9999';
            document.body.appendChild(container);
        }
        return container;
    },

    // Función para formatear números
    formatNumber(num, decimals = 2) {
        return parseFloat(num).toFixed(decimals);
    },

    // Función para formatear fecha
    formatDateTime(date = new Date()) {
        return date.toLocaleString('es-ES', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    },

    // Función para validar campos de entrada
    validateInput(input, rules = {}) {
        const value = input.value.trim();
        let isValid = true;
        let message = '';

        if (rules.required && !value) {
            isValid = false;
            message = 'Este campo es obligatorio';
        } else if (rules.minLength && value.length < rules.minLength) {
            isValid = false;
            message = `Mínimo ${rules.minLength} caracteres`;
        } else if (rules.maxLength && value.length > rules.maxLength) {
            isValid = false;
            message = `Máximo ${rules.maxLength} caracteres`;
        } else if (rules.pattern && !rules.pattern.test(value)) {
            isValid = false;
            message = rules.message || 'Formato inválido';
        }

        // Aplicar clases de Bootstrap
        input.classList.remove('is-valid', 'is-invalid');
        input.classList.add(isValid ? 'is-valid' : 'is-invalid');

        // Mostrar mensaje de error
        const feedback = input.parentNode.querySelector('.invalid-feedback');
        if (feedback) {
            feedback.textContent = message;
        }

        return isValid;
    },

    // Función para hacer requests AJAX
    async makeRequest(url, options = {}) {
        const defaultOptions = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            },
            credentials: 'same-origin'
        };

        const finalOptions = { ...defaultOptions, ...options };

        try {
            const response = await fetch(url, finalOptions);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error en request:', error);
            this.showNotification('Error en la comunicación con el servidor', 'danger');
            throw error;
        }
    },

    // Función para debounce (útil para búsquedas)
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Función para auto-refresh
    setupAutoRefresh(callback, interval = 30000) {
        if (typeof callback !== 'function') {
            console.error('Callback debe ser una función');
            return;
        }

        const refreshId = setInterval(callback, interval);
        
        // Detener refresh al cambiar de página
        window.addEventListener('beforeunload', () => {
            clearInterval(refreshId);
        });

        return refreshId;
    },

    // Función para mostrar/ocultar elementos con animación
    toggleElement(element, show = null) {
        if (!element) return;

        const isVisible = !element.classList.contains('d-none');
        const shouldShow = show !== null ? show : !isVisible;

        if (shouldShow) {
            element.classList.remove('d-none');
            element.style.opacity = '0';
            element.style.transform = 'translateY(-10px)';
            
            setTimeout(() => {
                element.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
                element.style.opacity = '1';
                element.style.transform = 'translateY(0)';
            }, 10);
        } else {
            element.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
            element.style.opacity = '0';
            element.style.transform = 'translateY(-10px)';
            
            setTimeout(() => {
                element.classList.add('d-none');
                element.style.transition = '';
            }, 300);
        }
    },

    // Función para copiar al portapapeles
    async copyToClipboard(text) {
        try {
            if (navigator.clipboard && window.isSecureContext) {
                await navigator.clipboard.writeText(text);
            } else {
                // Fallback para navegadores sin soporte
                const textArea = document.createElement('textarea');
                textArea.value = text;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
            }
            
            this.showNotification('Copiado al portapapeles', 'success');
            return true;
        } catch (error) {
            console.error('Error al copiar:', error);
            this.showNotification('Error al copiar al portapapeles', 'danger');
            return false;
        }
    }
};

// Inicializar automáticamente solo si no estamos en SPA
document.addEventListener('DOMContentLoaded', function() {
    // Verificar si estamos en una página SPA
    const isSPA = document.getElementById('sistema-selector-view') !== null;
    
    if (!isSPA) {
        CoriolisCommon.init();
    }
});
