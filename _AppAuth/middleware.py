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
                return redirect(settings.LOGIN_URL)
            request.session["last_activity"] = now
            return self.get_response(request)

        return redirect(settings.LOGIN_URL)


'''
import time
from django.shortcuts import redirect
from django.contrib.auth import logout

class AuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # No interceptar rutas de Easy Auth, estáticos y lo que definas público
        exempt_prefixes = (
            "/.auth/",     # Endpoints de Easy Auth (login, logout, me)
            "/static/",
            "/health",
        )
        if request.path.startswith(exempt_prefixes):
            return self.get_response(request)

        # Inactividad (opcional)
        max_inactivity = 1200  # 20 min
        if getattr(request, "user", None) and request.user.is_authenticated:
            now = int(time.time())
            last = request.session.get("last_activity", now)
            if now - last > max_inactivity:
                logout(request)
                request.session.flush()
                return redirect('/.auth/login/aad?post_login_redirect_uri=/')
            request.session["last_activity"] = now
            return self.get_response(request)

        # Si NO está autenticado → manda al login de Easy Auth
        return redirect('/.auth/login/aad?post_login_redirect_uri=/')

'''

'''import time
from django.shortcuts import redirect
from django.contrib.auth import logout

class AuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        exempt_paths = {"/auth/login/", "/api/token/", "/AppMonitoreoCoriolis/api/node-red/", "/monitoreo/api/node-red/"}  # URLs públicas sin login
        max_inactivity = 1200  # segundos para cerrar sesión por inactividad

        if request.user.is_authenticated:
            current_time = int(time.time())
            last_activity = request.session.get("last_activity", current_time)

            if current_time - last_activity > max_inactivity:
                logout(request)
                request.session.flush()
                return redirect("login")

            request.session["last_activity"] = current_time

        elif request.path not in exempt_paths:
            return redirect("login")

        return self.get_response(request)
        '''
