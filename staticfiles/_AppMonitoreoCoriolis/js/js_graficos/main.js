// ====================================================================
// MAIN.JS - Inicialización principal y control de vistas
// ====================================================================

// Variables globales adicionales para tendencias
let tendenciasInterval = null;

// Función para abrir modal de flujo (sensor1) con dos gráficos REALES
async function abrirModal(sensorId) {
    const sistemaId = obtenerSistemaActual();
    if (!sistemaId) {
        alert('Error: No se pudo identificar el sistema actual.\n\nVerifique que:\n1. Está accediendo desde un sistema específico\n2. El sistema existe en la base de datos\n3. La URL contiene el ID del sistema');
        return;
    }

    if (sensorId === 'sensor1') {
        // Modal de flujo (volumétrico y másico)
        // Configurar fechas en los campos (solo referencia visual para búsqueda manual)
        const fechaFin = new Date();
        const fechaInicio = new Date(fechaFin.getTime() - (1 * 60 * 60 * 1000)); // 1 hora atrás
        
        document.getElementById('fechaInicio').value = fechaInicio.toISOString().slice(0, 16);
        document.getElementById('fechaFin').value = fechaFin.toISOString().slice(0, 16);
        
        // Iniciar en modo tiempo real por defecto
        inicializarModoTiempoReal();
        
        // Mostrar modal de flujo
        var modal = new bootstrap.Modal(document.getElementById('historicoModal'));
        modal.show();
        
        // Configurar eventos del modal
        configurarEventosModal();
        
        //console.log(`✅ Modal de flujo abierto para sistema: ${sistemaId}`);
        
    } else if (sensorId === 'sensor3') {
        // Modal de presión
        abrirModalPresion();
        
    } else if (sensorId === 'sensor2') {
        // Modal de temperatura
        abrirModalTemperatura();
        
    } else {
        // Sensor no implementado
        alert(`Funcionalidad para ${sensorId} en desarrollo.\nActualmente disponibles: Flujo (sensor1), Temperatura (sensor2) y Presión (sensor3).`);
        return;
    }
}

// Función para abrir modal de presión (sensor3)
async function abrirModalPresion() {
    const sistemaId = obtenerSistemaActual();
    if (!sistemaId) {
        alert('Error: No se pudo identificar el sistema actual.');
        return;
    }
    
    // Configurar fechas en los campos (solo referencia visual para búsqueda manual)
    const fechaFin = new Date();
    const fechaInicio = new Date(fechaFin.getTime() - (1 * 60 * 60 * 1000)); // 1 hora atrás
    
    document.getElementById('fechaInicioPresion').value = fechaInicio.toISOString().slice(0, 16);
    document.getElementById('fechaFinPresion').value = fechaFin.toISOString().slice(0, 16);
    
    // Iniciar en modo tiempo real por defecto
    inicializarModoTiempoRealPresion();
    
    // Mostrar modal de presión
    var modal = new bootstrap.Modal(document.getElementById('presionModal'));
    modal.show();
    
    // Configurar eventos del modal
    configurarEventosModalPresion();
    
    //console.log(`✅ Modal de presión abierto para sistema: ${sistemaId}`);
}

// Función para abrir modal de temperatura (sensor2)
async function abrirModalTemperatura() {
    const sistemaId = obtenerSistemaActual();
    if (!sistemaId) {
        alert('Error: No se pudo identificar el sistema actual.');
        return;
    }
    
    // Configurar fechas en los campos (solo referencia visual para búsqueda manual)
    const fechaFin = new Date();
    const fechaInicio = new Date(fechaFin.getTime() - (1 * 60 * 60 * 1000)); // 1 hora atrás
    
    document.getElementById('fechaInicioTemperatura').value = fechaInicio.toISOString().slice(0, 16);
    document.getElementById('fechaFinTemperatura').value = fechaFin.toISOString().slice(0, 16);
    
    // Iniciar en modo tiempo real por defecto
    inicializarModoTiempoRealTemperatura();
    
    // Mostrar modal de temperatura
    var modal = new bootstrap.Modal(document.getElementById('temperaturaModal'));
    modal.show();
    
    // Configurar eventos del modal
    configurarEventosModalTemperatura();
    
    //console.log(`✅ Modal de temperatura abierto para sistema: ${sistemaId}`);
}

