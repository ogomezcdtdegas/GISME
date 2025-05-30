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