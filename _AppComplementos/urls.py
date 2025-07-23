from django.urls import path

# Criticidad
from .views.views_Criticidad.Commands import CreateCriticidadCommand, UpdateCriticidadCommand
from .views.views_Criticidad.Queries import GetAllCriticidadListQuery, GetCriticidadPorTipoCritQuery
from .views.views_Criticidad.Commands.DeleteCriticidadCommand.DeleteCriticidadCommand import DeleteCriticidadCommand

# Tipo Criticidad
from .views.views_tipoCriticidad.Commands import CreateTipoCriticidadCommand, UpdateTipoCriticidadCommand, DeleteTipoCriticidadCommand
from .views.views_tipoCriticidad.Commands.DeleteTipoCriticidadRelacionCommand.DeleteTipoCriticidadRelacionCommand import DeleteTipoCriticidadRelacionCommand
from .views.views_tipoCriticidad.Queries import GetAllTipoCriticidadPagQuery, GetAllTipoCriticidadListQuery

# Producto
from .views.views_Producto.Commands import (
    CreateProductoCommand, 
    UpdateProductoCommand, 
    DeleteProductoCommand,
    DeleteProductoRelacionCommand
)
from .views.views_Producto.Queries import GetAllProductoPagQuery

# Tipo Equipo
from .views.views_TipoEquipo.Commands import (
    crearTipoEquipo,
    EditarTipoEquipoView,
    DeleteTipoEquipoCommand,
    DeleteTipoEquipoRelacionCommand
)
from .views.views_TipoEquipo.Queries import TipoEquipoPaginatedAPI, TipoEquipoPaginatedHTML

# Tecnología
from .views.views_Tecnologia.Commands import (
    crearTecnologia,
    EditarTecnologiaView,
    DeleteTecnologiaCommand
)
from .views.views_Tecnologia.Commands.DeleteTecnologiaRelacionCommand.DeleteTecnologiaRelacionCommand import DeleteTecnologiaRelacionCommand


# Ubicación
from .views.views_Ubicacion.Commands.CreateUbicacionCommand.CreateUbicacionCommand import CreateUbicacionView
from .views.views_Ubicacion.Commands.UpdateUbicacionCommand.UpdateUbicacionCommand import UpdateUbicacionView
from .views.views_Ubicacion.Commands.DeleteUbicacionCommand.DeleteUbicacionCommand import DeleteUbicacionView
from .views.views_Ubicacion.Queries.GetAllUbicacionPagQuery.GetAllUbicacionPagQuery import UbicacionListPagView
from .views.views_Ubicacion.Queries.GetAllUbicacionListQuery.GetAllUbicacionListQuery import UbicacionListAllView
from .views.views_Ubicacion.Queries.GetUbicacionByIdQuery.GetUbicacionByIdQuery import GetUbicacionByIdView

# Sistema - Nueva estructura modular
from .views.views_Sistema import (
    # Commands
    CrearSistemaCommandView,
    EditarSistemaCommandView,
    EliminarSistemaCommandView,
    
    # Queries
    ListarSistemasQueryView,
    ListarTodosSistemasQueryView,
    ObtenerSistemaQueryView,
    
    # Templates & Debug
    SistemasIndexView,
    SistemaBaseView
)

