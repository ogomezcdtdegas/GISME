"""
URLs para _AppAdmin usando estructura CQS con paginación
"""
from django.urls import path
from .views.views_AdminUser.views_template import AdminUserPaginatedHTML
# Importar las nuevas vistas con logging
from .views.views_AdminUser.views_with_logging import CreateAdminUserWithLogging, UpdateAdminUserWithLogging, DeleteAdminUserWithLogging

# Debugging: verificar que la vista correcta se está importando
print(f"🔧 DEBUGGING URLS:")
print(f"   - CreateAdminUserWithLogging: {CreateAdminUserWithLogging}")
print(f"   - MRO: {[cls.__name__ for cls in CreateAdminUserWithLogging.__mro__]}")
from .views.views_AdminUser.Queries.GetAdminUserListQuery import GetAdminUserListQuery
from .views.views_AdminUser.Queries.GetAdminUserByIdQuery import GetAdminUserByIdQuery
from .views.views_AdminUser.Queries.GetAdminRolesQuery import GetAdminRolesQuery
from .views.views_AdminUser.Queries.GetAdminUserPaginatedAPI import AdminUserPaginatedAPI

# Login Log imports
from .views.views_LoginLog.views_template import LoginLogTemplateView
from .views.views_LoginLog.Queries.GetLoginLogPaginatedQuery import GetLoginLogPaginatedQuery

# Action Log imports
from .views.views_ActionLog.views_template import ActionLogTemplateView
from .views.views_ActionLog.Queries.GetActionLogPaginatedQuery import GetActionLogPaginatedQuery

app_name = '_AppAdmin'

urlpatterns = [
    # Vista principal con paginación (Template View)
    path('', AdminUserPaginatedHTML.as_view(), name='index'),
    path('usuarios/crear/', AdminUserPaginatedHTML.as_view(), name='crear_usuario'),  # Compatibilidad
    
    # API Endpoints usando estructura CQS
    # Queries (Consultas)
    path('api/users/', GetAdminUserListQuery.as_view(), name='api_users_list'),
    path('api/users/paginated/', AdminUserPaginatedAPI.as_view(), name='api_users_paginated'),
    path('api/users/<int:pk>/', UpdateAdminUserWithLogging.as_view(), name='api_users_detail'),  # GET/PUT al mismo endpoint
    path('api/roles/', GetAdminRolesQuery.as_view(), name='api_roles'),
    
    # Commands (Acciones) - Ahora con logging
    path('api/users/create/', CreateAdminUserWithLogging.as_view(), name='api_users_create'),
    path('api/users/<int:pk>/delete/', DeleteAdminUserWithLogging.as_view(), name='api_users_delete'),
    
    # URLs de compatibilidad con las URLs originales - Ahora con logging
    path('usuarios/editar/<int:pk>/', UpdateAdminUserWithLogging.as_view(), name='editar_usuario'),
    path('usuarios/eliminar/', DeleteAdminUserWithLogging.as_view(), name='eliminar_usuario'),
    
    # LoginLog - Template View and API
    path('loginLog/', LoginLogTemplateView.as_view(), name='login_log_template'),
    path('api/loginLog/paginated/', GetLoginLogPaginatedQuery.as_view(), name='api_login_log_paginated'),
    
    # ActionLog - Template View and API
    path('actionLog/', ActionLogTemplateView.as_view(), name='action_log_template'),
    path('api/actionLog/paginated/', GetActionLogPaginatedQuery.as_view(), name='api_action_log_paginated'),
]