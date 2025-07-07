// tipoEquipo.js - Servicio para gestión de tipos de equipo
import { BaseAPI } from '../base.js';
import { ENDPOINTS } from '../endpoints.js';

export const TipoEquipoService = {
    async listar(page = 1, perPage = 10, search = '') {
        const params = { 
            page, 
            per_page: perPage,
            ordering: 'tipo_equipo__name'  // Ordenamiento alfabético por tipo de equipo
        };
        
        // Solo agregar el parámetro de búsqueda si no está vacío
        if (search && search.trim()) {
            params.search = search.trim();
        }
        
        return BaseAPI.get(ENDPOINTS.TIPO_EQUIPO.LISTAR, params);
    },

    async crear(data) {
        return BaseAPI.post(ENDPOINTS.TIPO_EQUIPO.CREAR, data);
    },

    async actualizar(id, data) {
        return BaseAPI.put(ENDPOINTS.TIPO_EQUIPO.ACTUALIZAR(id), data);
    },

    async eliminarTipo(id) {
        return BaseAPI.delete(ENDPOINTS.TIPO_EQUIPO.ELIMINAR(id));
    },

    async eliminarRelacion(id) {
        return BaseAPI.delete(ENDPOINTS.TIPO_EQUIPO.ELIMINAR_RELACION(id));
    }
};
