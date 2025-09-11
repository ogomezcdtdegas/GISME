"""
URLs para _AppAdmin usando estructura CQS con paginación
"""
from django.urls import path
from .views.views_AdminUser.views_template import AdminUserPaginatedHTML
from .views.views_AdminUser.Commands.CreateAdminUserCommand import CreateAdminUserCommand
from .views.views_AdminUser.Commands.UpdateAdminUserCommand import UpdateAdminUserCommand
from .views.views_AdminUser.Commands.DeleteAdminUserCommand import DeleteAdminUserCommand
from .views.views_AdminUser.Queries.GetAdminUserListQuery import GetAdminUserListQuery
from .views.views_AdminUser.Queries.GetAdminUserByIdQuery import GetAdminUserByIdQuery
from .views.views_AdminUser.Queries.GetAdminRolesQuery import GetAdminRolesQuery
from .views.views_AdminUser.Queries.GetAdminUserPaginatedAPI import AdminUserPaginatedAPI

app_name = '_AppAdmin'

urlpatterns = [
    # Vista principal con paginación (Template View)
    path('', AdminUserPaginatedHTML.as_view(), name='index'),
    path('usuarios/crear/', AdminUserPaginatedHTML.as_view(), name='crear_usuario'),  # Compatibilidad
    
    # API Endpoints usando estructura CQS
    # Queries (Consultas)
    path('api/users/', GetAdminUserListQuery.as_view(), name='api_users_list'),
    path('api/users/paginated/', AdminUserPaginatedAPI.as_view(), name='api_users_paginated'),
    path('api/users/<int:pk>/', UpdateAdminUserCommand.as_view(), name='api_users_detail'),  # GET/PUT al mismo endpoint
    path('api/roles/', GetAdminRolesQuery.as_view(), name='api_roles'),
    
    # Commands (Acciones)
    path('api/users/create/', CreateAdminUserCommand.as_view(), name='api_users_create'),
    path('api/users/<int:pk>/delete/', DeleteAdminUserCommand.as_view(), name='api_users_delete'),
    
    # URLs de compatibilidad con las URLs originales
    path('usuarios/editar/<int:pk>/', UpdateAdminUserCommand.as_view(), name='editar_usuario'),
    path('usuarios/eliminar/', DeleteAdminUserCommand.as_view(), name='eliminar_usuario'),
]