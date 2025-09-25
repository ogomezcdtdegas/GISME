// ====================================================================
// TIME-CONTROL.JS - Control de modos tiempo real y filtrado
// ====================================================================

// Función para inicializar modo tiempo real (últimos 3 días que se actualizan)
function inicializarModoTiempoReal() {
    const sistemaId = obtenerSistemaActual();
    if (!sistemaId) return;
    
    // console.log('🔄 Iniciando modo tiempo real - últimos 3 días dinámico');
    modoTiempoReal = true;
    
    // Cargar datos iniciales
    cargarUltimos3DiasDinamico(sistemaId);
    
    // Configurar actualización automática usando CONFIG
    if (intervalActualizacionGraficos) {
        clearInterval(intervalActualizacionGraficos);
    }
    
    intervalActualizacionGraficos = setInterval(async () => {
        if (modoTiempoReal) {
            // console.log('🔄 Actualizando gráficos automáticamente...');
            await cargarUltimos3DiasDinamico(sistemaId);
        }
    }, CONFIG.INTERVALOS.ACTUALIZACION_GRAFICOS);
    
    // Actualizar indicador de modo
    actualizarIndicadorModo(true);
    
    console.log(CONFIG.TEXTOS.CONSOLE_MODO_TIEMPO_REAL);
}

// Función para actualizar indicador de modo
function actualizarIndicadorModo(esTiempoReal, fechaInicio = null, fechaFin = null) {
    const indicador = document.getElementById('modo-indicador');
    if (!indicador) return;
    
    if (esTiempoReal) {
        indicador.innerHTML = `
            <strong>Modo Tiempo Real:</strong> 
            <span class="badge bg-success me-2">●</span>
            ${CONFIG.TEXTOS.MODO_TIEMPO_REAL}
        `;
    } else {
        const fechaInicioFormat = fechaInicio ? new Date(fechaInicio).toLocaleString('es-ES') : 'N/A';
        const fechaFinFormat = fechaFin ? new Date(fechaFin).toLocaleString('es-ES') : 'N/A';
        indicador.innerHTML = `
            <strong>Modo Filtrado:</strong> 
            <span class="badge bg-warning me-2">⏸</span>
            Datos estáticos del período: ${fechaInicioFormat} al ${fechaFinFormat}. Use "Volver a Tiempo Real" para reactivar actualizaciones.
        `;
    }
}

// Función para cambiar a modo filtrado (estático)
function cambiarAModoFiltrado() {
    // console.log('⏸️ Cambiando a modo filtrado - pausando actualizaciones automáticas');
    modoTiempoReal = false;
    
    // Detener actualizaciones automáticas
    if (intervalActualizacionGraficos) {
        clearInterval(intervalActualizacionGraficos);
        intervalActualizacionGraficos = null;
    }
    
    // Obtener fechas seleccionadas para el indicador
    const fechaInicio = document.getElementById('fechaInicio')?.value || null;
    const fechaFin = document.getElementById('fechaFin')?.value || null;
    
    // Actualizar indicador de modo
    actualizarIndicadorModo(false, fechaInicio, fechaFin);
}

// Función para configurar eventos del modal
function configurarEventosModal() {
    // Agregar evento al botón buscar
    const btnBuscar = document.getElementById('buscarHistoricoFlujo');
    if (btnBuscar) {
        btnBuscar.onclick = function() {
            cambiarAModoFiltrado();  // Cambiar a modo filtrado
            buscarHistoricoFlujo();   // Buscar con filtros
        };
    }
    
    // Agregar evento al botón reset (volver a tiempo real)
    const btnReset = document.getElementById('volverTiempoReal');
    if (btnReset) {
        btnReset.onclick = resetearAModoTiempoReal;
    }
    
    // console.log('🔧 Eventos del modal configurados');
}

// Función para resetear a modo tiempo real
function resetearAModoTiempoReal() {
    // console.log('▶️ Reseteando a modo tiempo real - últimos 3 días dinámico');
    
    // Resetear fechas a valores por defecto (últimos 3 días)
    const fechaFin = new Date();
    const fechaInicio = new Date();
    fechaInicio.setDate(fechaFin.getDate() - 3);
    
    document.getElementById('fechaInicio').value = fechaInicio.toISOString().slice(0, 16);
    document.getElementById('fechaFin').value = fechaFin.toISOString().slice(0, 16);
    
    // Reiniciar modo tiempo real
    inicializarModoTiempoReal();
    
    // Actualizar indicador de modo
    actualizarIndicadorModo(true);
}

// Función para buscar histórico con filtros de fecha (BOTÓN BUSCAR)
async function buscarHistoricoFlujo() {
    const sistemaId = obtenerSistemaActual();
    if (!sistemaId) {
        alert('Error: No se pudo identificar el sistema actual para realizar la búsqueda.');
        return;
    }
    
    // console.log('🔍 Buscando histórico con nuevos filtros...');
    await cargarDatosHistoricosFlujo(sistemaId);
}