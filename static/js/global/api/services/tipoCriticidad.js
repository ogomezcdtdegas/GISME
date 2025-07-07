// tipoCriticidad.js - Servicio para gestión de tipos de criticidad
import { BaseAPI } from '../base.js';
import { ENDPOINTS } from '../endpoints.js';
import { CriticidadService } from './criticidad.js';

export const TipoCriticidadService = {
    async listarTodo(page = 1, perPage, ordering = 'tipo_criticidad__name', search = '') {
        try {
            const params = { 
                page, 
                per_page: perPage,
                ordering: ordering
            };
            
            // Solo agregar el parámetro de búsqueda si no está vacío
            if (search && search.trim()) {
                params.search = search.trim();
            }
            
            const response = await BaseAPI.get(ENDPOINTS.TIPO_CRITICIDAD.LISTAR, params);
            return response;
        } catch (error) {
            console.error('Error en listarTodo:', error);
            throw error;
        }
    },

    async listarUnicos() {
        try {
            const response = await BaseAPI.get(ENDPOINTS.TIPO_CRITICIDAD.UNICOS);
            return response;
        } catch (error) {
            console.error('Error en listarUnicos:', error);
            throw error;
        }
    },

    async crear(name, criticidadId) {
        return BaseAPI.post(ENDPOINTS.TIPO_CRITICIDAD.CREAR, {
            name,
            criticidad_id: criticidadId
        });
    },

    async actualizar(id, data) {
        return BaseAPI.put(ENDPOINTS.TIPO_CRITICIDAD.ACTUALIZAR(id), data);
    },

    async eliminarTipo(id) {
        return BaseAPI.delete(ENDPOINTS.TIPO_CRITICIDAD.ELIMINAR(id));
    },

    async eliminarRelacion(id) {
        return BaseAPI.delete(ENDPOINTS.TIPO_CRITICIDAD.ELIMINAR_RELACION(id));
    }
};
