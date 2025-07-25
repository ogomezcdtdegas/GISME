from django.urls import path

'''.....................................................................................................................................'''
# Criticidad ---------------------------------------------------------------------------------------
from .views.views_Criticidad.Commands import CreateCriticidadCommand, UpdateCriticidadCommand
from .views.views_Criticidad.Commands.DeleteCriticidadCommand import DeleteCriticidadCommand
from .views.views_Criticidad.Queries import GetAllCriticidadListQuery, GetCriticidadPorTipoCritQuery
from .views.views_Criticidad.Queries import GetAllCriticidadPagQuery
from .views.views_Criticidad.views_template import CriticidadPaginatedHTML
#---------------------------------------------------------------------------------------

'''.....................................................................................................................................'''
# Tipo Criticidad
from .views.views_tipoCriticidad.Commands import CreateTipoCriticidadCommand, UpdateTipoCriticidadCommand, DeleteTipoCriticidadCommand, DeleteTipoCriticidadRelacionCommand
from .views.views_tipoCriticidad.Queries import GetAllTipoCriticidadListQuery, GetAllTipoCriticidadPagQuery
from .views.views_tipoCriticidad.views_template import TipoCriticidadPaginatedHTML
#---------------------------------------------------------------------------------------

'''.....................................................................................................................................'''
# Producto
from .views.views_Producto.Commands import CreateProductoCommand, UpdateProductoCommand, DeleteProductoCommand, DeleteProductoRelacionCommand
from .views.views_Producto.Queries import GetAllProductoPagQuery
from .views.views_Producto.views_template import ProductoPaginatedHTML
#---------------------------------------------------------------------------------------

'''.....................................................................................................................................'''
# Tipo Equipo
from .views.views_TipoEquipo.Commands import crearTipoEquipo, EditarTipoEquipoView, DeleteTipoEquipoCommand, DeleteTipoEquipoRelacionCommand
from .views.views_TipoEquipo.Queries import TipoEquipoPaginatedAPI
from .views.views_TipoEquipo.views_template import TipoEquipoPaginatedHTML
#---------------------------------------------------------------------------------------

'''.....................................................................................................................................'''
# Tecnología
from .views.views_Tecnologia.Commands import crearTecnologia, EditarTecnologiaView, DeleteTecnologiaCommand
from .views.views_Tecnologia.Commands.DeleteTecnologiaRelacionCommand import DeleteTecnologiaRelacionCommand
from .views.views_Tecnologia.Queries import GetAllTecnologiaPagQuery
from .views.views_Tecnologia.views_template import TecnologiaPaginatedHTML
#---------------------------------------------------------------------------------------

'''.....................................................................................................................................'''
# Ubicación
from .views.views_Ubicacion.Commands.CreateUbicacionCommand import CreateUbicacionView
from .views.views_Ubicacion.Commands.UpdateUbicacionCommand import UpdateUbicacionView
from .views.views_Ubicacion.Commands.DeleteUbicacionCommand import DeleteUbicacionView
from .views.views_Ubicacion.Queries.GetAllUbicacionPagQuery import UbicacionListPagView
from .views.views_Ubicacion.Queries.GetAllUbicacionListQuery import UbicacionListAllView
from .views.views_Ubicacion.Queries.GetUbicacionByIdQuery import GetUbicacionByIdView
from .views.views_Ubicacion.views_template import UbicacionListPagHTML
#---------------------------------------------------------------------------------------

'''.....................................................................................................................................'''
# Sistema
from .views.views_Sistema import CrearSistemaCommandView, EditarSistemaCommandView, EliminarSistemaCommandView, ListarSistemasQueryView, ListarTodosSistemasQueryView, SistemaBaseView, SistemasIndexView, ObtenerSistemaQueryView
#---------------------------------------------------------------------------------------

