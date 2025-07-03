// productos.js - Servicio para gestión de productos
import { BaseAPI } from '../base.js';
import { ENDPOINTS } from '../endpoints.js';

export const ProductosService = {
    async listarTodo(page = 1, perPage, ordering = 'producto__name') {
        return BaseAPI.get(ENDPOINTS.PRODUCTOS.LISTAR, { 
            page, 
            per_page: perPage,
            ordering: ordering
        });
    },

    async crear(name, tipoCriticidadId, criticidadId) {
        return BaseAPI.post(ENDPOINTS.PRODUCTOS.CREAR, {
            name,
            tipo_criticidad_id: tipoCriticidadId,
            criticidad_id: criticidadId
        });
    },

    async actualizar(id, data) {
        return BaseAPI.put(ENDPOINTS.PRODUCTOS.ACTUALIZAR(id), data);
    },

    async obtenerPorId(id) {
        return BaseAPI.get(ENDPOINTS.PRODUCTOS.POR_ID(id));
    }
};
