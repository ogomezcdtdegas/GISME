// ====================================================================
// SWEETALERT2-UTILS.JS - Utilidades globales para SweetAlert2
// ====================================================================

/**
 * Configuración global de SweetAlert2
 */
const SWEET_CONFIG = {
    // Configuración por defecto para todos los modales
    defaultConfig: {
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Aceptar',
        cancelButtonText: 'Cancelar',
        allowOutsideClick: false,
        allowEscapeKey: true,
        showClass: {
            popup: 'animate__animated animate__fadeInDown'
        },
        hideClass: {
            popup: 'animate__animated animate__fadeOutUp'
        }
    },
    
    // Configuraciones específicas por tipo
    success: {
        icon: 'success',
        confirmButtonColor: '#28a745',
        timer: 3000,
        timerProgressBar: true
    },
    
    error: {
        icon: 'error',
        confirmButtonColor: '#dc3545'
    },
    
    warning: {
        icon: 'warning',
        confirmButtonColor: '#ffc107',
        confirmButtonTextColor: '#000'
    },
    
    info: {
        icon: 'info',
        confirmButtonColor: '#17a2b8'
    },
    
    permission: {
        icon: 'warning',
        iconColor: '#dc3545',
        title: 'Sin Permisos',
        confirmButtonColor: '#dc3545',
        confirmButtonText: 'Entendido'
    }
};

/**
 * Mostrar modal de éxito
 * @param {string} title - Título del modal
 * @param {string} text - Texto del modal
 * @param {Object} options - Opciones adicionales
 */
function showSuccessAlert(title = 'Éxito', text = 'Operación realizada correctamente', options = {}) {
    const config = {
        ...SWEET_CONFIG.defaultConfig,
        ...SWEET_CONFIG.success,
        title,
        text,
        ...options
    };
    
    return Swal.fire(config);
}

/**
 * Mostrar modal de error
 * @param {string} title - Título del modal
 * @param {string} text - Texto del modal
 * @param {Object} options - Opciones adicionales
 */
function showErrorAlert(title = 'Error', text = 'Ha ocurrido un error', options = {}) {
    const config = {
        ...SWEET_CONFIG.defaultConfig,
        ...SWEET_CONFIG.error,
        title,
        text,
        ...options
    };
    
    return Swal.fire(config);
}

/**
 * Mostrar modal de advertencia
 * @param {string} title - Título del modal
 * @param {string} text - Texto del modal
 * @param {Object} options - Opciones adicionales
 */
function showWarningAlert(title = 'Advertencia', text = 'Atención requerida', options = {}) {
    const config = {
        ...SWEET_CONFIG.defaultConfig,
        ...SWEET_CONFIG.warning,
        title,
        text,
        ...options
    };
    
    return Swal.fire(config);
}

/**
 * Mostrar modal de información
 * @param {string} title - Título del modal
 * @param {string} text - Texto del modal
 * @param {Object} options - Opciones adicionales
 */
function showInfoAlert(title = 'Información', text = 'Información importante', options = {}) {
    const config = {
        ...SWEET_CONFIG.defaultConfig,
        ...SWEET_CONFIG.info,
        title,
        text,
        ...options
    };
    
    return Swal.fire(config);
}

/**
 * Mostrar modal de permisos denegados
 * @param {string} text - Texto específico del error de permisos
 * @param {Object} options - Opciones adicionales
 */
function showPermissionDeniedAlert(text = 'No tiene permisos para esta acción. Contacte al administrador.', options = {}) {
    const config = {
        ...SWEET_CONFIG.defaultConfig,
        ...SWEET_CONFIG.permission,
        text,
        ...options
    };
    
    return Swal.fire(config);
}

/**
 * Mostrar modal de confirmación
 * @param {string} title - Título del modal
 * @param {string} text - Texto del modal
 * @param {Object} options - Opciones adicionales
 */
function showConfirmAlert(title = 'Confirmar', text = '¿Está seguro?', options = {}) {
    const config = {
        ...SWEET_CONFIG.defaultConfig,
        title,
        text,
        icon: 'question',
        showCancelButton: true,
        ...options
    };
    
    return Swal.fire(config);
}

/**
 * Mostrar modal de carga/procesamiento
 * @param {string} title - Título del modal
 * @param {string} text - Texto del modal
 */
function showLoadingAlert(title = 'Procesando...', text = 'Por favor espere') {
    return Swal.fire({
        title,
        text,
        allowOutsideClick: false,
        allowEscapeKey: false,
        showConfirmButton: false,
        didOpen: () => {
            Swal.showLoading();
        }
    });
}

/**
 * Cerrar modal de carga
 */
function hideLoadingAlert() {
    Swal.close();
}

/**
 * Wrapper para manejar errores de respuesta de fetch con SweetAlert2
 * @param {Response} response - Respuesta de fetch
 * @param {string} defaultErrorMessage - Mensaje de error por defecto
 * @returns {Promise}
 */
async function handleFetchResponse(response, defaultErrorMessage = 'Error de conexión') {
    if (response.status === 403) {
        const data = await response.json();
        showPermissionDeniedAlert(data.error);
        throw new Error(data.error || 'Sin permisos');
    }
    
    if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        const errorMessage = data.error || data.message || defaultErrorMessage;
        showErrorAlert('Error', errorMessage);
        throw new Error(errorMessage);
    }
    
    return response.json();
}

// ====================================================================
// FUNCIONES DE COMPATIBILIDAD CON CÓDIGO EXISTENTE
// ====================================================================

/**
 * Reemplaza alert() nativo con SweetAlert2
 * Solo para casos donde no se puede modificar el código existente
 */
function sweetAlert(message, type = 'info') {
    switch(type.toLowerCase()) {
        case 'success':
            return showSuccessAlert('Éxito', message);
        case 'error':
            return showErrorAlert('Error', message);
        case 'warning':
            return showWarningAlert('Advertencia', message);
        case 'permission':
            return showPermissionDeniedAlert(message);
        default:
            return showInfoAlert('Información', message);
    }
}

// ====================================================================
// CONSOLE LOG PARA DEBUG
// ====================================================================
console.log('✅ SweetAlert2 Utils cargado globalmente');
console.log('📋 Funciones disponibles: showSuccessAlert, showErrorAlert, showWarningAlert, showInfoAlert, showPermissionDeniedAlert, showConfirmAlert, showLoadingAlert, hideLoadingAlert, handleFetchResponse');