# Grouped URL patterns by resource
criticidad_urls = [
    path('', CriticidadPaginatedHTML.as_view(), name='allCriticidadesPag'),
    path('criticidad/', CriticidadPaginatedHTML.as_view(), name='criticidad_paginated_html'),
    path('criticidad-list-pag/', GetAllCriticidadPagQuery.CriticidadPaginatedAPI.as_view(), name='criticidad_paginated_api'),
    path('listar-todo-criticidad/', GetAllCriticidadListQuery.CriticidadListAllView.as_view(), name='listarTodoCriticidad'),
    path('crear-criticidad/', CreateCriticidadCommand.crearCriticidad.as_view(), name='crearCriticidad'),
    path('editar-criticidad/<uuid:obj_id>/', UpdateCriticidadCommand.editarCriticidad.as_view(), name='editarCriticidad'),
    path('criticidades-por-tipo/<uuid:tipo_id>/', GetCriticidadPorTipoCritQuery.CriticidadesPorTipoView.as_view(), name='criticidades_por_tipo'),
    path('eliminar-criticidad/<uuid:obj_id>/', DeleteCriticidadCommand.as_view(), name='eliminarCriticidad'),
]

tipo_criticidad_urls = [
    path('listar-todo-tipocriticidades/', TipoCriticidadPaginatedHTML.as_view(), name='allTipCriticidadesPag'),
    path('tipCriticidades/', GetAllTipoCriticidadPagQuery.TipoCriticidadPaginatedAPI.as_view(), name='tipocriticidad_paginated_api'),
    path('tipoCriticidad-list-pag/', GetAllTipoCriticidadPagQuery.TipoCriticidadPaginatedAPI.as_view(), name='tipocriticidad_paginated_api_modern'),
    path('listar-todo-tipocriticidad/', GetAllTipoCriticidadListQuery.TipoCriticidadListAllView.as_view(), name='listarTipoCriticidad'),
    path('tipos-criticidad-unicos/', GetAllTipoCriticidadListQuery.TiposCriticidadUnicosView.as_view(), name='tiposCriticidadUnicos'),
    path('crear-tipCriticidad/', CreateTipoCriticidadCommand.crearTipCriticidad.as_view(), name='crearTipCriticidad'),
    path('editar-tipCriticidad/<uuid:obj_id>/', UpdateTipoCriticidadCommand.editarTipCriticidad.as_view(), name='editarTipCriticidad'),
    path('eliminar-tipo-criticidad/<uuid:obj_id>/', DeleteTipoCriticidadCommand.as_view(), name='eliminarTipoCriticidad'),
    path('eliminar-tipo-criticidad-relacion/<uuid:obj_id>/', DeleteTipoCriticidadRelacionCommand.as_view(), name='eliminarTipoCriticidadRelacion'),
]

producto_urls = [
    path('listar-todo-productos/', ProductoPaginatedHTML.as_view(), name='allProductosPag'),
    path('producto/', ProductoPaginatedHTML.as_view(), name='producto_paginated_html'),
    path('producto-list-pag/', GetAllProductoPagQuery.ProductoPaginatedAPI.as_view(), name='producto_paginated_api'),
    path('crear-producto-completo/', CreateProductoCommand.CrearProductoCompletoView.as_view(), name='crearProducto'),
    path('editar-producto/<uuid:obj_id>/', UpdateProductoCommand.EditarProductoView.as_view(), name='editar_producto'),
    path('eliminar-producto/<uuid:obj_id>/', DeleteProductoCommand.as_view(), name='eliminarProducto'),
    path('eliminar-producto-relacion/<uuid:obj_id>/', DeleteProductoRelacionCommand.as_view(), name='eliminarProductoRelacion'),
]

