from django.urls import path
from .views import UsuarioCreateView

urlpatterns = [
    path('usuarios/crear/', UsuarioCreateView.as_view(), name='crear_usuario'),
]