urlpatterns = [
    # Backward compatibility: old name for TipoEquipo paginada HTML
    path('listar-todo-tipoequipos/',
         __import__('_AppComplementos.views.views_TipoEquipo.Queries.GetAllTipoEquipoPagQuery.GetAllTipoEquipoPagQuery', fromlist=['TipoEquipoPaginatedHTML']).TipoEquipoPaginatedHTML.as_view(),
         name='allTiposEquipoPag'),
    # Backward compatibility: old name for Tecnología paginada HTML
    path('listar-todo-tecnologias/',
         __import__('_AppComplementos.views.views_Tecnologia.Queries.GetAllTecnologiaPagQuery.GetAllTecnologiaPagQuery', fromlist=['TecnologiaPaginatedHTML']).TecnologiaPaginatedHTML.as_view(),
         name='allTecnologiasPag'),
    # Backward compatibility: old name for Producto paginada HTML
    path('listar-todo-productos/',
         __import__('_AppComplementos.views.views_Producto.Queries.GetAllProductoPagQuery.GetAllProductoPagQuery', fromlist=['ProductoPaginatedHTML']).ProductoPaginatedHTML.as_view(),
         name='allProductosPag'),
    # Backward compatibility: old name for Criticidad paginada HTML
    path('',
         __import__('_AppComplementos.views.views_Criticidad.Queries.GetAllCriticidadPagQuery.GetAllCriticidadPagQuery', fromlist=['CriticidadPaginatedHTML']).CriticidadPaginatedHTML.as_view(),
         name='allCriticidadesPag'),
    # Criticidad paginada HTML
    path('criticidad/',
         __import__('_AppComplementos.views.views_Criticidad.Queries.GetAllCriticidadPagQuery.GetAllCriticidadPagQuery', fromlist=['CriticidadPaginatedHTML']).CriticidadPaginatedHTML.as_view(),
         name='criticidad_paginated_html'),

    # Criticidad paginada API (JSON)
    path('criticidad-list-pag/',
         __import__('_AppComplementos.views.views_Criticidad.Queries.GetAllCriticidadPagQuery.GetAllCriticidadPagQuery', fromlist=['CriticidadPaginatedAPI']).CriticidadPaginatedAPI.as_view(),
         name='criticidad_paginated_api'),
    path('listar-todo-criticidad/', GetAllCriticidadListQuery.CriticidadListAllView.as_view(), name='listarTodoCriticidad'),
    path('crear-criticidad/', CreateCriticidadCommand.crearCriticidad.as_view(), name='crearCriticidad'),
    path('editar-criticidad/<uuid:obj_id>/', UpdateCriticidadCommand.editarCriticidad.as_view(), name='editarCriticidad'),
    path('criticidades-por-tipo/<uuid:tipo_id>/',GetCriticidadPorTipoCritQuery.CriticidadesPorTipoView.as_view(),name='criticidades_por_tipo'),
    path('eliminar-criticidad/<uuid:obj_id>/', DeleteCriticidadCommand.as_view(), name='eliminarCriticidad'),

    path('listar-todo-tipocriticidad/', GetAllTipoCriticidadListQuery.TipoCriticidadListAllView.as_view(), name='listarTipoCriticidad'),
    path('tipos-criticidad-unicos/', GetAllTipoCriticidadListQuery.TiposCriticidadUnicosView.as_view(), name='tiposCriticidadUnicos'),
    path('tipCriticidades/', GetAllTipoCriticidadPagQuery.as_view(), name='allTipCriticidadesPag'),
    path('crear-tipCriticidad/', CreateTipoCriticidadCommand.crearTipCriticidad.as_view(), name='crearTipCriticidad'),
    path('editar-tipCriticidad/<uuid:obj_id>/', UpdateTipoCriticidadCommand.editarTipCriticidad.as_view(), name='editarTipCriticidad'),
    path('eliminar-tipo-criticidad/<uuid:obj_id>/', DeleteTipoCriticidadCommand.as_view(), name='eliminarTipoCriticidad'),
    path('eliminar-tipo-criticidad-relacion/<uuid:obj_id>/', DeleteTipoCriticidadRelacionCommand.as_view(), name='eliminarTipoCriticidadRelacion'),

    # Producto paginada HTML
    path('producto/',
         __import__('_AppComplementos.views.views_Producto.Queries.GetAllProductoPagQuery.GetAllProductoPagQuery', fromlist=['ProductoPaginatedHTML']).ProductoPaginatedHTML.as_view(),
         name='producto_paginated_html'),

    # Producto paginada API (JSON)
    path('producto-list-pag/',
         __import__('_AppComplementos.views.views_Producto.Queries.GetAllProductoPagQuery.GetAllProductoPagQuery', fromlist=['ProductoPaginatedAPI']).ProductoPaginatedAPI.as_view(),
         name='producto_paginated_api'),
    path('crear-producto-completo/', CreateProductoCommand.CrearProductoCompletoView.as_view(), name='crearProducto'),
    path('editar-producto/<uuid:obj_id>/', UpdateProductoCommand.EditarProductoView.as_view(), name='editar_producto'),
    path('eliminar-producto/<uuid:obj_id>/', DeleteProductoCommand.as_view(), name='eliminarProducto'),
    path('eliminar-producto-relacion/<uuid:obj_id>/', DeleteProductoRelacionCommand.as_view(), name='eliminarProductoRelacion'),
    
    # Tipo Equipo paginada HTML
    path('tipoEquipos/',
         __import__('_AppComplementos.views.views_TipoEquipo.Queries.GetAllTipoEquipoPagQuery.GetAllTipoEquipoPagQuery', fromlist=['TipoEquipoPaginatedHTML']).TipoEquipoPaginatedHTML.as_view(),
         name='tipoequipo_paginated_html'),

    # Tipo Equipo paginada API (JSON)
    path('tipoEquipo-list-pag/',
         __import__('_AppComplementos.views.views_TipoEquipo.Queries.GetAllTipoEquipoPagQuery.GetAllTipoEquipoPagQuery', fromlist=['TipoEquipoPaginatedAPI']).TipoEquipoPaginatedAPI.as_view(),
         name='tipoequipo_paginated_api'),

    path('crear-tipoEquipo/', crearTipoEquipo.as_view(), name='crearTipoEquipo'),
    path('editar-tipoEquipo/<uuid:obj_id>/', EditarTipoEquipoView.as_view(), name='editarTipoEquipo'),
    path('eliminar-tipo-equipo/<uuid:obj_id>/', DeleteTipoEquipoCommand.as_view(), name='eliminarTipoEquipo'),
    path('eliminar-tipo-equipo-relacion/<uuid:obj_id>/', DeleteTipoEquipoRelacionCommand.as_view(), name='eliminarTipoEquipoRelacion'),

    # Tecnología URLs
    # Tecnología paginada HTML
    path('tecnologia/',
         __import__('_AppComplementos.views.views_Tecnologia.Queries.GetAllTecnologiaPagQuery.GetAllTecnologiaPagQuery', fromlist=['TecnologiaPaginatedHTML']).TecnologiaPaginatedHTML.as_view(),
         name='tecnologia_paginated_html'),

    # Tecnología paginada API (JSON)
    path('tecnologia-list-pag/',
         __import__('_AppComplementos.views.views_Tecnologia.Queries.GetAllTecnologiaPagQuery.GetAllTecnologiaPagQuery', fromlist=['TecnologiaPaginatedAPI']).TecnologiaPaginatedAPI.as_view(),
         name='tecnologia_paginated_api'),
    path('crear-tecnologia/', crearTecnologia.as_view(), name='crearTecnologia'),
    path('editar-tecnologia/<uuid:obj_id>/', EditarTecnologiaView.as_view(), name='editarTecnologia'),
    path('eliminar-tecnologia/<uuid:obj_id>/', DeleteTecnologiaCommand.as_view(), name='eliminarTecnologia'),
    path('eliminar-tecnologia-relacion/<uuid:obj_id>/', DeleteTecnologiaRelacionCommand.as_view(), name='eliminarTecnologiaRelacion'),

    # Ubicación URLs
    path('ubicaciones/', UbicacionListPagView.as_view(), name='allUbicacionesPag'),
    path('listar-todo-ubicaciones/', UbicacionListAllView.as_view(), name='listarTodoUbicaciones'),
    path('crear-ubicacion/', CreateUbicacionView.as_view(), name='crearUbicacion'),
    path('ubicacion/<uuid:obj_id>/', GetUbicacionByIdView.as_view(), name='obtenerUbicacion'),
    path('editar-ubicacion/<uuid:obj_id>/', UpdateUbicacionView.as_view(), name='editarUbicacion'),
    path('eliminar-ubicacion/<uuid:obj_id>/', DeleteUbicacionView.as_view(), name='eliminarUbicacion'),

    # Sistema URLs - Templates (CBV)
    path('sistemas/', SistemasIndexView.as_view(), name='allSistemasPag'),
    
    # Sistema URLs - API Queries (CBV)
    path('listar-sistemas/', ListarSistemasQueryView.as_view(), name='listarSistemas'),
    path('listar-todo-sistemas/', ListarTodosSistemasQueryView.as_view(), name='listarTodoSistemas'),
    path('sistema/<uuid:sistema_id>/', ObtenerSistemaQueryView.as_view(), name='obtenerSistema'),
    
    # Sistema URLs - API Commands (CBV)
    path('crear-sistema/', CrearSistemaCommandView.as_view(), name='crearSistema'),
    path('editar-sistema/<uuid:sistema_id>/', EditarSistemaCommandView.as_view(), name='editarSistema'),
    path('eliminar-sistema/<uuid:sistema_id>/', EliminarSistemaCommandView.as_view(), name='eliminarSistema'),
    
    # Sistema URLs - Debug
    path('debug-sistema/<uuid:pk>/', SistemaBaseView.as_view(), name='debugSistema'),
]
