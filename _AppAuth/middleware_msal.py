# _AppAuth/middleware_msal.py

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

class MSALAuthMiddleware(MiddlewareMixin):
    """
    Middleware unificado para autenticación MSAL que maneja:
    1. Autenticación Azure AD via MSAL (desarrollo y producción)
    2. Autenticación especial para Node-RED con Basic Auth
    """
    
    def process_request(self, request):
        # Para rutas de Node-RED, intentar Basic Auth primero
        if '/monitoreo/api/node-red/' in request.path:
            return self._handle_node_red_auth(request)
        
        # Para otras rutas, continuar con MSAL auth
        return self._handle_msal_auth(request)
    
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
    
    def _handle_msal_auth(self, request):
        """Maneja autenticación MSAL - Lee datos de la sesión que son guardados por views_aad_local.py"""
        # Los datos MSAL se guardan en la sesión durante el callback de MSAL
        b64 = request.session.get("X_MS_CLIENT_PRINCIPAL")
        if not b64:
            return

        try:
            data = json.loads(base64.b64decode(b64))
            claims = {c["typ"]: c["val"] for c in data.get("claims", [])}
        except Exception as e:
            log.warning("MSAL principal inválido: %s", e)
            return

        # Validar tenant
        tid = claims.get(TID_CLAIM)
        if hasattr(settings, 'AZURE_TENANT_ID') and tid != settings.AZURE_TENANT_ID:
            log.warning("Tenant ID no coincide: esperado %s, recibido %s", 
                       settings.AZURE_TENANT_ID, tid)
            return

        # Encontrar email del usuario
        email = None
        for email_claim in EMAIL_CLAIMS:
            if email_claim in claims:
                email = claims[email_claim]
                break

        if not email:
            log.warning("No se encontró email en claims MSAL: %s", list(claims.keys()))
            return

        # Obtener o crear usuario
        User = get_user_model()
        try:
            user = User.objects.get(email__iexact=email)
            request.user = user
            log.debug("Usuario MSAL autenticado: %s", email)
        except User.DoesNotExist:
            # Usuario autenticado en Azure AD pero no registrado en la plataforma
            # Marcar en sesión para que AuthMiddleware redirija a acceso denegado
            request.session['user_not_registered'] = True
            request.session['unregistered_user_email'] = email
            log.info("Usuario %s autenticado en Azure AD pero no registrado en la plataforma", email)
        except Exception as e:
            log.error("Error obteniendo usuario MSAL %s: %s", email, e)
