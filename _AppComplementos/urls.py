from django.urls import path

''' Criticidad '''
from .views.views_Criticidad.Commands import CreateCriticidadCommand, UpdateCriticidadCommand
from .views.views_Criticidad.Queries import GetAllCriticidadPagQuery, GetAllCriticidadListQuery

''' Tipo Criticidad '''
from .views.views_tipoCriticidad.Commands import CreateTipoCriticidadCommand, UpdateTipoCriticidadCommand
from .views.views_tipoCriticidad.Queries import GetAllTipoCriticidadPagQuery

urlpatterns = [
    path('', GetAllCriticidadPagQuery.allCriticidadPag.as_view(), name='allCriticidadesPag'),
    path('crear-criticidad/', CreateCriticidadCommand.crearCriticidad.as_view(), name='crearCriticidad'),
    path('editar-criticidad/<uuid:obj_id>/', UpdateCriticidadCommand.editarCriticidad.as_view(), name='editarCriticidad'),

    path('tipCriticidades/', GetAllTipoCriticidadPagQuery.allTipCriticidadPag.as_view(), name='allTipCriticidadesPag'),
    path('crear-tipCriticidad/', CreateTipoCriticidadCommand.crearTipCriticidad.as_view(), name='crearTipCriticidad'),
    path('editar-tipCriticidad/<uuid:obj_id>/', UpdateTipoCriticidadCommand.editarTipCriticidad.as_view(), name='editarTipCriticidad'),

    path('listar-todo-criticidad/', GetAllCriticidadListQuery.CriticidadListAllView.as_view(), name='listarTodoCriticidad'),
]
