// ====================================================================
// MAIN.JS - Inicialización principal y control de vistas
// ====================================================================

// Función para abrir modal de flujo (sensor1) con dos gráficos REALES
async function abrirModal(sensorId) {
    if (sensorId !== 'sensor1') {
        // Para sensor2 y sensor3, mostrar mensaje temporal
        alert(`Funcionalidad para ${sensorId} en desarrollo.\nActualmente solo está disponible el histórico de flujo (sensor1).`);
        return;
    }
    
    const sistemaId = obtenerSistemaActual();
    if (!sistemaId) {
        // console.error('❌ No se pudo obtener el ID del sistema');
        alert('Error: No se pudo identificar el sistema actual.\n\nVerifique que:\n1. Está accediendo desde un sistema específico\n2. El sistema existe en la base de datos\n3. La URL contiene el ID del sistema');
        return;
    }
    
    // Configurar fechas por defecto usando CONFIG
    const fechaFin = new Date();
    const fechaInicio = new Date();
    fechaInicio.setDate(fechaFin.getDate() - CONFIG.PERIODOS.DIAS_POR_DEFECTO);
    
    document.getElementById('fechaInicio').value = fechaInicio.toISOString().slice(0, 16);
    document.getElementById('fechaFin').value = fechaFin.toISOString().slice(0, 16);
    
    // Iniciar en modo tiempo real por defecto (últimos 3 días que se actualizan)
    inicializarModoTiempoReal();
    
    // Mostrar modal
    var modal = new bootstrap.Modal(document.getElementById('historicoModal'));
    modal.show();
    
    // Configurar eventos del modal
    configurarEventosModal();
    
    // console.log(`✅ Modal de flujo abierto para sistema: ${sistemaId}`);
}

// Función para mostrar la vista de monitoreo
function mostrarVistaMonitoreo() {
    console.log('📊 Mostrando vista de monitoreo específica');
    
    // Ocultar vista de selector
    const selectorView = document.getElementById('sistema-selector-view');
    if (selectorView) {
        selectorView.classList.add('hidden');
        selectorView.style.display = 'none';
        console.log('✅ Vista selector ocultada');
    } else {
        console.warn('⚠️ No se encontró elemento sistema-selector-view');
    }
    
    // Mostrar vista de monitoreo
    const monitoringView = document.getElementById('sistema-monitoring-view');
    if (monitoringView) {
        monitoringView.classList.remove('hidden');
        monitoringView.style.display = 'block';
        console.log('✅ Vista monitoreo mostrada');
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
    console.log('📋 Mostrando vista de selección de sistemas');
    
    // Mostrar vista de selector
    const selectorView = document.getElementById('sistema-selector-view');
    if (selectorView) {
        selectorView.classList.remove('hidden');
        selectorView.style.display = 'block';
        console.log('✅ Vista selector mostrada');
    } else {
        console.warn('⚠️ No se encontró elemento sistema-selector-view');
    }
    
    // Ocultar vista de monitoreo
    const monitoringView = document.getElementById('sistema-monitoring-view');
    if (monitoringView) {
        monitoringView.classList.add('hidden');
        monitoringView.style.display = 'none';
        console.log('✅ Vista monitoreo ocultada');
    } else {
        console.warn('⚠️ No se encontró elemento sistema-monitoring-view');
    }
}

// Función alias para compatibilidad con botones existentes
function showSelectorView() {
    console.log('🔄 Cambiando a vista de selector (showSelectorView)');
    mostrarVistaSelector();
    
    // También detener actualizaciones automáticas cuando volvemos al selector
    if (tiempoRealInterval) {
        clearInterval(tiempoRealInterval);
        tiempoRealInterval = null;
        console.log('⏸️ Actualizaciones automáticas pausadas');
    }
}

// Limpiar intervals cuando se abandone la página
window.addEventListener('beforeunload', function() {
    if (tiempoRealInterval) {
        clearInterval(tiempoRealInterval);
        console.log('🧹 Intervals limpiados al salir de la página');
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
        
        // Actualizar displays inmediatamente
        actualizarDisplaysConDatosReales();
        
        // Configurar actualización automática usando CONFIG
        if (tiempoRealInterval) clearInterval(tiempoRealInterval);
        tiempoRealInterval = setInterval(actualizarDisplaysConDatosReales, CONFIG.INTERVALOS.ACTUALIZACION_DISPLAYS);
        
        console.log(CONFIG.TEXTOS.CONSOLE_ACTUALIZACION);
    } else {
        console.warn('⚠️ No se detectó un sistema específico - mostrar tabla de selección');
        // Mostrar la vista de selección de sistemas
        mostrarVistaSelector();
        // Fallback a datos simulados para vista general
        actualizarDisplaysSimulados();
    }
});

console.log('✅ Sistema de monitoreo Coriolis con datos REALES cargado');