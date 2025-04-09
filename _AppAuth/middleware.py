from django.shortcuts import redirect

class AuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated and request.path not in ["/auth/login/", "/api/token/"]:
            return redirect("login")  # Redirigir a login si no está autenticado
        return self.get_response(request)