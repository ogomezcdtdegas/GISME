/**
 * ====================================================================
 * ARCHIVO: sweetalert2-usage-examples.js
 * DESCRIPCIÓN: Ejemplos de uso de las utilidades globales de SweetAlert2
 * CONTEXTO: Muestra cómo usar las funciones globales en vistas que heredan 
 *           de ComplementosPermissionMixin
 * ====================================================================
 */

// ====================================================================
// EJEMPLOS DE USO BÁSICO
// ====================================================================

// Ejemplo 1: Mostrar éxito
function ejemploExito() {
    showSuccessAlert('¡Configuración guardada exitosamente!');
}

// Ejemplo 2: Mostrar error general
function ejemploError() {
    showErrorAlert('No se pudieron cargar los datos del servidor');
}

// Ejemplo 3: Mostrar advertencia
function ejemploAdvertencia() {
    showWarningAlert('Esta acción no se puede deshacer');
}

// Ejemplo 4: Mostrar error de permisos (específico para ComplementosPermissionMixin)
function ejemploPermisos() {
    showPermissionDeniedAlert('No tiene permisos para esta acción. Contacte al administrador.');
}

// ====================================================================
// EJEMPLOS DE USO CON FETCH Y MANEJO DE RESPUESTAS
// ====================================================================

// Ejemplo 5: Usar handleFetchResponse para manejo automático de errores
async function ejemploConFetch() {
    try {
        const response = await fetch('/complementos/api/coeficientes/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({
                systemId: 'abc-123',
                mt: 1.0,
                bt: 0.0
            })
        });
        
        // Esta función maneja automáticamente errores de permisos, errores de servidor, etc.
        const data = await handleFetchResponse(response);
        
        if (data.success) {
            showSuccessAlert(data.message || 'Operación completada');
        }
    } catch (error) {
        // Los errores ya fueron manejados por handleFetchResponse
        console.error('Error en la operación:', error);
    }
}

// ====================================================================
// EJEMPLOS PARA VISTAS CON ComplementosPermissionMixin
// ====================================================================

// Ejemplo 6: Función típica para vistas de administración
async function actualizarConfiguracion(datos) {
    try {
        const response = await fetch('/complementos/api/configuracion/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify(datos)
        });
        
        // Si la respuesta es 403 (sin permisos), handleFetchResponse 
        // automáticamente mostrará showPermissionDeniedAlert()
        const data = await handleFetchResponse(response);
        
        if (data.success) {
            showSuccessAlert('Configuración actualizada correctamente');
            // Cerrar modal, actualizar tabla, etc.
        } else {
            showErrorAlert(data.error || 'Error al actualizar configuración');
        }
        
    } catch (error) {
        // Los errores de permisos ya fueron manejados automáticamente
        console.error('Error:', error);
    }
}

// Ejemplo 7: Validación con alertas antes de enviar datos
function validarYEnviar(formulario) {
    const datos = new FormData(formulario);
    
    // Validaciones
    if (!datos.get('nombre')) {
        showWarningAlert('El nombre es obligatorio');
        return;
    }
    
    if (!datos.get('email')) {
        showWarningAlert('El email es obligatorio'); 
        return;
    }
    
    // Si todo está bien, enviar
    enviarDatos(Object.fromEntries(datos));
}

// ====================================================================
// INTEGRACIÓN CON CÓDIGO LEGACY
// ====================================================================

// Ejemplo 8: Para mantener compatibilidad con código existente
// (como hicimos en coriolis_spa.html)
const mostrarExito = showSuccessAlert;
const mostrarError = showErrorAlert;
const mostrarErrorPermisos = showPermissionDeniedAlert;

// ====================================================================
// EJEMPLO COMPLETO: CRUD CON PERMISOS
// ====================================================================

class AdministradorSistemas {
    constructor() {
        this.apiBase = '/complementos/api/sistemas/';
    }
    
    async crear(sistema) {
        try {
            const response = await fetch(this.apiBase, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify(sistema)
            });
            
            const data = await handleFetchResponse(response);
            
            if (data.success) {
                showSuccessAlert('Sistema creado exitosamente');
                this.recargarTabla();
            }
        } catch (error) {
            console.error('Error al crear sistema:', error);
        }
    }
    
    async eliminar(sistemaId) {
        try {
            const response = await fetch(`${this.apiBase}${sistemaId}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': getCSRFToken()
                }
            });
            
            const data = await handleFetchResponse(response);
            
            if (data.success) {
                showSuccessAlert('Sistema eliminado exitosamente');
                this.recargarTabla();
            }
        } catch (error) {
            console.error('Error al eliminar sistema:', error);
        }
    }
    
    recargarTabla() {
        // Lógica para recargar la tabla
        console.log('Recargando tabla...');
    }
}

// ====================================================================
// FUNCIÓN UTILITARIA PARA CSRF TOKEN
// ====================================================================

function getCSRFToken() {
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
    
    return token || '';
}

// ====================================================================
// EXPORTAR PARA USO EN MÓDULOS (SI ES NECESARIO)
// ====================================================================

// Si este archivo se incluye como módulo ES6:
// export { ejemploExito, ejemploError, actualizarConfiguracion, AdministradorSistemas };