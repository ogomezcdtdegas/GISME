# Configuración de Azure App Service para Logout Unificado

## Resumen
Este documento describe cómo configurar Azure App Service para que el logout funcione correctamente tanto en desarrollo (MSAL) como en producción (EasyAuth).

## Variables de Entorno Requeridas

### Desarrollo (MSAL)
```bash
USE_EASYAUTH=False
AZURE_TENANT_ID=87b3fb92-01b4-4639-9ff7-222b3de2ef1e
AZURE_CLIENT_ID=tu-client-id
AZURE_CLIENT_SECRET=tu-client-secret
```

### Producción (EasyAuth)
```bash
USE_EASYAUTH=True
AZURE_TENANT_ID=87b3fb92-01b4-4639-9ff7-222b3de2ef1e
```

## Configuración de Azure App Service

### 1. Variables de Entorno en Azure
En Azure Portal → Tu App Service → Configuration → Application settings:

```
USE_EASYAUTH = True
AZURE_TENANT_ID = 87b3fb92-01b4-4639-9ff7-222b3de2ef1e
```

### 2. Configuración de EasyAuth
En Azure Portal → Tu App Service → Authentication:

1. **Provider Configuration (Microsoft)**:
   - Tenant type: `Workforce`
   - Client ID: `tu-client-id`
   - Client secret: `tu-client-secret`
   - Allowed token audiences: `tu-client-id`

2. **App Service Authentication Settings**:
   - Unauthenticated requests: `Return HTTP 401 Unauthorized`
   - Token store: `Enabled`
   - Allow cookie authentication: `Enabled`

3. **URLs de Redirección Permitidas**:
   Agregar en Azure AD App Registration → Authentication → Redirect URIs:
   ```
   https://tu-app.azurewebsites.net/.auth/login/aad/callback
   https://tu-app.azurewebsites.net/auth/logout-complete/
   ```

4. **Logout URLs**:
   Agregar en Azure AD App Registration → Authentication → Logout URLs:
   ```
   https://tu-app.azurewebsites.net/auth/logout-complete/
   https://tu-app.azurewebsites.net/.auth/logout
   ```

## Flujo de Logout

### Desarrollo (MSAL)
1. Usuario hace clic en logout
2. `LogoutView` detecta `USE_EASYAUTH=False`
3. Limpia sesión Django
4. Redirige a `https://login.microsoftonline.com/{tenant}/oauth2/v2.0/logout`
5. Microsoft redirige a `/auth/logout-complete/`
6. `LogoutCompleteView` muestra página de confirmación

### Producción (EasyAuth)
1. Usuario hace clic en logout
2. `LogoutView` detecta `USE_EASYAUTH=True`
3. Limpia sesión Django
4. Redirige a `/.auth/logout?post_logout_redirect_uri=/auth/logout-complete/`
5. EasyAuth limpia tokens y redirige a Microsoft
6. Microsoft redirige de vuelta a `/auth/logout-complete/`
7. `LogoutCompleteView` muestra página de confirmación

## URLs Importantes

- **Logout unificado**: `/auth/logout/`
- **Logout completo**: `/auth/logout-complete/`
- **Login unificado**: `/auth/login/`

## Testing

### Desarrollo
```bash
# Verificar que USE_EASYAUTH=False
python manage.py shell
>>> import os
>>> os.getenv('USE_EASYAUTH')
'False'

# Probar logout
curl -X GET http://localhost:8000/auth/logout/
```

### Producción
```bash
# Verificar configuración
# En Azure Portal → App Service → Configuration
# Verificar que USE_EASYAUTH=True

# Probar logout
curl -X GET https://tu-app.azurewebsites.net/auth/logout/
```

## Troubleshooting

### Error: Logout no funciona en producción
1. Verificar que `USE_EASYAUTH=True` en Azure App Service
2. Verificar URLs de redirección en Azure AD
3. Verificar configuración de EasyAuth

### Error: Logout no funciona en desarrollo
1. Verificar que `USE_EASYAUTH=False` en variables locales
2. Verificar que `AZURE_TENANT_ID` está configurado
3. Verificar URLs de redirección en Azure AD para localhost

### Error: Loop infinito de redirección
1. Verificar que las URLs de logout en Azure AD son correctas
2. Verificar que no hay conflictos entre EasyAuth y middleware personalizado
3. Revisar logs de Django para errores de autenticación

## Archivos Modificados

- `_AppAuth/views_logout.py`: Vistas unificadas de logout
- `_AppAuth/urls.py`: URLs actualizadas para logout
- `_AppAuth/templates/_AppAuth/logout_complete.html`: Template de confirmación
- `config/urls.py`: URLs principales (sin cambios necesarios)

## Comandos de Deployment

```bash
# Desarrollar y probar localmente
python manage.py runserver

# Deploy a Azure
az webapp up --name tu-app --resource-group tu-rg

# Verificar configuración en Azure
az webapp config appsettings list --name tu-app --resource-group tu-rg
```
