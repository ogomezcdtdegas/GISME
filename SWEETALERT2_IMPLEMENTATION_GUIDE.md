# SweetAlert2 Utilidades Globales - Guía de Implementación

## 📋 Descripción

Este sistema proporciona utilidades globales de SweetAlert2 para uso consistente en todo el proyecto Django, especialmente para vistas que heredan de `ComplementosPermissionMixin`.

## 🎯 Objetivo Principal

Centralizar el manejo de alertas y modales para que todas las vistas que usan `ComplementosPermissionMixin` muestren mensajes elegantes y consistentes, especialmente para errores de permisos.

## 📁 Archivos Principales

### 1. `/config/static/js/sweetalert2-utils.js`
- **Propósito**: Utilidades globales de SweetAlert2
- **Funciones principales**:
  - `showSuccessAlert(message)`
  - `showErrorAlert(message)`
  - `showWarningAlert(message)`
  - `showPermissionDeniedAlert(message)`
  - `handleFetchResponse(response)`

### 2. `/config/templates/base.html`
- **Cambios**: Agregada referencia al script de utilidades
- **Ubicación**: Después de SweetAlert2 CDN, antes de scripts globales

## 🚀 Funciones Disponibles

### Alertas Básicas

```javascript
// Éxito
showSuccessAlert('Operación completada exitosamente');

// Error general
showErrorAlert('Ha ocurrido un error inesperado');

// Advertencia
showWarningAlert('Esta acción no se puede deshacer');

// Error de permisos (específico para ComplementosPermissionMixin)
showPermissionDeniedAlert('No tiene permisos para esta acción. Contacte al administrador.');
```

### Manejo Automático de Respuestas

```javascript
async function ejemplo() {
    try {
        const response = await fetch('/api/endpoint/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify(datos)
        });
        
        // Maneja automáticamente errores 403, 500, etc.
        const data = await handleFetchResponse(response);
        
        if (data.success) {
            showSuccessAlert(data.message);
        }
    } catch (error) {
        // Los errores ya fueron manejados por handleFetchResponse
        console.error('Error:', error);
    }
}
```

## 🔧 Implementación en Archivos Existentes

### Para JavaScript existente:

```javascript
// Opción 1: Reemplazar directamente
- mostrarError('mensaje') 
+ showErrorAlert('mensaje')

- mostrarExito('mensaje')
+ showSuccessAlert('mensaje')

- mostrarErrorPermisos('mensaje')
+ showPermissionDeniedAlert('mensaje')
```

```javascript
// Opción 2: Mantener compatibilidad
const mostrarExito = showSuccessAlert;
const mostrarError = showErrorAlert;
const mostrarErrorPermisos = showPermissionDeniedAlert;
```

### Para nuevos archivos:

```javascript
// Simplemente usar las funciones globales directamente
showSuccessAlert('Mensaje de éxito');
showErrorAlert('Mensaje de error');
```

## 🎨 Configuraciones Personalizadas

### Configuración Global (SWEET_CONFIG)

```javascript
const SWEET_CONFIG = {
    success: {
        icon: 'success',
        confirmButtonColor: '#28a745',
        timer: 3000,
        timerProgressBar: true
    },
    error: {
        icon: 'error',
        confirmButtonColor: '#dc3545'
    },
    warning: {
        icon: 'warning',
        confirmButtonColor: '#ffc107'
    },
    permission_denied: {
        icon: 'warning',
        title: 'Acceso Denegado',
        confirmButtonColor: '#ffc107',
        footer: '<small>Si necesita acceso, contacte al administrador del sistema</small>'
    }
};
```

## 🔒 Integración con ComplementosPermissionMixin

### Backend (_AppAdmin/mixins.py)
- ✅ Ya configurado para retornar mensajes de error apropiados
- ✅ Respuesta 403 con mensaje personalizable

### Frontend (Automático)
- ✅ `handleFetchResponse()` detecta automáticamente errores 403
- ✅ Muestra `showPermissionDeniedAlert()` automáticamente
- ✅ Consistente en todas las vistas que heredan el mixin

## 📋 Lista de Archivos Actualizados

### ✅ Completados:
1. `/config/static/js/sweetalert2-utils.js` - ✅ Creado
2. `/config/templates/base.html` - ✅ Script agregado
3. `/_AppMonitoreoCoriolis/templates/.../modal_configuracion.html` - ✅ Actualizado
4. `/_AppMonitoreoCoriolis/templates/.../coriolis_spa.html` - ✅ Actualizado

### 🔄 Pendientes por revisar:
- Otros archivos JavaScript con `alert()` nativo
- Templates con formularios que manejan permisos
- Archivos estáticos con funciones `mostrarError*`

## 🧪 Testing

### Casos de Prueba:
1. **Usuario con permisos**: Debería ver alertas de éxito/error normales
2. **Usuario sin permisos**: Debería ver alerta de "Acceso Denegado" automáticamente
3. **Error de conexión**: Debería ver alerta de error con mensaje apropiado
4. **Operación exitosa**: Debería ver alerta de éxito con auto-close

### URLs de Prueba:
- `/complementos/api/coeficientes/` (POST) - Requiere permisos de configuración
- `/complementos/api/sistemas/` (POST/PUT/DELETE) - Requiere permisos de administración
- `/complementos/api/ubicaciones/` (POST/PUT/DELETE) - Requiere permisos de administración

## 📖 Ejemplos de Uso

Ver archivo: `/config/static/js/sweetalert2-usage-examples.js`

## 🎯 Beneficios Obtenidos

1. **Consistencia**: Todas las alertas tienen el mismo estilo y comportamiento
2. **Mantenibilidad**: Un solo lugar para cambiar estilos de alertas
3. **Usabilidad**: Alertas más elegantes que `alert()` nativo
4. **Automatización**: Manejo automático de errores de permisos
5. **Escalabilidad**: Fácil de extender para nuevas funcionalidades

## 🔮 Futuras Mejoras

1. **Confirmaciones**: Agregar utilidades para confirmaciones antes de acciones destructivas
2. **Loading**: Integrar alertas de carga para operaciones largas
3. **Toast**: Notificaciones discretas para operaciones menores
4. **Theming**: Diferentes temas según el contexto (admin, monitoring, etc.)