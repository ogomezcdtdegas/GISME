// sistemas.js - Servicio para gestión de sistemas
import { BaseAPI } from '../base.js';
import { ENDPOINTS } from '../endpoints.js';

export const SistemaAPI = {
    // Método list para compatibilidad con sistema.js
    async list(params = {}) {
        const page = params.page || 1;
        const pageSize = params.page_size || 10;
        const ordering = params.ordering || 'tag';
        const search = params.search || '';
        
        const queryParams = { 
            page, 
            per_page: pageSize,
            ordering: ordering
        };
        
        // Solo agregar el parámetro de búsqueda si no está vacío
        if (search && search.trim()) {
            queryParams.search = search.trim();
        }
        
        return BaseAPI.get(ENDPOINTS.SISTEMA.LISTAR, queryParams);
    },

    // Método create para compatibilidad
    async create(data) {
        return BaseAPI.post(ENDPOINTS.SISTEMA.CREAR, data);
    },

    // Método update para compatibilidad
    async update(id, data) {
        return BaseAPI.put(ENDPOINTS.SISTEMA.ACTUALIZAR(id), data);
    },

    // Método delete para compatibilidad
    async delete(id) {
        return BaseAPI.delete(ENDPOINTS.SISTEMA.ELIMINAR(id));
    },

    // Método retrieve para compatibilidad
    async retrieve(id) {
        return BaseAPI.get(ENDPOINTS.SISTEMA.POR_ID(id));
    },

    async listarTodo(page = 1, perPage = 10, ordering = 'tag', search = '') {
        const queryParams = { 
            page, 
            per_page: perPage,
            ordering: ordering
        };
        
        if (search && search.trim()) {
            queryParams.search = search.trim();
        }
        
        return BaseAPI.get(ENDPOINTS.SISTEMA.LISTAR, queryParams);
    },

    async listarTodosSinPaginacion(ordering = 'tag') {
        return BaseAPI.get(ENDPOINTS.SISTEMA.LISTAR_TODOS, { ordering: ordering });
    },

    async obtenerPorId(id) {
        if (!id) return null;
        try {
            const response = await BaseAPI.get(ENDPOINTS.SISTEMA.POR_ID(id));
            return response;
        } catch (error) {
            console.error('Error al obtener sistema:', error);
            return null;
        }
    },

    async crear(data) {
        return BaseAPI.post(ENDPOINTS.SISTEMA.CREAR, data);
    },

    async actualizar(id, data) {
        return BaseAPI.put(ENDPOINTS.SISTEMA.ACTUALIZAR(id), data);
    },

    async eliminar(id) {
        return BaseAPI.delete(ENDPOINTS.SISTEMA.ELIMINAR(id));
    },

    async validarDuplicado(tag, sistemaId, ubicacionId, excludeId = null) {
        try {
            // Esta validación se hace en el backend a través del serializer
            // pero podemos implementar una pre-validación aquí si es necesario
            return { isValid: true };
        } catch (error) {
            console.error('Error validando duplicado:', error);
            return { isValid: false, error: error.message };
        }
    }
};