tipo_equipo_urls = [
    path('listar-todo-tipoequipos/', TipoEquipoPaginatedHTML.as_view(), name='allTiposEquipoPag'),
    path('tipoEquipos/', TipoEquipoPaginatedHTML.as_view(), name='tipoequipo_paginated_html'),
    path('tipoEquipo-list-pag/', TipoEquipoPaginatedAPI.as_view(), name='tipoequipo_paginated_api'),
    path('crear-tipoEquipo/', crearTipoEquipo.as_view(), name='crearTipoEquipo'),
    path('editar-tipoEquipo/<uuid:obj_id>/', EditarTipoEquipoView.as_view(), name='editarTipoEquipo'),
    path('eliminar-tipo-equipo/<uuid:obj_id>/', DeleteTipoEquipoCommand.as_view(), name='eliminarTipoEquipo'),
    path('eliminar-tipo-equipo-relacion/<uuid:obj_id>/', DeleteTipoEquipoRelacionCommand.as_view(), name='eliminarTipoEquipoRelacion'),
]

tecnologia_urls = [
    path('listar-todo-tecnologias/', TecnologiaPaginatedHTML.as_view(), name='allTecnologiasPag'),
    path('tecnologia/', TecnologiaPaginatedHTML.as_view(), name='tecnologia_paginated_html'),
    path('tecnologia-list-pag/', GetAllTecnologiaPagQuery.TecnologiaPaginatedAPI.as_view(), name='tecnologia_paginated_api'),
    path('crear-tecnologia/', crearTecnologia.as_view(), name='crearTecnologia'),
    path('editar-tecnologia/<uuid:obj_id>/', EditarTecnologiaView.as_view(), name='editarTecnologia'),
    path('eliminar-tecnologia/<uuid:obj_id>/', DeleteTecnologiaCommand.as_view(), name='eliminarTecnologia'),
    path('eliminar-tecnologia-relacion/<uuid:obj_id>/', DeleteTecnologiaRelacionCommand.as_view(), name='eliminarTecnologiaRelacion'),
]

ubicacion_urls = [
    path('listar-todo-ubicaciones/', UbicacionListPagHTML.as_view(), name='allUbicacionesPag'),
    path('ubicaciones/', UbicacionListPagHTML.as_view(), name='ubicacion_paginated_html'),
    path('ubicaciones-list-pag/', UbicacionListPagView.as_view(), name='ubicacion_paginated_api'),
    path('listar-todo-ubicaciones/', UbicacionListAllView.as_view(), name='listarTodoUbicaciones'),
    path('crear-ubicacion/', CreateUbicacionView.as_view(), name='crearUbicacion'),
    path('ubicacion/<uuid:obj_id>/', GetUbicacionByIdView.as_view(), name='obtenerUbicacion'),
    path('editar-ubicacion/<uuid:obj_id>/', UpdateUbicacionView.as_view(), name='editarUbicacion'),
    path('eliminar-ubicacion/<uuid:obj_id>/', DeleteUbicacionView.as_view(), name='eliminarUbicacion'),
]

sistema_urls = [
    path('sistemas/', SistemasIndexView.as_view(), name='allSistemasPag'),
    path('listar-sistemas-pag/', ListarSistemasQueryView.as_view(), name='listarSistemasPag'),
    path('listar-todo-sistemas/', ListarTodosSistemasQueryView.as_view(), name='listarTodoSistemas'),
    path('sistema/<uuid:sistema_id>/', ObtenerSistemaQueryView.as_view(), name='obtenerSistema'),
    path('crear-sistema/', CrearSistemaCommandView.as_view(), name='crearSistema'),
    path('editar-sistema/<uuid:sistema_id>/', EditarSistemaCommandView.as_view(), name='editarSistema'),
    path('eliminar-sistema/<uuid:sistema_id>/', EliminarSistemaCommandView.as_view(), name='eliminarSistema'),
    path('debug-sistema/<uuid:pk>/', SistemaBaseView.as_view(), name='debugSistema'),
]

# Combine all URL patterns
urlpatterns = (
    criticidad_urls +
    tipo_criticidad_urls +
    producto_urls +
    tipo_equipo_urls +
    tecnologia_urls +
    ubicacion_urls +
    sistema_urls
)