from django.urls import path
from .views import login_view, logout_view, access_denied_production
from .views_aad_local import aad_login, aad_callback, aad_logout, access_denied

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    # URLs para Azure AD local
    path('aad/login/', aad_login, name='aad_login'),
    path('aad/callback/', aad_callback, name='aad_callback'),
    path('aad/logout/', aad_logout, name='aad_logout'),
    path('access-denied/', access_denied, name='access_denied'),
    path('access-denied-prod/', access_denied_production, name='access_denied_production'),
]