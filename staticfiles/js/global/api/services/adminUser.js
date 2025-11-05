// adminUser.js - Servicio para gestión de usuarios admin
import { BaseAPI } from '../base.js';
import { ENDPOINTS } from '../endpoints.js';

export const AdminUserService = {
    async listarPaginado(page = 1, perPage = 10, ordering = '-date_joined', search = '') {
        const params = { 
            page, 
            per_page: perPage,
            ordering: ordering
        };
        
        // Solo agregar el parámetro de búsqueda si no está vacío
        if (search && search.trim()) {
            params.search = search.trim();
        }
        
        //console.log('🎯 AdminUserService llamando BaseAPI.get con:', ENDPOINTS.ADMIN_USERS.LISTAR, params);
        const result = await BaseAPI.get(ENDPOINTS.ADMIN_USERS.LISTAR, params);
        //console.log('🔍 BaseAPI.get retornó:', result);
        return result;
    },

    async obtenerRoles() {
        return BaseAPI.get(ENDPOINTS.ADMIN_USERS.ROLES);
    },

    async obtenerPorId(id) {
        if (!id) return null;
        try {
            const response = await BaseAPI.get(ENDPOINTS.ADMIN_USERS.POR_ID(id));
            return response;
        } catch (error) {
            //console.error('Error al obtener usuario:', error);
            return null;
        }
    },

    async crear(userData) {
        try {
            return await BaseAPI.post(ENDPOINTS.ADMIN_USERS.CREAR, userData);
        } catch (error) {
            //console.error('Error al crear usuario:', error);
            return { success: false, error: error.message };
        }
    },

    async actualizar(id, userData) {
        try {
            return await BaseAPI.put(ENDPOINTS.ADMIN_USERS.ACTUALIZAR(id), userData);
        } catch (error) {
            //console.error('Error al actualizar usuario:', error);
            return { success: false, error: error.message };
        }
    },

    async eliminar(id) {
        try {
            return await BaseAPI.delete(ENDPOINTS.ADMIN_USERS.ELIMINAR(id));
        } catch (error) {
            //console.error('Error al eliminar usuario:', error);
            return { success: false, error: error.message };
        }
    }
};
