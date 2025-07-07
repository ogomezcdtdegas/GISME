// criticidad.js - Servicio para gestión de criticidades
import { BaseAPI } from '../base.js';
import { ENDPOINTS } from '../endpoints.js';

export const CriticidadService = {
    async listarTodo(page = 1, perPage = 10, ordering = 'name', search = '') {
        const params = { 
            page, 
            per_page: perPage,
            ordering: ordering
        };
        
        // Solo agregar el parámetro de búsqueda si no está vacío
        if (search && search.trim()) {
            params.search = search.trim();
        }
        
        return BaseAPI.get(ENDPOINTS.CRITICIDAD.LISTAR, params);
    },

    async listarTodosSinPaginacion(ordering = 'name') {
        return BaseAPI.get(ENDPOINTS.CRITICIDAD.LISTAR_TODOS, { ordering: ordering });
    },

    async listarPorTipo(tipoId) {
        try {
            const response = await BaseAPI.get(ENDPOINTS.CRITICIDAD.POR_TIPO(tipoId));
            
            if (response.success && response.data) {
                // Mantener el formato {id, name} que espera el frontend
                return response.data.map(item => ({
                    id: item.value,
                    name: item.label
                }));
            }
            
            // Si no hay datos o la respuesta no es exitosa, devolver array vacío
            return [];
        } catch (error) {
            console.error('Error al obtener criticidades por tipo:', error);
            // En caso de error (incluye 404), devolver array vacío
            return [];
        }
    },

    async obtenerPorId(id) {
        if (!id) return null;
        try {
            const response = await BaseAPI.get(ENDPOINTS.CRITICIDAD.POR_ID(id));
            return response;
        } catch (error) {
            console.error(`Error al obtener criticidad ${id}:`, error);
            return null;
        }
    },

    async crear(name) {
        return BaseAPI.post(ENDPOINTS.CRITICIDAD.CREAR, { name });
    },

    async actualizar(id, name) {
        return BaseAPI.put(ENDPOINTS.CRITICIDAD.ACTUALIZAR(id), { name });
    },

    async eliminar(id) {
        return BaseAPI.delete(ENDPOINTS.CRITICIDAD.ELIMINAR(id));
    }
};
