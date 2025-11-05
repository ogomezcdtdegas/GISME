import base64, json, time
from django.conf import settings
from django.contrib.auth import get_user_model, login as dj_login, logout as dj_logout
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from .msal_client import auth_url, acquire_token_by_auth_code
from .models import UserLoginLog

def _get_client_ip(request):
    """Obtener la IP del cliente considerando proxies"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = (x_forwarded_for.split(',')[0].strip()).split(':')[0]
        print(ip)
    else:
        ip = request.META.get('REMOTE_ADDR', 'Unknown')
    return ip

def _to_client_principal(id_token_claims: dict) -> dict:
    claims = []
    for k, v in id_token_claims.items():
        if isinstance(v, (list, tuple)): v = ",".join(v)
        claims.append({"typ": k, "val": str(v)})
    return {"auth_typ": "aad", "name_typ": "name", "role_typ": "roles", "claims": claims}

def aad_login(request):
    state = str(int(time.time()))
    request.session["aad_state"] = state
    return redirect(auth_url(state))

@csrf_exempt  # usamos response_mode=form_post
def aad_callback(request):
    state = request.POST.get("state") or request.GET.get("state")
    code  = request.POST.get("code")  or request.GET.get("code")
    if not code or state != request.session.get("aad_state"):
        return render(request, "_AppAuth/aad_error.html", {"msg": "State o code inválidos"})

    result = acquire_token_by_auth_code(code)
    if "id_token_claims" not in result:
        return render(request, "_AppAuth/aad_error.html", {"msg": result.get('error_description', 'Error AAD')})

    claims = result["id_token_claims"]
    principal = _to_client_principal(claims)
    b64 = base64.b64encode(json.dumps(principal).encode()).decode()
    request.session["X_MS_CLIENT_PRINCIPAL"] = b64  # lo leerá el middleware

    # crea/inicia usuario Django
    User = get_user_model()
    email = claims.get("preferred_username") or claims.get("email") or claims.get("upn")
    username = claims.get("oid") or email
    
    # Verificar si el usuario está registrado en la plataforma
    user = User.objects.filter(email=email).first()
    if user:
        # Verificar si el usuario está activo
        if not user.is_active:
            # Usuario existe pero está inactivo
            return render(request, "_AppAuth/access_denied.html", {
                "user_email": email,
                "access_reason": "inactive"
            })
        
        # Usuario existe y está activo, proceder con login
        dj_login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        
        # Registrar el login exitoso
        try:
            ip_address = _get_client_ip(request)
            UserLoginLog.objects.create(
                user=user,
                email=email,
                ip_address=ip_address
            )
        except Exception as e:
            # No fallar el login si hay error guardando el log
            print(f"Error guardando log de login: {e}")
        
        return redirect("/")
    else:
        # Usuario no está registrado en la plataforma
        return render(request, "_AppAuth/access_denied.html", {
            "user_email": email,
            "access_reason": "not_registered"
        })

def aad_logout(request):
    dj_logout(request)
    return redirect("/")

def access_denied(request):
    """Vista para mostrar acceso denegado cuando el usuario no está registrado o está inactivo"""
    user_email = request.GET.get('email', 'No disponible')
    access_reason = request.GET.get('reason', 'not_registered')
    return render(request, "_AppAuth/access_denied.html", {
        "user_email": user_email,
        "access_reason": access_reason
    })
