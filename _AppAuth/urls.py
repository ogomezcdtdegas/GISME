from django.urls import path
from .views import login_view, logout_view, access_denied_production
from .views_aad_local import aad_login, aad_callback, aad_logout, access_denied
from .views_logout import LogoutView, LogoutCompleteView, LoginRedirectView

urlpatterns = [
    path('login/', LoginRedirectView.as_view(), name='login'),  # Nueva vista unificada de login
    path('django-login/', login_view, name='django_login'),  # Mantenemos la vista original
    path('logout/', LogoutView.as_view(), name='logout'),  # Nueva vista unificada de logout
    path('logout-complete/', LogoutCompleteView.as_view(), name='logout_complete'),
    path('legacy-logout/', logout_view, name='legacy_logout'),  # Mantenemos la vista original como fallback
    # URLs para Azure AD local
    path('aad/login/', aad_login, name='aad_login'),
    path('aad/callback/', aad_callback, name='aad_callback'),
    path('aad/logout/', aad_logout, name='aad_logout'),
    path('access-denied/', access_denied, name='access_denied'),
    path('access-denied-prod/', access_denied_production, name='access_denied_production'),
]