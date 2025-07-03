// tipoCriticidad.js - Servicio para gestión de tipos de criticidad
import { BaseAPI } from '../base.js';
import { ENDPOINTS } from '../endpoints.js';
import { CriticidadService } from './criticidad.js';

export const TipoCriticidadService = {
    async listarTodo(page = 1, perPage) {
        try {
            const response = await BaseAPI.get(ENDPOINTS.TIPO_CRITICIDAD.LISTAR, { page, per_page: perPage });
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
    }
};
