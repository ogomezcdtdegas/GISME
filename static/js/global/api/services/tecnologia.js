// tecnologia.js - Servicio para gestión de tecnologías
import { BaseAPI } from '../base.js';
import { ENDPOINTS } from '../endpoints.js';

export const TecnologiaService = {
    async getAll(page = 1, perPage = 10, search = '') {
        const params = { 
            page, 
            per_page: perPage,
            ordering: 'tecnologia__name'  // Ordenamiento alfabético por tecnología
        };
        
        // Solo agregar el parámetro de búsqueda si no está vacío
        if (search && search.trim()) {
            params.search = search.trim();
        }
        
        return BaseAPI.get(ENDPOINTS.TECNOLOGIA.LISTAR, params);
    },

    async getById(id) {
        return BaseAPI.get(ENDPOINTS.TECNOLOGIA.ACTUALIZAR(id));
    },

    async create(data) {
        return BaseAPI.post(ENDPOINTS.TECNOLOGIA.CREAR, data);
    },

    async update(id, data) {
        return BaseAPI.put(ENDPOINTS.TECNOLOGIA.ACTUALIZAR(id), data);
    },

    async delete(id) {
        return BaseAPI.delete(ENDPOINTS.TECNOLOGIA.ELIMINAR(id));
    },

    // Métodos para dropdowns encadenados
    async getTiposEquipoUnicos() {
        // Usar el endpoint de tipo equipo con parámetro para obtener todos los registros
        const response = await BaseAPI.get(ENDPOINTS.TIPO_EQUIPO.LISTAR, { per_page: 1000 });
        if (response.success !== false) {
            // Extraer tipos únicos de la respuesta
            const tiposUnicos = response.results.reduce((acc, item) => {
                if (!acc.some(t => t.id === item.tipo_equipo_id)) {
                    acc.push({
                        id: item.tipo_equipo_id,
                        name: item.tipo_equipo_name
                    });
                }
                return acc;
            }, []);
            
            return {
                success: true,
                results: tiposUnicos.sort((a, b) => a.name.localeCompare(b.name))
            };
        }
        return response;
    },

    async getProductosPorTipoEquipo(tipoEquipoId) {
        // Usar el endpoint de tipo equipo con parámetro para obtener todos los registros
        const response = await BaseAPI.get(ENDPOINTS.TIPO_EQUIPO.LISTAR, { per_page: 1000 });
        if (response.success !== false) {
            const productosFiltered = response.results
                .filter(item => String(item.tipo_equipo_id) === String(tipoEquipoId))
                .reduce((acc, item) => {
                    if (!acc.some(p => p.id === item.producto_id)) {
                        acc.push({
                            id: item.producto_id,
                            name: item.producto_name
                        });
                    }
                    return acc;
                }, []);
            
            return {
                success: true,
                results: productosFiltered.sort((a, b) => a.name.localeCompare(b.name))
            };
        }
        return response;
    },

    async getTiposCriticidadPorProducto(productoId) {
        // Usar el endpoint de tipo equipo con parámetro para obtener todos los registros
        const response = await BaseAPI.get(ENDPOINTS.TIPO_EQUIPO.LISTAR, { per_page: 1000 });
        if (response.success !== false) {
            const tiposFiltered = response.results
                .filter(item => String(item.producto_id) === String(productoId))
                .reduce((acc, item) => {
                    if (!acc.some(t => t.id === item.tipo_criticidad_id)) {
                        acc.push({
                            id: item.tipo_criticidad_id,
                            name: item.tipo_criticidad_name
                        });
                    }
                    return acc;
                }, []);
            
            return {
                success: true,
                results: tiposFiltered.sort((a, b) => a.name.localeCompare(b.name))
            };
        }
        return response;
    },

    async getCriticidadesPorTipo(tipoCriticidadId) {
        // Usar el endpoint de tipo equipo con parámetro para obtener todos los registros
        const response = await BaseAPI.get(ENDPOINTS.TIPO_EQUIPO.LISTAR, { per_page: 1000 });
        if (response.success !== false) {
            const criticidadesFiltered = response.results
                .filter(item => String(item.tipo_criticidad_id) === String(tipoCriticidadId))
                .reduce((acc, item) => {
                    if (!acc.some(c => c.id === item.criticidad_id)) {
                        acc.push({
                            id: item.criticidad_id,
                            name: item.criticidad_name
                        });
                    }
                    return acc;
                }, []);
            
            return {
                success: true,
                results: criticidadesFiltered.sort((a, b) => a.name.localeCompare(b.name))
            };
        }
        return response;
    }
};
