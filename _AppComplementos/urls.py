from django.urls import path


'''.....................................................................................................................................'''
# Ubicación
from .views.views_Ubicacion.views_with_logging import CreateUbicacionWithLogging, UpdateUbicacionWithLogging, DeleteUbicacionWithLogging
from .views.views_Ubicacion.Queries.GetAllUbicacionPagQuery import UbicacionListPagView
from .views.views_Ubicacion.Queries.GetAllUbicacionListQuery import UbicacionListAllView
from .views.views_Ubicacion.Queries.GetUbicacionByIdQuery import GetUbicacionByIdView
from .views.views_Ubicacion.views_template import UbicacionListPagHTML
#---------------------------------------------------------------------------------------

'''.....................................................................................................................................'''
# Sistema  
from .views.views_Sistema.views_with_logging import CreateSistemaWithLogging, UpdateSistemaWithLogging, DeleteSistemaWithLogging
from .views.views_Sistema import ListarSistemasQueryView, ListarTodosSistemasQueryView, SistemaBaseView, SistemasIndexView, ObtenerSistemaQueryView
#---------------------------------------------------------------------------------------# Grouped URL patterns by resource


ubicacion_urls = [
    path('listar-todo-ubicaciones/', UbicacionListPagHTML.as_view(), name='allUbicacionesPag'),
    path('ubicaciones/', UbicacionListPagHTML.as_view(), name='ubicacion_paginated_html'),
    path('ubicaciones-list-pag/', UbicacionListPagView.as_view(), name='ubicacion_paginated_api'),
    path('listar-todo-ubicaciones/', UbicacionListAllView.as_view(), name='listarTodoUbicaciones'),
    path('crear-ubicacion/', CreateUbicacionWithLogging.as_view(), name='crearUbicacion'),
    path('ubicacion/<uuid:obj_id>/', GetUbicacionByIdView.as_view(), name='obtenerUbicacion'),
    path('editar-ubicacion/<uuid:obj_id>/', UpdateUbicacionWithLogging.as_view(), name='editarUbicacion'),
    path('eliminar-ubicacion/<uuid:obj_id>/', DeleteUbicacionWithLogging.as_view(), name='eliminarUbicacion'),
]

sistema_urls = [
    path('sistemas/', SistemasIndexView.as_view(), name='allSistemasPag'),
    path('listar-sistemas-pag/', ListarSistemasQueryView.as_view(), name='listarSistemasPag'),
    path('listar-todo-sistemas/', ListarTodosSistemasQueryView.as_view(), name='listarTodoSistemas'),
    path('sistema/<uuid:sistema_id>/', ObtenerSistemaQueryView.as_view(), name='obtenerSistema'),
    path('crear-sistema/', CreateSistemaWithLogging.as_view(), name='crearSistema'),
    path('editar-sistema/<uuid:sistema_id>/', UpdateSistemaWithLogging.as_view(), name='editarSistema'),
    path('eliminar-sistema/<uuid:sistema_id>/', DeleteSistemaWithLogging.as_view(), name='eliminarSistema'),
    path('debug-sistema/<uuid:pk>/', SistemaBaseView.as_view(), name='debugSistema'),
]

# Combine all URL patterns
urlpatterns = (
    ubicacion_urls +
    sistema_urls
)