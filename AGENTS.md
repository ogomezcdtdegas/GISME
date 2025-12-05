# GISME: Metrological System Management Platform

GISME (Gestión Integral de un Sistema Metrológico) is a Django-based web platform for managing gas laboratory metrological systems, specifically focused on Coriolis flowmeter monitoring and batch detection for gas custody transfer operations.

## Architecture Overview

### App Structure (Modular Django Apps)

The project follows a modular app-based architecture with clear separation of concerns:

- **`_AppMonitoreoCoriolis`**: Core monitoring app for Coriolis flowmeter data (IoT ingestion, batch detection, reporting)
- **`_AppComplementos`**: Supporting entities (locations, systems, configurations)
- **`_AppAdmin`**: User administration, roles, and audit logging
- **`_AppAuth`**: Authentication (Azure AD MSAL integration with dual deployment modes)
- **`_AppHome`**: Landing pages and dashboards
- **`_AppCommon`**: Shared models and utilities (e.g., `BaseModel` with UUID primary keys)

All custom apps use `_App` prefix to distinguish from third-party Django apps.

### CQRS-Style Organization

Views are organized using command/query separation:

```
_AppMonitoreoCoriolis/
├── views/
│   ├── commands/    # Write operations (create, update, delete)
│   ├── queries/     # Read operations (list, detail, reports)
│   ├── templates/   # View-specific templates
│   └── utils.py     # Shared view utilities
```

**Pattern**: Import handlers from `views/__init__.py` to expose them at the app level. This keeps URL routing clean while maintaining internal organization.

### Data Models

**UUID Primary Keys**: All models inherit from `_AppCommon.models.BaseModel`, which provides:
- `id = UUIDField(primary_key=True, default=uuid.uuid4)` 
- `created_at = DateTimeField(auto_now_add=True)`

This pattern ensures globally unique identifiers across distributed systems and avoids sequential ID enumeration attacks.

**Example**: `NodeRedData` model stores IoT telemetry from Coriolis flowmeters with ForeignKey to `Sistema` (system configuration). Key fields include flow rates, density, temperature, pressure, and calibration coefficients copied at insert time for historical accuracy.

## Authentication & Authorization

### Dual Deployment Modes

The app supports two authentication modes controlled by `USE_EASYAUTH` environment variable:

1. **Azure EasyAuth Mode** (`USE_EASYAUTH=True`): For Azure App Service deployment using built-in Azure AD authentication
   - Login: `/.auth/login/aad?prompt=login&post_login_redirect_uri=/`
   - Handled by Azure infrastructure before reaching Django

2. **Local MSAL Mode** (`USE_EASYAUTH=False`): For local development or non-Azure hosting
   - Login: `/aad/login` (handled by `_AppAuth.views_aad_local`)
   - Uses MSAL Python library to interact with Azure AD directly

**Configuration**: All Azure AD settings (`AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`, `AZURE_REDIRECT_URI`) are loaded from environment variables via `.env` file.

### Custom Middleware Stack

Three critical custom middlewares (order matters):

1. **`MSALAuthMiddleware`** (_AppAuth/middleware_msal.py): Processes Azure AD tokens and creates/updates Django User objects
2. **`AuthMiddleware`** (_AppAuth/middleware.py): 
   - Enforces authentication on all non-exempt paths
   - Implements 20-minute inactivity timeout (1200 seconds)
   - Redirects unauthenticated users or inactive accounts
3. **`CacheControlMiddleware`**: Prevents browser caching of sensitive authenticated pages

### Role-Based Permissions

Custom permission mixins in `_AppAdmin/mixins.py`:

- **`AdminPermissionMixin`**: Restricts user management to `admin` and `admin_principal` roles
  - `admin_principal`: Full CRUD on users
  - `admin`: Read-only access
  
- **`ComplementosPermissionMixin`**: Restricts location/system management to admin roles

- **`SuperuserPermissionMixin`**: Enforces superuser-only for critical deletions

**Pattern**: Mixins override `dispatch()` to check permissions before view execution. They return appropriate JSON responses for API calls or redirect to home for template views.

### Audit Logging

`ActionLogMixin` and `UniversalActionLogMixin` provide automatic logging:

```python
class CreateUbicacionView(UniversalActionLogMixin, CreateAPIView):
    log_config = {
        'affected_type': 'ubicacion',
        'get_value': lambda obj: obj.nombre,
        'model_class': Ubicacion,
    }
```

Logs user actions (create/edit/delete) with IP address, timestamp, and affected object details to `_AppAdmin.models.UserActionLog`.

## Gas Industry Utilities

### UTIL_LIB Package

Domain-specific calculation modules:

