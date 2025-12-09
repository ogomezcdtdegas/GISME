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
    
    //console.log(CONFIG.TEXTOS.CONSOLE_MODO_TIEMPO_REAL);
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
    
    // Resetear campos de fecha (solo referencia visual, no afecta tiempo real)
    const fechaFin = new Date();
    const fechaInicio = new Date(fechaFin.getTime() - (1 * 60 * 60 * 1000)); // 1 hora atrás
    
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

// ====================================================================
// FUNCIONES DE CONTROL DE TIEMPO PARA PRESIÓN
// ====================================================================

// Función para inicializar modo tiempo real de presión
function inicializarModoTiempoRealPresion() {
    const sistemaId = obtenerSistemaActual();
    if (!sistemaId) return;
    
    //console.log('🔄 Iniciando modo tiempo real presión');
    modoTiempoRealPresion = true;
    
    // Cargar datos iniciales
    cargarUltimosDiasPresion(sistemaId);
    
    // Configurar actualización automática usando CONFIG
    if (intervalActualizacionPresion) {
        clearInterval(intervalActualizacionPresion);
    }
    
    intervalActualizacionPresion = setInterval(async () => {
        if (modoTiempoRealPresion) {
            //console.log('🔄 Actualizando gráfico de presión automáticamente...');
            await cargarUltimosDiasPresion(sistemaId);
        }
    }, CONFIG.INTERVALOS.ACTUALIZACION_GRAFICOS);
    
    // Actualizar indicador de modo
    actualizarIndicadorModoPresion(true);
    
    //console.log(CONFIG.TEXTOS.CONSOLE_MODO_TIEMPO_REAL);
}

