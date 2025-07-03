// endpoints.js - Centralizador de URLs de la API

export const ENDPOINTS = {
    PRODUCTOS: {
        LISTAR: '/complementos/listar-todo-productos/',
        CREAR: '/complementos/crear-producto-completo/',
        ACTUALIZAR: (id) => `/complementos/editar-producto/${id}/`
    },
    CRITICIDAD: {
        LISTAR: '/complementos/',
        LISTAR_TODOS: '/complementos/listar-todo-criticidad/',
        CREAR: '/complementos/crear-criticidad/',
        ACTUALIZAR: (id) => `/complementos/editar-criticidad/${id}/`,
        POR_TIPO: (tipoId) => `/complementos/criticidades-por-tipo/${tipoId}/`,
        POR_ID: (id) => `/complementos/criticidad/${id}/`
    },
    TIPO_CRITICIDAD: {
        LISTAR: '/complementos/tipCriticidades/',
        LISTAR_TODOS: '/complementos/listar-todo-tipocriticidad/',
        UNICOS: '/complementos/tipos-criticidad-unicos/',
        CREAR: '/complementos/crear-tipCriticidad/',
        ACTUALIZAR: (id) => `/complementos/editar-tipCriticidad/${id}/`,
        POR_ID: (id) => `/complementos/tipo-criticidad/${id}/`
    }
};
