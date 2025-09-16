/**
 * API functions para action logs
 * Manejo de llamadas al backend para obtener logs de acciones de usuarios
 */

// Configuración base
const API_BASE = '/admin_panel/api/actionLog/paginated/';

/**
 * Obtener logs de acciones con paginación y filtros
 * @param {number} page - Número de página
 * @param {string} email - Filtro por email (opcional)
 * @param {string} action - Filtro por acción (opcional)
 * @param {string} affectedType - Filtro por tipo afectado (opcional)
 * @param {string} affectedValue - Filtro por valor afectado (opcional)
 * @param {number} perPage - Registros por página
 * @returns {Promise} - Respuesta con logs paginados
 */
export async function fetchActionLogs(page = 1, email = '', action = '', affectedType = '', affectedValue = '', perPage = 10) {
    try {
        const params = new URLSearchParams({
            page: page.toString(),
            page_size: perPage.toString()
        });
        
        if (email && email.trim() !== '') {
            params.append('email', email.trim());
        }
        
        if (action && action.trim() !== '') {
            params.append('action', action.trim());
        }
        
        if (affectedType && affectedType.trim() !== '') {
            params.append('affected_type', affectedType.trim());
        }
        
        if (affectedValue && affectedValue.trim() !== '') {
            params.append('affected_value', affectedValue.trim());
        }
        
        const response = await fetch(`${API_BASE}?${params}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error fetching action logs:', error);
        throw error;
    }
}