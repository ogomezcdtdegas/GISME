// ui.js - Utilidades para UI y manipulación del DOM
export const UI = {
    // Utilidades generales
    utils: {
        escapeHtml(unsafe) {
            if (!unsafe) return '';
            return unsafe
                .toString()
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        },

        formatDate(dateString) {
            if (!dateString) return '';
            const date = new Date(dateString);
            return date.toLocaleDateString('es-ES', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
            });
        }
    },

    // Toast notifications
    toast: {
        success(message) {
            // Por ahora usamos alert, pero aquí podrías integrar una librería de toasts
            alert("✅ " + message);
        },
        error(message) {
            alert("❌ " + message);
        },
        warning(message) {
            alert("⚠️ " + message);
        }
    },

    // Form utilities
    form: {
        getValue(elementId) {
            const element = document.getElementById(elementId);
            return element ? element.value : null;
        },

        setValue(elementId, value) {
            const element = document.getElementById(elementId);
            if (element) element.value = value;
        },

        reset(formId) {
            document.getElementById(formId)?.reset();
        },

        disable(elementId) {
            const element = document.getElementById(elementId);
            if (element) element.disabled = true;
        },

        enable(elementId) {
            const element = document.getElementById(elementId);
            if (element) element.disabled = false;
        }
    },

    // Select utilities
    select: {
        async populateSelect(selectId, options, selectedValue = null) {
            const select = document.getElementById(selectId);
            if (!select) return;

            select.innerHTML = '<option value="">Seleccione...</option>';
            
            options.forEach(option => {
                const optElement = document.createElement('option');
                optElement.value = option.id;
                optElement.textContent = option.name;
                if (selectedValue && option.id === selectedValue) {
                    optElement.selected = true;
                }
                select.appendChild(optElement);
            });
        }
    },

    // Alert notifications using SweetAlert2
    showAlert(message, type = 'info') {
        const config = {
            text: message,
            confirmButtonText: 'OK'
        };

        switch (type) {
            case 'success':
                config.icon = 'success';
                config.title = '¡Éxito!';
                break;
            case 'error':
                config.icon = 'error';
                config.title = 'Error';
                break;
            case 'warning':
                config.icon = 'warning';
                config.title = 'Advertencia';
                break;
            default:
                config.icon = 'info';
                config.title = 'Información';
        }

        // Verificar si SweetAlert2 está disponible
        if (typeof Swal !== 'undefined') {
            Swal.fire(config);
        } else {
            // Fallback a alert nativo
            alert(`${config.title}: ${message}`);
        }
    },

    // Loading state
    loading: {
        show(elementId) {
            const element = document.getElementById(elementId);
            if (element) {
                element.innerHTML = '<div class="text-center"><div class="spinner-border" role="status"><span class="visually-hidden">Cargando...</span></div></div>';
            }
        },
        hide(elementId) {
            const element = document.getElementById(elementId);
            if (element && element.querySelector('.spinner-border')) {
                element.innerHTML = '';
            }
        }
    }
};