// Función para actualizar indicador de modo de presión
function actualizarIndicadorModoPresion(esTiempoReal, fechaInicio = null, fechaFin = null) {
    const indicador = document.getElementById('modo-indicador-presion');
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

// Función para cambiar a modo filtrado de presión
function cambiarAModoFiltradoPresion() {
    //console.log('⏸️ Cambiando presión a modo filtrado');
    modoTiempoRealPresion = false;
    
    // Detener actualizaciones automáticas
    if (intervalActualizacionPresion) {
        clearInterval(intervalActualizacionPresion);
        intervalActualizacionPresion = null;
    }
    
    // Obtener fechas seleccionadas
    const fechaInicio = document.getElementById('fechaInicioPresion')?.value || null;
    const fechaFin = document.getElementById('fechaFinPresion')?.value || null;
    
    // Actualizar indicador de modo
    actualizarIndicadorModoPresion(false, fechaInicio, fechaFin);
}

// Función para resetear presión a modo tiempo real
function resetearPresionATiempoReal() {
    //console.log('▶️ Reseteando presión a modo tiempo real');
    
    // Resetear campos de fecha (solo referencia visual, no afecta tiempo real)
    const fechaFin = new Date();
    const fechaInicio = new Date(fechaFin.getTime() - (1 * 60 * 60 * 1000)); // 1 hora atrás
    
    document.getElementById('fechaInicioPresion').value = fechaInicio.toISOString().slice(0, 16);
    document.getElementById('fechaFinPresion').value = fechaFin.toISOString().slice(0, 16);
    
    // Reiniciar modo tiempo real
    inicializarModoTiempoRealPresion();
    
    // Actualizar indicador de modo
    actualizarIndicadorModoPresion(true);
}

// Función para buscar histórico de presión con filtros
async function buscarHistoricoPresion() {
    const sistemaId = obtenerSistemaActual();
    if (!sistemaId) {
        alert('Error: No se pudo identificar el sistema actual para realizar la búsqueda.');
        return;
    }
    
    //console.log('🔍 Buscando histórico de presión con filtros...');
    
    const fechaInicio = document.getElementById('fechaInicioPresion').value;
    const fechaFin = document.getElementById('fechaFinPresion').value;
    
    if (!fechaInicio || !fechaFin) {
        alert('Por favor selecciona un rango de fecha y hora válido');
        return;
    }
    
    await cargarDatosHistoricosPresion(sistemaId, fechaInicio, fechaFin);
}

// Función para configurar eventos del modal de presión
function configurarEventosModalPresion() {
    // Evento para botón buscar
    const btnBuscar = document.getElementById('buscarHistoricoPresion');
    if (btnBuscar) {
        btnBuscar.onclick = function() {
            cambiarAModoFiltradoPresion();
            buscarHistoricoPresion();
        };
    }
    
    // Evento para botón volver a tiempo real
    const btnReset = document.getElementById('volverTiempoRealPresion');
    if (btnReset) {
        btnReset.onclick = resetearPresionATiempoReal;
    }
    
    //console.log('🔧 Eventos del modal de presión configurados');
}

// ====================================================================
// FUNCIONES DE CONTROL DE TIEMPO PARA TEMPERATURA
// ====================================================================

// Función para inicializar modo tiempo real de temperatura
function inicializarModoTiempoRealTemperatura() {
    //console.log('🌡️ Inicializando modo tiempo real para temperatura');
    
    modoTiempoRealTemperatura = true;
    
    // Limpiar interval existente de temperatura si existe
    if (intervalActualizacionTemperatura) {
        clearInterval(intervalActualizacionTemperatura);
    }
    
    // Cargar datos iniciales de temperatura
    const sistemaId = obtenerSistemaActual();
    if (sistemaId) {
        cargarDatosHistoricosTemperatura(sistemaId);
        
        // Configurar actualización automática para temperatura
        intervalActualizacionTemperatura = setInterval(function() {
            if (modoTiempoRealTemperatura) {
                //console.log('⚡ Auto-actualizando datos de temperatura...');
                cargarDatosHistoricosTemperatura(sistemaId);
            }
        }, CONFIG.INTERVALOS.ACTUALIZACION_GRAFICOS);
        
        //console.log(CONFIG.TEXTOS.CONSOLE_MODO_TIEMPO_REAL);
    }
    
    // Actualizar indicador
    actualizarIndicadorModoTemperatura(true);
}

// Función para actualizar indicador de modo de temperatura
function actualizarIndicadorModoTemperatura(esTiempoReal, fechaInicio = null, fechaFin = null) {
    const indicador = document.getElementById('modo-indicador-temperatura');
    if (!indicador) return;
    
    if (esTiempoReal) {
        indicador.innerHTML = `
            <strong>Modo Tiempo Real:</strong> 
            <span class="badge bg-success me-2">●</span>
            Los gráficos se actualizan automáticamente mostrando los últimos datos de temperatura.
        `;
    } else {
        const fechaInicioStr = fechaInicio ? new Date(fechaInicio).toLocaleDateString('es-CO') : 'N/A';
        const fechaFinStr = fechaFin ? new Date(fechaFin).toLocaleDateString('es-CO') : 'N/A';
        
        indicador.innerHTML = `
            <strong>Modo Filtrado:</strong> 
            <span class="badge bg-warning me-2">●</span>
            Mostrando datos desde ${fechaInicioStr} hasta ${fechaFinStr}. Los gráficos no se actualizan automáticamente.
        `;
    }
}

// Función para cambiar a modo filtrado de temperatura
function cambiarAModoFiltradoTemperatura() {
    //console.log('⏸️ Cambiando temperatura a modo filtrado');
    
    modoTiempoRealTemperatura = false;
    
    // Detener actualización automática de temperatura
    if (intervalActualizacionTemperatura) {
        clearInterval(intervalActualizacionTemperatura);
        intervalActualizacionTemperatura = null;
        //console.log('⏹️ Detenida la actualización automática de temperatura');
    }
}

// Función para resetear temperatura a modo tiempo real
function resetearTemperaturaATiempoReal() {
    //console.log('▶️ Reseteando temperatura a modo tiempo real');
    
    // Resetear campos de fecha (solo referencia visual, no afecta tiempo real)
    const fechaFin = new Date();
    const fechaInicio = new Date(fechaFin.getTime() - (1 * 60 * 60 * 1000)); // 1 hora atrás
    
    document.getElementById('fechaInicioTemperatura').value = fechaInicio.toISOString().slice(0, 16);
    document.getElementById('fechaFinTemperatura').value = fechaFin.toISOString().slice(0, 16);
    
    // Reiniciar modo tiempo real
    inicializarModoTiempoRealTemperatura();
    
    // Actualizar indicador de modo
    actualizarIndicadorModoTemperatura(true);
}

// Función para buscar histórico de temperatura con filtros
async function buscarHistoricoTemperatura() {
    const sistemaId = obtenerSistemaActual();
    if (!sistemaId) {
        alert('Error: No se pudo identificar el sistema actual para realizar la búsqueda.');
        return;
    }
    
    //console.log('🔍 Buscando histórico de temperatura con filtros...');
    
    const fechaInicio = document.getElementById('fechaInicioTemperatura').value;
    const fechaFin = document.getElementById('fechaFinTemperatura').value;
    
    if (!fechaInicio || !fechaFin) {
        alert('Por favor selecciona un rango de fecha y hora válido');
        return;
    }
    
    await cargarDatosHistoricosTemperatura(sistemaId, fechaInicio, fechaFin);
}

// Función para configurar eventos del modal de temperatura
function configurarEventosModalTemperatura() {
    // Evento para botón buscar
    const btnBuscar = document.getElementById('buscarHistoricoTemperatura');
    if (btnBuscar) {
        btnBuscar.onclick = function() {
            cambiarAModoFiltradoTemperatura();
            buscarHistoricoTemperatura();
        };
    }
    
    // Evento para botón volver a tiempo real
    const btnReset = document.getElementById('volverTiempoRealTemperatura');
    if (btnReset) {
        btnReset.onclick = resetearTemperaturaATiempoReal;
    }
    
    //console.log('🔧 Eventos del modal de temperatura configurados');
}