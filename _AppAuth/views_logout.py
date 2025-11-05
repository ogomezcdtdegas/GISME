from django.shortcuts import redirect, render
from django.contrib.auth import logout
from django.contrib import messages
from django.conf import settings
from django.views import View
from django.http import HttpResponse
import os
import logging

log = logging.getLogger(__name__)

class LogoutView(View):
    """
    Vista de logout unificada que usa MSAL para todos los entornos
    """
    
    def get(self, request):
        return self.handle_logout(request)
    
    def post(self, request):
        return self.handle_logout(request)
    
    def handle_logout(self, request):
        """Maneja logout usando MSAL para todos los entornos"""
        
        # Logout de Django (siempre)
        if request.user.is_authenticated:
            user_email = getattr(request.user, 'email', 'Usuario anónimo')
            logout(request)
            log.info(f"Usuario {user_email} cerró sesión")
        
        # Limpiar sesión Django
        request.session.flush()
        
        # Usar logout de MSAL para todos los entornos
        return self._msal_logout(request)
    
    def _msal_logout(self, request):
        """Logout usando MSAL para todos los entornos"""
        
        # Construir URL de logout de Microsoft
        tenant_id = os.getenv('AZURE_TENANT_ID')
        post_logout_uri = request.build_absolute_uri('/auth/logout-complete/')
        logout_url = (
            f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/logout"
            f"?post_logout_redirect_uri={post_logout_uri}"
        )
        
        log.info("Redirigiendo a logout de MSAL")
        return redirect(logout_url)


class LogoutCompleteView(View):
    """Vista que se ejecuta después del logout completo"""
    
    def get(self, request):
        # Asegurar que la sesión esté completamente limpia
        request.session.flush()
        
        # Mostrar página de confirmación de logout
        return render(request, '_AppAuth/logout_complete.html')
    
    def post(self, request):
        return self.get(request)


class LoginRedirectView(View):
    """Vista para manejar redirecciones de login"""
    
    def get(self, request):
        # Siempre usar MSAL - rutas directas que coinciden con Azure AD
        return redirect('/aad/login')
