/**
 * API functions para action logs
 * Manejo de llamadas al backend para obtener logs de acciones de usuarios
 */

// Configuración base
const API_BASE = '/admin_panel/api/actionLog/paginated/';

/**
 * Obtener logs de acciones con paginación y filtros
 * @param {number} page - Número de página
 * @param {string} searchQuery - Búsqueda general (opcional)
 * @param {string} action - Filtro por acción específica (opcional)
 * @param {string} affectedType - Filtro por tipo afectado (opcional)
 * @param {string} email - Filtro por email específico (opcional)
 * @param {number} perPage - Registros por página
 * @returns {Promise} - Respuesta con logs paginados
 */
export async function fetchActionLogs(page = 1, searchQuery = '', action = '', affectedType = '', email = '', perPage = 10) {
    try {
        const params = new URLSearchParams({
            page: page.toString(),
            per_page: perPage.toString()
        });
        
        // Búsqueda general
        if (searchQuery && searchQuery.trim() !== '') {
            params.append('search', searchQuery.trim());
        }
        
        // Filtros específicos
        if (action && action.trim() !== '') {
            params.append('action', action.trim());
        }
        
        if (affectedType && affectedType.trim() !== '') {
            params.append('affected_type', affectedType.trim());
        }
        
        if (email && email.trim() !== '') {
            params.append('email', email.trim());
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