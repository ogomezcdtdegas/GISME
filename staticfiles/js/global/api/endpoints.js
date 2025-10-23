// endpoints.js - Centralizador de URLs de la API

export const ENDPOINTS = {
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
    },
    ADMIN_USERS: {
        LISTAR: '/admin_panel/api/users/paginated/',
        CREAR: '/admin_panel/api/users/create/',
        POR_ID: (id) => `/admin_panel/api/users/${id}/`,
        ACTUALIZAR: (id) => `/admin_panel/api/users/${id}/`,
        ELIMINAR: (id) => `/admin_panel/api/users/${id}/delete/`,
        ROLES: '/admin_panel/api/roles/'
    }
};
