from django.urls import path

''' Criticidad '''
from .views.views_Criticidad.Commands import CreateCriticidadCommand, UpdateCriticidadCommand
from .views.views_Criticidad.Queries import GetAllCriticidadPagQuery, GetAllCriticidadListQuery, GetCriticidadPorTipoCritQuery
from .views.views_Criticidad.Commands.DeleteCriticidadCommand.DeleteCriticidadCommand import DeleteCriticidadCommand

''' Tipo Criticidad '''
from .views.views_tipoCriticidad.Commands import CreateTipoCriticidadCommand, UpdateTipoCriticidadCommand, DeleteTipoCriticidadCommand
from .views.views_tipoCriticidad.Commands.DeleteTipoCriticidadRelacionCommand.DeleteTipoCriticidadRelacionCommand import DeleteTipoCriticidadRelacionCommand
from .views.views_tipoCriticidad.Queries import GetAllTipoCriticidadPagQuery, GetAllTipoCriticidadListQuery

''' Producto '''
from .views.views_Producto.Commands import (
    CreateProductoCommand, 
    UpdateProductoCommand, 
    DeleteProductoCommand,
    DeleteProductoRelacionCommand
)
from .views.views_Producto.Queries import GetAllProductoPagQuery

''' Tipo Equipo '''
from .views.views_TipoEquipo.Commands import (
    crearTipoEquipo,
    EditarTipoEquipoView,
    DeleteTipoEquipoCommand,
    DeleteTipoEquipoRelacionCommand
)
from .views.views_TipoEquipo.Queries import allTipoEquiposPag

urlpatterns = [
    path('', GetAllCriticidadPagQuery.allCriticidadPag.as_view(), name='allCriticidadesPag'),
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

    path('listar-todo-productos/', GetAllProductoPagQuery.allProductosPag.as_view(), name='allProductosPag'),
    path('crear-producto-completo/', CreateProductoCommand.CrearProductoCompletoView.as_view(), name='crearProducto'),
    path('editar-producto/<uuid:obj_id>/', UpdateProductoCommand.EditarProductoView.as_view(), name='editar_producto'),
    path('eliminar-producto/<uuid:obj_id>/', DeleteProductoCommand.as_view(), name='eliminarProducto'),
    path('eliminar-producto-relacion/<uuid:obj_id>/', DeleteProductoRelacionCommand.as_view(), name='eliminarProductoRelacion'),
    
    # Tipo Equipo URLs
    path('tipoEquipos/', allTipoEquiposPag.as_view(), name='allTiposEquipoPag'),
    path('crear-tipoEquipo/', crearTipoEquipo.as_view(), name='crearTipoEquipo'),
    path('editar-tipoEquipo/<uuid:obj_id>/', EditarTipoEquipoView.as_view(), name='editarTipoEquipo'),
    path('eliminar-tipo-equipo/<uuid:obj_id>/', DeleteTipoEquipoCommand.as_view(), name='eliminarTipoEquipo'),
    path('eliminar-tipo-equipo-relacion/<uuid:obj_id>/', DeleteTipoEquipoRelacionCommand.as_view(), name='eliminarTipoEquipoRelacion'),
]
