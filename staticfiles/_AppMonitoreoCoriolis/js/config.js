// ====================================================================
// CONFIG.JS - Configuración global y variables del sistema
// ====================================================================

// =====================================================
// CONFIGURACIÓN DE TIEMPOS Y PERÍODOS (FÁCIL DE MODIFICAR)
// =====================================================
const CONFIG = {
    // Configuración de intervalos de actualización (en milisegundos)
    INTERVALOS: {
        ACTUALIZACION_DISPLAYS: 10000,      // 10 segundos para actualizar displays de sensores
        ACTUALIZACION_GRAFICOS: 10000,      // 10 segundos para actualizar gráficos en modo tiempo real
    },
    
    // Configuración de períodos por defecto
    PERIODOS: {
        DIAS_POR_DEFECTO: 1,                // Días hacia atrás para mostrar por defecto (últimos 3 días)
    },
    
    // Configuración de gráficos
    GRAFICOS: {
        FLUJO_VOLUMETRICO: {
            color: '#007bff',
            colorFondo: 'rgba(0, 123, 255, 0.1)',
            label: 'Flujo Volumétrico',
            canvasId: 'graficaFlujoVolumetrico'
        },
        FLUJO_MASICO: {
            color: '#28a745', 
            colorFondo: 'rgba(40, 167, 69, 0.1)',
            label: 'Flujo Másico',
            canvasId: 'graficaFlujoMasico'
        },
        PRESION: {
            color: '#dc3545',
            colorFondo: 'rgba(220, 53, 69, 0.1)',
            label: 'Presión',
            canvasId: 'graficaPresion'
        }
    },
    
    // Textos dinámicos que se calculan automáticamente basados en la configuración
    TEXTOS: {
        get MODO_TIEMPO_REAL() {
            const segundos = Math.floor(CONFIG.INTERVALOS.ACTUALIZACION_GRAFICOS / 1000);
            const dias = CONFIG.PERIODOS.DIAS_POR_DEFECTO;
            return `Los gráficos se actualizan automáticamente cada ${segundos} segundos mostrando los últimos ${dias} días.`;
        },
        get INFO_PERIODO_TIEMPO_REAL() {
            const dias = CONFIG.PERIODOS.DIAS_POR_DEFECTO;
            return `Últimos ${dias} días - Se actualiza automáticamente`;
        },
        REGISTROS_TIEMPO_REAL_VOLUMETRICO: (total) => {
            const dias = CONFIG.PERIODOS.DIAS_POR_DEFECTO;
            return `${total} registros (Últimos ${dias} días - Actualizando)`;
        },
        REGISTROS_TIEMPO_REAL_MASICO: (total) => {
            const dias = CONFIG.PERIODOS.DIAS_POR_DEFECTO;
            return `${total} registros (Últimos ${dias} días - Actualizando)`;
        },
        REGISTROS_TIEMPO_REAL_PRESION: (total) => {
            const dias = CONFIG.PERIODOS.DIAS_POR_DEFECTO;
            return `${total} registros (Últimos ${dias} días - Actualizando)`;
        },
        get CONSOLE_ACTUALIZACION() {
            const segundos = Math.floor(CONFIG.INTERVALOS.ACTUALIZACION_DISPLAYS / 1000);
            return `⏰ Actualización automática configurada cada ${segundos} segundos`;
        },
        get CONSOLE_MODO_TIEMPO_REAL() {
            const segundos = Math.floor(CONFIG.INTERVALOS.ACTUALIZACION_GRAFICOS / 1000);
            return `✅ Modo tiempo real iniciado - se actualiza cada ${segundos} segundos`;
        }
    }
};

// Variables globales para controlar los gráficos
let sistemaActual = null;
let chartFlujoVolumetrico = null;
let chartFlujoMasico = null;
let chartPresion = null;
let tiempoRealInterval = null;

// Variables para controlar el modo de los gráficos
let modoTiempoReal = true; // true = últimos N días actualizándose, false = filtrado estático
let intervalActualizacionGraficos = null;

// Variables para controlar presión
let modoTiempoRealPresion = true;
let intervalActualizacionPresion = null;

// Variables del sistema desde Django - Se inicializan desde el HTML template
// let SISTEMA_ACTUAL; // Ya se define en el HTML template