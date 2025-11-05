# Componentes de la Aplicación Monitoreo Coriolis

Este directorio contiene los componentes reutilizables de la aplicación de monitoreo Coriolis.

## Estructura de Componentes

### 📊 `modal_flujo.html` ✅ **ACTIVO**
**Propósito:** Modal para mostrar histórico de flujo volumétrico y másico
**IDs importantes:**
- `#historicoModal` - Modal principal
- `#graficaFlujoVolumetrico` - Canvas para gráfico volumétrico
- `#graficaFlujoMasico` - Canvas para gráfico másico
- `#fechaInicio`, `#fechaFin` - Controles de fecha
- `#modo-indicador` - Indicador del modo actual
- `#contador-volumetrico`, `#contador-masico` - Contadores de registros

**Uso:**
```django
{% include '_AppMonitoreoCoriolis/componentes/modal_flujo.html' %}
```

### 🗺️ `modal_mapa.html` ✅ **ACTIVO**
**Propósito:** Modal para mostrar la ubicación del sistema en un mapa interactivo
**IDs importantes:**
- `#mapModal` - Modal principal
- `#map` - Contenedor del mapa Leaflet
- `#modal-sistema-info` - Información del sistema
- `#modal-ubicacion-info` - Información de ubicación
- `#modal-coordenadas-info` - Coordenadas del sistema

**Uso:**
```django
{% include '_AppMonitoreoCoriolis/componentes/modal_mapa.html' %}
```

### 🌡️ `modal_temperatura.html` 🚧 **PREPARADO**
**Propósito:** Modal para mostrar histórico de temperatura
**IDs importantes:**
- `#temperaturaModal` - Modal principal
- `#graficaTemperatura` - Canvas para gráfico de temperatura
- `#fechaInicioTemperatura`, `#fechaFinTemperatura` - Controles de fecha
- `#modo-indicador-temperatura` - Indicador del modo actual
- `#contador-temperatura` - Contador de registros

**Uso:**
```django
{% include '_AppMonitoreoCoriolis/componentes/modal_temperatura.html' %}
```

### 📊 `modal_presion.html` 🚧 **PREPARADO**
**Propósito:** Modal para mostrar histórico de presión
**IDs importantes:**
- `#presionModal` - Modal principal
- `#graficaPresion` - Canvas para gráfico de presión
- `#fechaInicioPresion`, `#fechaFinPresion` - Controles de fecha
- `#modo-indicador-presion` - Indicador del modo actual
- `#contador-presion` - Contador de registros

**Uso:**
```django
{% include '_AppMonitoreoCoriolis/componentes/modal_presion.html' %}
```

## Futuros Componentes

Componentes que se pueden agregar en el futuro:
- `modal_configuracion.html` - Modal para configuración del sistema
- `card_sensor.html` - Componente de card para sensores individuales
- `panel_estado.html` - Panel de estado del sistema
- `loading_overlay.html` - Overlay de carga reutilizable
- `modal_alertas.html` - Modal para gestión de alertas
- `panel_estadisticas.html` - Panel de estadísticas del sistema

## Ventajas de esta Estructura

1. **Reutilización:** Los componentes pueden usarse en múltiples vistas
2. **Mantenibilidad:** Cambios centralizados en un solo archivo
3. **Organización:** Separación clara de responsabilidades
4. **Escalabilidad:** Fácil agregar nuevos componentes
5. **Testing:** Componentes pueden ser probados por separado

## Convenciones de Nomenclatura

- **Archivos:** `modal_[nombre].html`, `card_[nombre].html`, `panel_[nombre].html`
- **IDs:** Usar nombres descriptivos y únicos para evitar conflictos
- **Clases:** Seguir convenciones de Bootstrap y CSS personalizados
- **Comentarios:** Incluir header con propósito y uso del componente
- **⚠️ IMPORTANTE:** En comentarios HTML, usar `{percent ... percent}` en lugar de `{% ... %}` para evitar que Django interprete las directivas como código real