// Función para mostrar la vista de monitoreo
function mostrarVistaMonitoreo() {
    //console.log('📊 Mostrando vista de monitoreo específica');
    
    // Ocultar vista de selector
    const selectorView = document.getElementById('sistema-selector-view');
    if (selectorView) {
        selectorView.classList.add('hidden');
        selectorView.style.display = 'none';
        //console.log('✅ Vista selector ocultada');
    } else {
        //console.warn('⚠️ No se encontró elemento sistema-selector-view');
    }
    
    // Mostrar vista de monitoreo
    const monitoringView = document.getElementById('sistema-monitoring-view');
    if (monitoringView) {
        monitoringView.classList.remove('hidden');
        monitoringView.style.display = 'block';
        //console.log('✅ Vista monitoreo mostrada');
        
        // Inicializar tendencias después de mostrar la vista
        setTimeout(() => {
            //console.log('🔄 Inicializando gráfico de tendencias...');
            if (typeof cargarDatosTendencias === 'function') {
                cargarDatosTendencias();
            }
        }, 200);
    } else {
        // console.error('❌ No se encontró elemento sistema-monitoring-view');
    }
    
    // Actualizar información del breadcrumb y título 
    if (typeof SISTEMA_ACTUAL !== 'undefined' && SISTEMA_ACTUAL) {
        // Si hay contexto Django, usar esa información
        const breadcrumbSistema = document.getElementById('breadcrumbSistema');
        if (breadcrumbSistema) {
            breadcrumbSistema.textContent = `${SISTEMA_ACTUAL.tag} - ${SISTEMA_ACTUAL.sistema_id}`;
        }
        
        const sistemaTitle = document.getElementById('sistemaTitle');
        if (sistemaTitle) {
            sistemaTitle.innerHTML = `<i class="bi bi-diagram-3"></i> ${SISTEMA_ACTUAL.tag} - Monitoreo Coriolis`;
        }
    } else {
        // Si no hay contexto Django pero sí sistemId por URL, mostrar genérico
        const sistemaId = obtenerSistemaActual();
        if (sistemaId) {
            const breadcrumbSistema = document.getElementById('breadcrumbSistema');
            if (breadcrumbSistema) {
                breadcrumbSistema.textContent = `Sistema ${sistemaId.substring(0, 8)}...`;
            }
            
            const sistemaTitle = document.getElementById('sistemaTitle');
            if (sistemaTitle) {
                sistemaTitle.innerHTML = `<i class="bi bi-diagram-3"></i> Sistema ${sistemaId.substring(0, 8)}... - Monitoreo Coriolis`;
            }
        }
    }
}

// Función para mostrar la vista de selector
function mostrarVistaSelector() {
    //console.log('📋 Mostrando vista de selección de sistemas');
    
    // Limpiar intervalos activos
    if (tiempoRealInterval) {
        clearInterval(tiempoRealInterval);
        tiempoRealInterval = null;
        //console.log('🛑 Intervalo de tiempo real detenido');
    }
    
    if (tendenciasInterval) {
        clearInterval(tendenciasInterval);
        tendenciasInterval = null;
        //console.log('🛑 Intervalo de tendencias detenido');
    }
    
    // 🔌 Desconectar WebSocket
    if (typeof desconectarWebSocket === 'function') {
        desconectarWebSocket();
        console.log('🔌 WebSocket desconectado');
    }
    
    // Mostrar vista de selector
    const selectorView = document.getElementById('sistema-selector-view');
    if (selectorView) {
        selectorView.classList.remove('hidden');
        selectorView.style.display = 'block';
        //console.log('✅ Vista selector mostrada');
    } else {
        console.warn('⚠️ No se encontró elemento sistema-selector-view');
    }
    
    // Ocultar vista de monitoreo
    const monitoringView = document.getElementById('sistema-monitoring-view');
    if (monitoringView) {
        monitoringView.classList.add('hidden');
        monitoringView.style.display = 'none';
        //console.log('✅ Vista monitoreo ocultada');
    } else {
        //console.warn('⚠️ No se encontró elemento sistema-monitoring-view');
    }
}