- **`conversiones.py`**: Unit conversions for gas metering (lb/s ↔ kg/min, cm³/s ↔ gal/min, g/cm³ ↔ kg/m³, °C ↔ °F)
- **`densidad60Modelo.py`**: Density calculations at standard conditions (60°F)
- **`GUM_coriolis_simp.py`**: Uncertainty calculations following GUM methodology for Coriolis measurements

**Integration**: These are imported directly into views for real-time calculations and API responses.

## Key Development Workflows

### Running the Development Server

```bash
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Run Django dev server (uses config.settings.development by default)
python manage.py runserver
```

**Note**: `manage.py` defaults to `config.settings.development`. For production, set `DJANGO_SETTINGS_MODULE=config.settings.production`.

### Database Migrations

```bash
# Create migrations for app changes
python manage.py makemigrations _AppMonitoreoCoriolis

# Apply migrations
python manage.py migrate
```

All apps use PostgreSQL (`psycopg2-binary`) in production. Connection details come from environment variables.

### Static Files

Static files use WhiteNoise for production serving. Configuration in `config/settings/base.py`:

```python
STATICFILES_DIRS = [
    BASE_DIR / 'static',           # Global static files
    BASE_DIR / 'config/static'     # Config-specific static files
]
```

Each app also has its own `static/` directory for app-specific assets (JS, CSS, images).

### API Documentation

The project uses `drf-spectacular` for OpenAPI schema generation:

- Schema endpoint: `/api/schema/`
- Interactive docs: `/api/docs/` (Swagger UI)

Add `@extend_schema()` decorators to DRF views for automatic API documentation.

## Security Configuration

The project implements multiple security layers (see `config/settings/base.py`):

### Session & CSRF Protection

- **Session timeout**: 20 minutes with auto-renewal on each request (`SESSION_SAVE_EVERY_REQUEST=True`)
- **CSRF protection**: `CSRF_COOKIE_HTTPONLY=False` to allow AJAX requests with CSRF tokens
  - Token name: `csrftoken` (fetch from cookies in JavaScript)
  - Same-site policy: `Lax` for both session and CSRF cookies

### Headers

- `X_FRAME_OPTIONS = 'DENY'`: Prevents clickjacking
- `SECURE_CONTENT_TYPE_NOSNIFF = True`: Prevents MIME sniffing
- `SECURE_REFERRER_POLICY = 'same-origin'`: Limits referer leakage
- Custom `Server: Kernel` header to obscure server details

## Frontend Integration

### JavaScript Modules

Coriolis monitoring uses vanilla JavaScript with modular organization:

- **`coriolis-common.js`**: Shared utilities (CSRF token handling, API calls, formatters)
- **`coriolis-spa.js`**: Single-page app logic for real-time monitoring
- **`coriolis-map.js`**: Leaflet-based visualization of system locations

**AJAX Pattern**: All API calls include CSRF token from cookie:

```javascript
fetch('/api/endpoint/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify(data)
})
```

## External Dependencies

### Gas Industry Libraries

- **`pyaga8`**: AGA8 equation of state for natural gas density calculations
- **`pvtlib`**: PVT (Pressure-Volume-Temperature) properties for hydrocarbons
- **`metrolopy`**: Uncertainty propagation for metrological calculations

### Scientific Stack

- **`numpy`**, **`pandas`**: Data processing for batch analysis
- **`matplotlib`**: Chart generation for reports
- **`scipy`**: Statistical analysis

### Reporting

- **`reportlab`**: PDF generation for custody transfer certificates

## Project Conventions

1. **Environment Variables**: All secrets and deployment-specific config in `.env` file (never committed)
2. **Model Naming**: Models use singular Spanish names (`Sistema`, `Ubicacion`, `BatchDetectado`)
3. **URL Patterns**: Apps use namespaced URLs (e.g., `monitoreo:sistema-detail`)
4. **Templates**: Each app has `templates/_App{Name}/` subdirectory matching app name
5. **Error Handling**: Views return JSON `{'success': bool, 'error': str}` for API calls, redirect for template views

## Testing

Currently no automated tests exist in the codebase. When adding tests:

- Use Django's `TestCase` or `APITestCase` from DRF
- Place tests in `tests.py` within each app
- Run with: `python manage.py test _AppMonitoreoCoriolis`

## Common Pitfalls

1. **Middleware Order**: Custom auth middleware must come after `SessionMiddleware` and `AuthenticationMiddleware`
2. **UUID Fields**: When filtering by ID, ensure you're passing UUID objects or strings, not integers
3. **CSRF Exemption**: Never exempt views from CSRF unless they're truly public APIs with other auth (e.g., Node-RED with bearer token)
4. **Time Zones**: Database stores UTC (`USE_TZ=True`), convert to local time in templates/APIs as needed
5. **Static Files**: After adding new static files in development, restart server or use `collectstatic` for production
