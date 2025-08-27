from django.urls import path
from .views import UsuarioCreateView, UsuarioUpdateView, UsuarioDeleteView

urlpatterns = [
    path('usuarios/crear/', UsuarioCreateView.as_view(), name='crear_usuario'),
    path('usuarios/editar/<int:pk>/', UsuarioUpdateView.as_view(), name='editar_usuario'),
    path('usuarios/eliminar/', UsuarioDeleteView.as_view(), name='eliminar_usuario'),
]