// ubicaciones.js - Servicio para gestión de ubicaciones
import { BaseAPI } from '../base.js';
import { ENDPOINTS } from '../endpoints.js';

export const UbicacionAPI = {
    // Método list para compatibilidad con ubicacion.js
    async list(params = {}) {
        const page = params.page || 1;
        const pageSize = params.page_size || 10;
        const ordering = params.ordering || 'nombre';
        const search = params.search || '';
        
        // Usar el endpoint paginado en lugar del listado completo
        const queryParams = { 
            page, 
            per_page: pageSize,
            ordering: ordering
        };
        
        // Solo agregar el parámetro de búsqueda si no está vacío
        if (search && search.trim()) {
            queryParams.search = search.trim();
        }
        
        return BaseAPI.get(ENDPOINTS.UBICACION.LISTAR, queryParams);
    },

    // Método create para compatibilidad
    async create(data) {
        return BaseAPI.post(ENDPOINTS.UBICACION.CREAR, data);
    },

    // Método update para compatibilidad
    async update(id, data) {
        return this.actualizar(id, data);
    },

    // Método delete para compatibilidad
    async delete(id) {
        return this.eliminar(id);
    },

    // Método retrieve para compatibilidad
    async retrieve(id) {
        return this.obtenerPorId(id);
    },

    async listarTodo(page = 1, perPage = 10, ordering = 'nombre', search = '') {
        const params = { 
            page, 
            per_page: perPage,
            ordering: ordering
        };
        
        // Solo agregar el parámetro de búsqueda si no está vacío
        if (search && search.trim()) {
            params.search = search.trim();
        }
        
        return BaseAPI.get(ENDPOINTS.UBICACION.LISTAR, params);
    },

    async listarTodosSinPaginacion(ordering = 'nombre') {
        return BaseAPI.get(ENDPOINTS.UBICACION.LISTAR_TODOS, { ordering: ordering });
    },

    async obtenerPorId(id) {
        if (!id) return null;
        try {
            const response = await BaseAPI.get(ENDPOINTS.UBICACION.POR_ID(id));
            return response;
        } catch (error) {
            //console.error('Error al obtener ubicación:', error);
            return null;
        }
    },

    async crear(data) {
        return BaseAPI.post(ENDPOINTS.UBICACION.CREAR, data);
    },

    async actualizar(id, data) {
        return BaseAPI.put(ENDPOINTS.UBICACION.ACTUALIZAR(id), data);
    },

    async eliminar(id) {
        return BaseAPI.delete(ENDPOINTS.UBICACION.ELIMINAR(id));
    },

    async validarCoordenadas(latitud, longitud) {
        // Validaciones locales
        const lat = parseFloat(latitud);
        const lng = parseFloat(longitud);
        
        if (isNaN(lat) || isNaN(lng)) {
            return { valid: false, message: 'Las coordenadas deben ser números válidos' };
        }
        
        if (lat < -90 || lat > 90) {
            return { valid: false, message: 'La latitud debe estar entre -90 y 90 grados' };
        }
        
        if (lng < -180 || lng > 180) {
            return { valid: false, message: 'La longitud debe estar entre -180 y 180 grados' };
        }
        
        return { valid: true };
    },

    // Utilidad para formatear coordenadas
    formatearCoordenadas(latitud, longitud, decimales = 6) {
        const lat = parseFloat(latitud).toFixed(decimales);
        const lng = parseFloat(longitud).toFixed(decimales);
        return { latitud: lat, longitud: lng };
    },

    // Calcular distancia entre dos puntos (fórmula Haversine)
    calcularDistancia(lat1, lng1, lat2, lng2) {
        const R = 6371; // Radio de la Tierra en km
        const dLat = (lat2 - lat1) * Math.PI / 180;
        const dLng = (lng2 - lng1) * Math.PI / 180;
        
        const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
                Math.sin(dLng/2) * Math.sin(dLng/2);
                
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        const distancia = R * c;
        
        return distancia; // Distancia en kilómetros
    }
};
