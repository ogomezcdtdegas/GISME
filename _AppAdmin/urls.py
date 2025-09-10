"""
URLs para _AppAdmin usando vistas refactorizadas con repoGenerico
"""
from django.urls import path
from .views import (
    AdminPanelView,
    AdminUserListAPIView,
    AdminUserCreateAPIView,
    AdminUserDetailAPIView,
    AdminUserDeleteAPIView,
    AdminRolesAPIView
)

app_name = '_AppAdmin'

urlpatterns = [
    # Vista principal del panel
    path('', AdminPanelView.as_view(), name='index'),
    path('usuarios/crear/', AdminPanelView.as_view(), name='crear_usuario'),  # Compatibilidad
    
    # API Endpoints usando repoGenerico
    path('api/users/', AdminUserListAPIView.as_view(), name='api_users_list'),
    path('api/users/create/', AdminUserCreateAPIView.as_view(), name='api_users_create'),
    path('api/users/<int:pk>/', AdminUserDetailAPIView.as_view(), name='api_users_detail'),
    path('api/users/<int:pk>/delete/', AdminUserDeleteAPIView.as_view(), name='api_users_delete'),
    path('api/roles/', AdminRolesAPIView.as_view(), name='api_roles'),
    
    # URLs de compatibilidad con las URLs originales
    path('usuarios/editar/<int:pk>/', AdminUserDetailAPIView.as_view(), name='editar_usuario'),
    path('usuarios/eliminar/', AdminUserDeleteAPIView.as_view(), name='eliminar_usuario'),
]