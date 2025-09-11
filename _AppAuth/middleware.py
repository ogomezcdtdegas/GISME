# _AppAuth/middleware.py

# _AppAuth/middleware.py
import time
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.conf import settings

class AuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        exempt_prefixes = ("/.auth/", "/static/", "/health", "/aad/", "/auth/access-denied")  
        if request.path.startswith(exempt_prefixes):
            return self.get_response(request)

        # Verificar si el usuario está autenticado pero no registrado
        if request.session.get('user_not_registered'):
            email = request.session.get('unregistered_user_email', 'Usuario autenticado')
            # Limpiar la sesión para evitar bucles
            request.session.pop('user_not_registered', None)
            request.session.pop('unregistered_user_email', None)
            return redirect(f'/auth/access-denied-prod/?email={email}')

        max_inactivity = 1200
        if getattr(request, "user", None) and request.user.is_authenticated:
            now = int(time.time())
            last = request.session.get("last_activity", now)
            if now - last > max_inactivity:
                logout(request)
                request.session.flush()
                return redirect('/aad/login?post_login_redirect_uri=/')
            request.session["last_activity"] = now
            return self.get_response(request)

        # Si NO está autenticado → manda al login de MSAL
        return redirect('/aad/login?post_login_redirect_uri=/')
