# _AppAuth/views.py


from django.shortcuts import redirect, render
from django.contrib.auth import logout as dj_logout
from django.conf import settings

def login_view(request):
    return redirect(settings.LOGIN_URL)

def logout_view(request):
    dj_logout(request)
    return redirect(settings.LOGOUT_REDIRECT_URL)

def access_denied_production(request):
    """Vista para mostrar acceso denegado en producción cuando el usuario no está registrado o está inactivo"""
    # En producción, podemos intentar extraer el email del header si aún está disponible
    user_email = request.GET.get('email', 'Usuario autenticado')
    access_reason = request.GET.get('reason', 'not_registered')
    return render(request, "_AppAuth/access_denied.html", {
        "user_email": user_email,
        "access_reason": access_reason
    })


'''
from django.shortcuts import redirect
from django.contrib.auth import logout as dj_logout

def login_view(request):
    return redirect('/.auth/login/aad?post_login_redirect_uri=/')

def logout_view(request):
    dj_logout(request)  # limpia sesión de Django
    return redirect('/.auth/logout?post_logout_redirect_uri=/')
'''
'''
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("allEquiposPag")  # 🔹 Redirigir al home si el login es exitoso
        else:
            return render(request, "_AppAuth/login.html", {"error": "Credenciales incorrectas"})

    return render(request, "_AppAuth/login.html")


def logout_view(request):
    logout(request)  # 🔹 Cierra la sesión del usuario
    return redirect('login')  # 🔹 Redirige al login después de salir
    '''