/**
 * API functions para login logs
 * Manejo de llamadas al backend para obtener logs de login
 */

// Configuración base
const API_BASE = '/admin_panel/api/loginLog/paginated/';

/**
 * Obtener logs de login con paginación y filtro por email
 * @param {number} page - Número de página
 * @param {string} email - Filtro por email (opcional)
 * @param {number} perPage - Registros por página
 * @returns {Promise} - Respuesta con logs paginados
 */
export async function fetchLoginLogs(page = 1, email = '', perPage = 10) {
    try {
        const params = new URLSearchParams({
            page: page.toString(),
            page_size: perPage.toString()
        });
        
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
        console.error('Error fetching login logs:', error);
        throw error;
    }
}