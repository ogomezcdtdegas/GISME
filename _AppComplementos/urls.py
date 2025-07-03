from django.urls import path

''' Criticidad '''
from .views.views_Criticidad.Commands import CreateCriticidadCommand, UpdateCriticidadCommand
from .views.views_Criticidad.Queries import GetAllCriticidadPagQuery, GetAllCriticidadListQuery, GetCriticidadPorTipoCritQuery

''' Tipo Criticidad '''
from .views.views_tipoCriticidad.Commands import CreateTipoCriticidadCommand, UpdateTipoCriticidadCommand
from .views.views_tipoCriticidad.Queries import GetAllTipoCriticidadPagQuery, GetAllTipoCriticidadListQuery

''' Producto '''
from .views.views_Producto.Commands import CreateProductoCommand
from .views.views_Producto.Commands import UpdateProductoCommand
from .views.views_Producto.Queries import GetAllProductoPagQuery

urlpatterns = [
    path('', GetAllCriticidadPagQuery.allCriticidadPag.as_view(), name='allCriticidadesPag'),
    path('listar-todo-criticidad/', GetAllCriticidadListQuery.CriticidadListAllView.as_view(), name='listarTodoCriticidad'),
    path('crear-criticidad/', CreateCriticidadCommand.crearCriticidad.as_view(), name='crearCriticidad'),
    path('editar-criticidad/<uuid:obj_id>/', UpdateCriticidadCommand.editarCriticidad.as_view(), name='editarCriticidad'),
    path('criticidades-por-tipo/<uuid:tipo_id>/',GetCriticidadPorTipoCritQuery.CriticidadesPorTipoView.as_view(),name='criticidades_por_tipo'),

    path('listar-todo-tipocriticidad/', GetAllTipoCriticidadListQuery.TipoCriticidadListAllView.as_view(), name='listarTipoCriticidad'),
    path('tipos-criticidad-unicos/', GetAllTipoCriticidadListQuery.TiposCriticidadUnicosView.as_view(), name='tiposCriticidadUnicos'),
    path('tipCriticidades/', GetAllTipoCriticidadPagQuery.allTipCriticidadPag.as_view(), name='allTipCriticidadesPag'),
    path('crear-tipCriticidad/', CreateTipoCriticidadCommand.crearTipCriticidad.as_view(), name='crearTipCriticidad'),
    path('editar-tipCriticidad/<uuid:obj_id>/', UpdateTipoCriticidadCommand.editarTipCriticidad.as_view(), name='editarTipCriticidad'),

    path('listar-todo-productos/', GetAllProductoPagQuery.allProductosPag.as_view(), name='allProductosPag'),
    path('crear-producto-completo/', CreateProductoCommand.CrearProductoCompletoView.as_view(), name='crearProducto'),
    path('editar-producto/<uuid:obj_id>/', UpdateProductoCommand.EditarProductoView.as_view(), name='editar_producto'),
]
