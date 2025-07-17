import time
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
