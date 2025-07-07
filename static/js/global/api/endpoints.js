// endpoints.js - Centralizador de URLs de la API

export const ENDPOINTS = {
    PRODUCTOS: {
        LISTAR: '/complementos/listar-todo-productos/',
        CREAR: '/complementos/crear-producto-completo/',
        ACTUALIZAR: (id) => `/complementos/editar-producto/${id}/`,
        ELIMINAR: (id) => `/complementos/eliminar-producto/${id}/`,
        ELIMINAR_RELACION: (id) => `/complementos/eliminar-producto-relacion/${id}/`
    },
    CRITICIDAD: {
        LISTAR: '/complementos/',
        LISTAR_TODOS: '/complementos/listar-todo-criticidad/',
        CREAR: '/complementos/crear-criticidad/',
        ACTUALIZAR: (id) => `/complementos/editar-criticidad/${id}/`,
        POR_TIPO: (tipoId) => `/complementos/criticidades-por-tipo/${tipoId}/`,
        POR_ID: (id) => `/complementos/criticidad/${id}/`,
        ELIMINAR: (id) => `/complementos/eliminar-criticidad/${id}/`
    },
    TIPO_CRITICIDAD: {
        LISTAR: '/complementos/tipCriticidades/',
        LISTAR_TODOS: '/complementos/listar-todo-tipocriticidad/',
        UNICOS: '/complementos/tipos-criticidad-unicos/',
        CREAR: '/complementos/crear-tipCriticidad/',
        ACTUALIZAR: (id) => `/complementos/editar-tipCriticidad/${id}/`,
        ELIMINAR: (id) => `/complementos/eliminar-tipo-criticidad/${id}/`,
        ELIMINAR_RELACION: (id) => `/complementos/eliminar-tipo-criticidad-relacion/${id}/`,
        POR_ID: (id) => `/complementos/tipo-criticidad/${id}/`
    },
    TIPO_EQUIPO: {
        LISTAR: '/complementos/tipoEquipos/',
        CREAR: '/complementos/crear-tipoEquipo/',
        ACTUALIZAR: (id) => `/complementos/editar-tipoEquipo/${id}/`,
        ELIMINAR: (id) => `/complementos/eliminar-tipo-equipo/${id}/`,
        ELIMINAR_RELACION: (id) => `/complementos/eliminar-tipo-equipo-relacion/${id}/`
    }
};