// Función alias para compatibilidad con botones existentes
function showSelectorView() {
    //console.log('🔄 Cambiando a vista de selector (showSelectorView)');
    mostrarVistaSelector();
    
    // También detener actualizaciones automáticas cuando volvemos al selector
    if (tiempoRealInterval) {
        clearInterval(tiempoRealInterval);
        tiempoRealInterval = null;
        //console.log('⏸️ Actualizaciones automáticas pausadas');
    }
}

// Limpiar intervals cuando se abandone la página
window.addEventListener('beforeunload', function() {
    if (tiempoRealInterval) {
        clearInterval(tiempoRealInterval);
        //console.log('🧹 Intervals limpiados al salir de la página');
    }
});

// Inicialización cuando se carga la página
document.addEventListener('DOMContentLoaded', function() {
    // console.log('🚀 Iniciando sistema de monitoreo Coriolis con datos REALES');
    
    // Mostrar información de debugging
    // console.log('🔍 Información del contexto:');
    // console.log('  - SISTEMA_ACTUAL disponible:', typeof SISTEMA_ACTUAL !== 'undefined' && SISTEMA_ACTUAL);
    // console.log('  - URL actual:', window.location.pathname);
    
    const sistemaId = obtenerSistemaActual();
    
    if (sistemaId) {
        // console.log(`✅ Sistema detectado: ${sistemaId}`);
        
        // Mostrar información adicional si viene del contexto Django
        if (typeof SISTEMA_ACTUAL !== 'undefined' && SISTEMA_ACTUAL) {
            // console.log(`  - Tag: ${SISTEMA_ACTUAL.tag}`);
            // console.log(`  - Sistema ID: ${SISTEMA_ACTUAL.sistema_id}`);
        }
        
        // ✅ LÓGICA CORREGIDA: Si se detecta cualquier sistema (contexto Django O URL), mostrar vista de monitoreo
        mostrarVistaMonitoreo();
        
        // Actualizar displays inmediatamente (solo carga inicial)
        actualizarDisplaysConDatosReales();
        
        // 🚀 WEBSOCKET: Conectar para recibir TODOS los datos en tiempo real
        console.log('🔌 Iniciando conexión WebSocket para tiempo real...');
        console.log('🔍 Sistema ID para WebSocket:', sistemaId);
        conectarWebSocketTendencias(sistemaId);
        
        // Cargar gráfico de tendencias inicial
        setTimeout(() => {
            cargarDatosTendencias();
        }, 500);
        
        // ✅ ELIMINADO: Ya NO necesitamos polling para displays
        // El WebSocket ahora envía TODOS los datos (tendencias + displays)
        // Comentado para referencia:
        // if (tiempoRealInterval) clearInterval(tiempoRealInterval);
        // tiempoRealInterval = setInterval(() => {
        //     actualizarDisplaysConDatosReales();
        // }, CONFIG.INTERVALOS.ACTUALIZACION_DISPLAYS);
        
        console.log('✅ WebSocket conectado - Sistema 100% en tiempo real (sin polling)');
    } else {
        //console.warn('⚠️ No se detectó un sistema específico - mostrar tabla de selección');
        // Mostrar la vista de selección de sistemas
        mostrarVistaSelector();
        // Fallback a datos simulados para vista general
        actualizarDisplaysSimulados();
    }
});

//console.log('✅ Sistema de monitoreo Coriolis con datos REALES cargado');