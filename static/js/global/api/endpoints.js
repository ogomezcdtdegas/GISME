// endpoints.js - Centralizador de URLs de la API

export const ENDPOINTS = {
    PRODUCTOS: {
        LISTAR: '/complementos/listar-todo-productos/',
        CREAR: '/complementos/crear-producto-completo/',
        ACTUALIZAR: (id) => `/complementos/editar-producto/${id}/`,
        POR_ID: (id) => `/complementos/editar-producto/${id}/`,
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
        LISTAR: '/complementos/tipoEquipo-list-pag/',
        CREAR: '/complementos/crear-tipoEquipo/',
        ACTUALIZAR: (id) => `/complementos/editar-tipoEquipo/${id}/`,
        ELIMINAR: (id) => `/complementos/eliminar-tipo-equipo/${id}/`,
        ELIMINAR_RELACION: (id) => `/complementos/eliminar-tipo-equipo-relacion/${id}/`
    },
    TECNOLOGIA: {
        LISTAR: '/complementos/tecnologia-list-pag/',
        CREAR: '/complementos/crear-tecnologia/',
        ACTUALIZAR: (id) => `/complementos/editar-tecnologia/${id}/`,
        ELIMINAR: (id) => `/complementos/eliminar-tecnologia/${id}/`,
        ELIMINAR_RELACION: (id) => `/complementos/eliminar-tecnologia-relacion/${id}/`
    },
    UBICACION: {
        LISTAR: '/complementos/ubicaciones/',
        LISTAR_TODOS: '/complementos/listar-todo-ubicaciones/',
        CREAR: '/complementos/crear-ubicacion/',
        POR_ID: (id) => `/complementos/ubicacion/${id}/`,
        ACTUALIZAR: (id) => `/complementos/editar-ubicacion/${id}/`,
        ELIMINAR: (id) => `/complementos/eliminar-ubicacion/${id}/`
    },
    SISTEMA: {
        LISTAR: '/complementos/listar-sistemas-pag/',
        LISTAR_TODOS: '/complementos/listar-todo-sistemas/',
        CREAR: '/complementos/crear-sistema/',
        POR_ID: (id) => `/complementos/sistema/${id}/`,
        ACTUALIZAR: (id) => `/complementos/editar-sistema/${id}/`,
        ELIMINAR: (id) => `/complementos/eliminar-sistema/${id}/`
    }
};
