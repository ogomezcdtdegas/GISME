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
        username = oid or email
        user, _ = User.objects.get_or_create(username=username, defaults={"email": email or ""})
        request.user = user


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