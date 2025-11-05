# _AppAuth/middleware_easyauth.py

import os, base64, json, logging
from django.contrib.auth import get_user_model
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

log = logging.getLogger(__name__)

EMAIL_CLAIMS = [
    "preferred_username",
    "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress",
    "upn", "name", "emails",
]
OID_CLAIM = "http://schemas.microsoft.com/identity/claims/objectidentifier"
TID_CLAIM = "http://schemas.microsoft.com/identity/claims/tenantid"

class EasyAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Para rutas de Node-RED, intentar Basic Auth primero
        if '/monitoreo/api/node-red/' in request.path:
            return self._handle_node_red_auth(request)
        
        # Para otras rutas, continuar con EasyAuth normal
        return self._handle_easyauth(request)
    
    def _handle_node_red_auth(self, request):
        """Maneja autenticación específica para Node-RED usando Basic Auth con variables de entorno"""
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        
        if not auth_header or not auth_header.startswith('Basic '):
            log.warning("Acceso denegado a Node-RED: Sin header Basic Auth")
            return
            
        try:
            # Decodificar credenciales del header
            encoded_credentials = auth_header.split(' ')[1]
            decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
            username, password = decoded_credentials.split(':', 1)
            
            # Obtener credenciales de variables de entorno
            node_red_user = os.environ.get('NODE_RED_USER')
            node_red_pass = os.environ.get('NODE_RED_PASS')
            
            if not node_red_user or not node_red_pass:
                log.error("Variables de entorno NODE_RED_USER o NODE_RED_PASS no configuradas")
                return
            
            # Verificar credenciales
            if username == node_red_user and password == node_red_pass:
                # Buscar un usuario admin en la base de datos para asignar
                User = get_user_model()
                try:
                    # Buscar un usuario con rol admin_principal para Node-RED
                    admin_user = User.objects.filter(
                        user_role__role='admin_principal'
                    ).first()
                    
                    if admin_user:
                        request.user = admin_user
                        log.info(f"Usuario Node-RED autenticado exitosamente como: {admin_user.email}")
                        return
                    else:
                        # Si no hay admin_principal, buscar cualquier admin
                        admin_user = User.objects.filter(
                            user_role__role='admin'
                        ).first()
                        
                        if admin_user:
                            request.user = admin_user
                            log.info(f"Usuario Node-RED autenticado como admin: {admin_user.email}")
                            return
                        else:
                            log.error("No se encontró usuario administrador para Node-RED")
                            return
                            
                except Exception as e:
                    log.error(f"Error buscando usuario admin para Node-RED: {e}")
                    return
            else:
                log.warning(f"Credenciales Node-RED inválidas para usuario: {username}")
                return
                
        except Exception as e:
            log.error(f"Error decodificando Basic Auth para Node-RED: {e}")
            return
    
    def _handle_easyauth(self, request):
        """Maneja autenticación normal de EasyAuth"""
        # Header real en Azure, sesión en local (llenada por MSAL)
        b64 = request.META.get("HTTP_X_MS_CLIENT_PRINCIPAL") if settings.USE_EASYAUTH else request.session.get("X_MS_CLIENT_PRINCIPAL")
        if not b64:
            return

        try:
            data = json.loads(base64.b64decode(b64))
            claims = {c["typ"]: c["val"] for c in data.get("claims", [])}
        except Exception as e:
            log.warning("EasyAuth principal inválido: %s", e)
            return

        raw_tenants = os.environ.get("ALLOWED_TENANTS", "").strip()
        if raw_tenants:
            allowed = {t.strip() for t in raw_tenants.split(",") if t.strip()}
            if claims.get(TID_CLAIM) not in allowed:
                return

        oid = claims.get(OID_CLAIM)
        email = next((claims.get(k) for k in EMAIL_CLAIMS if claims.get(k)), None)
        if not (oid or email):
            return

        User = get_user_model()
        
        # Verificar si el usuario está registrado en la plataforma (solo por email)
        user = User.objects.filter(email=email).first()
        if user:
            # Usuario existe en la BD, asignar a request
            request.user = user
        else:
            # Usuario no está registrado, marcar en sesión para manejo posterior
            request.session['unregistered_user_email'] = email
            request.session['user_not_registered'] = True
            # No asignar user (permanece anónimo)
            return


'''
import os
import base64
import json
import logging
from django.contrib.auth import get_user_model
from django.utils.deprecation import MiddlewareMixin

log = logging.getLogger(__name__)

# Claims posibles donde viene el UPN/email
EMAIL_CLAIMS = [
    "preferred_username",
    "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress",
    "upn", "name", "emails",
]
OID_CLAIM = "http://schemas.microsoft.com/identity/claims/objectidentifier"
TID_CLAIM = "http://schemas.microsoft.com/identity/claims/tenantid"  # por si quieres autorizar por tenant

class EasyAuthMiddleware(MiddlewareMixin):
    """
    Poblamos request.user leyendo los headers que inyecta Azure App Service (Easy Auth).
    - X-MS-CLIENT-PRINCIPAL: JSON base64 con claims del usuario.
    """
    def process_request(self, request):
        b64 = request.META.get("HTTP_X_MS_CLIENT_PRINCIPAL")
        if not b64:
            return  # anónimo (Easy Auth no autenticó)

        try:
            data = json.loads(base64.b64decode(b64))
            claims = {c["typ"]: c["val"] for c in data.get("claims", [])}
        except Exception as e:
            log.warning("EasyAuth: no pude decodificar X-MS-CLIENT-PRINCIPAL: %s", e)
            return

        oid = claims.get(OID_CLAIM)
        email = next((claims.get(k) for k in EMAIL_CLAIMS if claims.get(k)), None)

        if not (oid or email):
            # No tenemos identificador confiable → tratar como anónimo
            return

        # (Opcional) Forzar que solo entre un tenant específico (reemplaza por el que uses)
        allowed_tenants = set(os.environ.get("ALLOWED_TENANTS", "").split(","))
        if claims.get(TID_CLAIM) not in allowed_tenants:
            return

        User = get_user_model()
        username = oid or email  # usa el OID si existe; estable en el tiempo
        user, _ = User.objects.get_or_create(
            username=username,
            defaults={"email": email or ""}
        )

        # (Opcional) mapear roles/grupos a permisos de Django:
        # roles = claims.get("roles")
        # groups = claims.get("groups")
        # if roles and "admin" in roles:
        #     if not user.is_staff:
        #         user.is_staff = True
        #         user.save(update_fields=["is_staff"])

        request.user = user
'''