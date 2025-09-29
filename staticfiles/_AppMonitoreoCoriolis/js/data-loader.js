// ====================================================================
// DATA-LOADER.JS - Carga de datos desde APIs
// ====================================================================

// Función para actualizar displays con datos reales
async function actualizarDisplaysConDatosReales() {
    const sistemaId = obtenerSistemaActual();
    if (!sistemaId) {
        console.warn('No se detectó un sistema específico en la URL');
        return;
    }
    
    try {
        const response = await fetch(`/monitoreo/api/datos-tiempo-real/${sistemaId}/`);
        const data = await response.json();
        
        if (data.success) {
            // Actualizar displays con datos reales
            document.getElementById('display-sensor1').textContent = 
                `${data.datos.flujo.valor.toFixed(2)} ${data.datos.flujo.unidad}`;

            document.getElementById('display-sensor4').textContent = 
                `${data.datos.flujoMasico.valor.toFixed(2)} ${data.datos.flujoMasico.unidad}`;

            document.getElementById('display-sensor2').textContent = 
                `${data.datos.temperatura.valor.toFixed(2)} ${data.datos.temperatura.unidad}`;

            document.getElementById('display-sensor3').textContent = 
                `${data.datos.presion.valor.toFixed(2)} ${data.datos.presion.unidad}`;

            document.getElementById('display-sensor5').textContent = 
                `${data.datos.temperaturaRedundante.valor.toFixed(2)} ${data.datos.temperaturaRedundante.unidad}`;

            document.getElementById('display-sensor6').textContent = 
                `${data.datos.temperaturaDiagnostico.valor.toFixed(2)} ${data.datos.temperaturaDiagnostico.unidad}`;

            document.getElementById('tabla-volTotal').textContent = 
                `${data.datos.volTotal.valor.toFixed(3)}`;

            document.getElementById('tabla-masTotal').textContent = 
                `${data.datos.masTotal.valor.toFixed(3)}`;

            document.getElementById('tabla-densidad').textContent = 
                `${data.datos.densidad.valor.toFixed(3)}`;

            document.getElementById('tabla-frecuencia').textContent = 
                `${data.datos.frecuencia.valor.toFixed(3)}`;

            document.getElementById('tabla-concSolido').textContent = 
                `${data.datos.concSolido.valor.toFixed(3)}`;

            document.getElementById('tabla-corteAgua').textContent = 
                `${data.datos.corteAgua.valor.toFixed(3)}`;

            document.getElementById('tabla-signalGateway').textContent = 
                `${data.datos.signalGateway.valor.toFixed(3)}`;

            document.getElementById('tabla-tempGateway').textContent = 
                `${data.datos.tempGateway.valor.toFixed(3)}`;
            
            // Actualizar fecha de última actualización
            const ultimaActualizacion = document.getElementById('ultima-actualizacion');
            if (ultimaActualizacion && data.fecha_legible) {
                ultimaActualizacion.textContent = data.fecha_legible;
            }
                
            // console.log('✅ Datos tiempo real actualizados:', data.timestamp);
        } else {
            // console.error('❌ Error obteniendo datos tiempo real:', data.error);
            // Fallback a valores por defecto
            mostrarDatosNoDisponibles();
        }
    } catch (error) {
        // console.error('❌ Error en la petición de datos tiempo real:', error);
        mostrarDatosNoDisponibles();
    }
}

// Función fallback para mostrar mensaje cuando no hay datos
function mostrarDatosNoDisponibles() {
    // Displays principales
    document.getElementById('display-sensor1').textContent = 'Sin datos';
    document.getElementById('display-sensor2').textContent = 'Sin datos';
    document.getElementById('display-sensor3').textContent = 'Sin datos';
    document.getElementById('display-sensor4').textContent = 'Sin datos';
    document.getElementById('display-sensor5').textContent = 'Sin datos';
    document.getElementById('display-sensor6').textContent = 'Sin datos';
    
    // Elementos de la tabla
    document.getElementById('tabla-volTotal').textContent = 'Sin datos';
    document.getElementById('tabla-masTotal').textContent = 'Sin datos';
    document.getElementById('tabla-densidad').textContent = 'Sin datos';
    document.getElementById('tabla-frecuencia').textContent = 'Sin datos';
    document.getElementById('tabla-concSolido').textContent = 'Sin datos';
    document.getElementById('tabla-corteAgua').textContent = 'Sin datos';
    document.getElementById('tabla-signalGateway').textContent = 'Sin datos';
    document.getElementById('tabla-tempGateway').textContent = 'Sin datos';
    
    const ultimaActualizacion = document.getElementById('ultima-actualizacion');
    if (ultimaActualizacion) {
        ultimaActualizacion.textContent = 'Sin datos';
    }
}

// Función para cargar datos de los últimos 3 días (MODO TIEMPO REAL)
async function cargarUltimos3DiasDinamico(sistemaId) {
    try {
        // Calcular fechas usando CONFIG
        const fechaFin = new Date();
        const fechaInicio = new Date();
        fechaInicio.setDate(fechaFin.getDate() - CONFIG.PERIODOS.DIAS_POR_DEFECTO);
        
        const fechaInicioStr = formatearFechaParaAPI(fechaInicio);
        const fechaFinStr = formatearFechaParaAPI(fechaFin);
        
        const url = `/monitoreo/api/datos-flujo/${sistemaId}/?fecha_inicio=${fechaInicioStr}&fecha_fin=${fechaFinStr}`;
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.success) {
            // console.log('🔄 Cargando datos reales de últimos 3 días:', {
            //     volumetrico: data.flujo_volumetrico.total_registros,
            //     masico: data.flujo_masico.total_registros
            // });
            
            // Renderizar gráficos en modo tiempo real
            renderGraficoFlujoVolumetrico(data.flujo_volumetrico, true);
            renderGraficoFlujoMasico(data.flujo_masico, true);
            
            // Actualizar contadores con indicación de tiempo real usando CONFIG
            document.getElementById('contador-volumetrico').textContent = 
                CONFIG.TEXTOS.REGISTROS_TIEMPO_REAL_VOLUMETRICO(data.flujo_volumetrico.total_registros);
            document.getElementById('contador-masico').textContent = 
                CONFIG.TEXTOS.REGISTROS_TIEMPO_REAL_MASICO(data.flujo_masico.total_registros);
            
            // Actualizar información del período usando CONFIG
            const infoPeriodo = document.getElementById('info-periodo');
            if (infoPeriodo) {
                infoPeriodo.textContent = CONFIG.TEXTOS.INFO_PERIODO_TIEMPO_REAL;
            }
            
            // Actualizar indicador de modo
            actualizarIndicadorModo(true);
            
            return true;
        } else {
            console.error('❌ Error cargando datos de últimos 3 días:', data.error);
            renderGraficosVacios('Error: ' + data.error);
            return false;
        }
    } catch (error) {
        console.error('❌ Error en la petición de últimos 3 días:', error);
        console.error('❌ Detalles del error:', {
            message: error.message,
            stack: error.stack,
            sistemaId: sistemaId
        });
        renderGraficosVacios('Error de conexión: ' + error.message);
        return false;
    }
}

// Mejorar la función de carga de datos históricos para mostrar contadores
async function cargarDatosHistoricosFlujo(sistemaId) {
    try {
        const fechaInicio = document.getElementById('fechaInicio').value;
        const fechaFin = document.getElementById('fechaFin').value;
        
        if (!fechaInicio || !fechaFin) {
            alert('Por favor selecciona un rango de fecha y hora válido');
            return;
        }
        
        // Convertir a formato compatible con Django usando función utilitaria
        const fechaInicioISO = formatearFechaParaAPI(fechaInicio);
        const fechaFinISO = formatearFechaParaAPI(fechaFin);
        
        const url = `/monitoreo/api/datos-flujo/${sistemaId}/?fecha_inicio=${fechaInicioISO}&fecha_fin=${fechaFinISO}`;
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.success) {
            // Renderizar gráficos
            renderGraficoFlujoVolumetrico(data.flujo_volumetrico);
            renderGraficoFlujoMasico(data.flujo_masico);
            
            // Actualizar contadores
            document.getElementById('contador-volumetrico').textContent = 
                `${data.flujo_volumetrico.total_registros} registros`;
            document.getElementById('contador-masico').textContent = 
                `${data.flujo_masico.total_registros} registros`;
            
            // Actualizar información del período
            const infoPeriodo = document.getElementById('info-periodo');
            if (infoPeriodo) {
                const fechaInicioFormat = new Date(fechaInicio).toLocaleString('es-ES');
                const fechaFinFormat = new Date(fechaFin).toLocaleString('es-ES');
                infoPeriodo.textContent = ` Período: ${fechaInicioFormat} al ${fechaFinFormat}`;
            }
            
            // Actualizar indicador de modo
            actualizarIndicadorModo(false, fechaInicio, fechaFin);
                
            // console.log('✅ Datos históricos cargados:', {
            //     volumetrico: data.flujo_volumetrico.total_registros,
            //     masico: data.flujo_masico.total_registros
            // });
        } else {
            // console.error('❌ Error cargando datos históricos de flujo:', data.error);
            renderGraficosVacios('Error: ' + data.error);
        }
    } catch (error) {
        // console.error('❌ Error en la petición de datos históricos de flujo:', error);
        renderGraficosVacios('Error de conexión');
    }
}

// Función para exportar datos como CSV
function exportarDatos() {
    const sistemaId = obtenerSistemaActual();
    if (!sistemaId) {
        alert('No se pudo obtener el sistema actual');
        return;
    }
    
    const fechaInicio = document.getElementById('fechaInicio').value;
    const fechaFin = document.getElementById('fechaFin').value;
    
    if (!fechaInicio || !fechaFin) {
        alert('Por favor selecciona un rango de fecha y hora válido');
        return;
    }
    
    // Convertir a formato compatible con Django usando función utilitaria
    const fechaInicioISO = formatearFechaParaAPI(fechaInicio);
    const fechaFinISO = formatearFechaParaAPI(fechaFin);
    
    // Crear URL para descarga
    const url = `/monitoreo/api/datos-flujo/${sistemaId}/?fecha_inicio=${fechaInicioISO}&fecha_fin=${fechaFinISO}`;
    
    // Abrir en nueva ventana para descargar
    window.open(url, '_blank');
    
    // console.log('📥 Descargando datos para el período:', fechaInicio, 'al', fechaFin);
}

// Función fallback para datos simulados (cuando no hay sistema específico)
function actualizarDisplaysSimulados() {
    const val1 = (120 + Math.random() * 10).toFixed(1);
    document.getElementById('display-sensor1').textContent = val1 + ' m³/h';
    const val2 = (90 + Math.random() * 20).toFixed(1);
    document.getElementById('display-sensor2').textContent = val2 + ' °F';
    const val3 = (40 + Math.random() * 10).toFixed(1);
    document.getElementById('display-sensor3').textContent = val3 + ' PSI';
}

// ====================================================================
// FUNCIONES PARA PRESIÓN
// ====================================================================

// Función para cargar datos de presión de los últimos días (MODO TIEMPO REAL)
async function cargarUltimosDiasPresion(sistemaId) {
    try {
        // Calcular fechas usando CONFIG
        const fechaFin = new Date();
        const fechaInicio = new Date();
        fechaInicio.setDate(fechaFin.getDate() - CONFIG.PERIODOS.DIAS_POR_DEFECTO);
        
        const fechaInicioStr = formatearFechaParaAPI(fechaInicio);
        const fechaFinStr = formatearFechaParaAPI(fechaFin);
        
        const url = `/monitoreo/api/datos-presion/${sistemaId}/?fecha_inicio=${fechaInicioStr}&fecha_fin=${fechaFinStr}`;
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.success) {
            // Renderizar gráfico en modo tiempo real
            renderGraficoPresion(data);
            
            // Actualizar contadores con indicación de tiempo real usando CONFIG
            document.getElementById('contador-presion').textContent = 
                CONFIG.TEXTOS.REGISTROS_TIEMPO_REAL_PRESION(data.total_registros);
            
            // Actualizar información del período usando CONFIG
            const infoPeriodoPresion = document.getElementById('info-periodo-presion');
            if (infoPeriodoPresion) {
                infoPeriodoPresion.textContent = CONFIG.TEXTOS.INFO_PERIODO_TIEMPO_REAL;
            }
            
            // Actualizar indicador de modo
            actualizarIndicadorModoPresion(true);
            
            return true;
        } else {
            console.error('❌ Error cargando datos de presión:', data.error);
            renderGraficoPresionVacio('Error: ' + data.error);
            return false;
        }
    } catch (error) {
        console.error('❌ Error en la petición de datos de presión:', error);
        renderGraficoPresionVacio('Error de conexión');
        return false;
    }
}

// Función para cargar datos históricos de presión (MODO FILTRADO)
async function cargarDatosHistoricosPresion(sistemaId, fechaInicio, fechaFin) {
    try {
        const fechaInicioISO = formatearFechaParaAPI(fechaInicio);
        const fechaFinISO = formatearFechaParaAPI(fechaFin);
        
        const url = `/monitoreo/api/datos-presion/${sistemaId}/?fecha_inicio=${fechaInicioISO}&fecha_fin=${fechaFinISO}`;
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.success) {
            // Renderizar gráfico con datos históricos
            renderGraficoPresion(data);
            
            // Actualizar contadores sin indicación de tiempo real
            document.getElementById('contador-presion').textContent = 
                `${data.total_registros} registros`;
            
            // Actualizar indicador de modo
            actualizarIndicadorModoPresion(false, fechaInicio, fechaFin);
                
            console.log('✅ Datos históricos de presión cargados:', {
                presion: data.total_registros
            });
        } else {
            console.error('❌ Error cargando datos históricos de presión:', data.error);
            renderGraficoPresionVacio('Error: ' + data.error);
        }
    } catch (error) {
        console.error('❌ Error en la petición de datos históricos de presión:', error);
        renderGraficoPresionVacio('Error de conexión');
    }
}

// Función para exportar datos de presión como CSV
function exportarDatosPresion() {
    const sistemaId = obtenerSistemaActual();
    if (!sistemaId) {
        alert('No se pudo obtener el sistema actual');
        return;
    }
    
    const fechaInicio = document.getElementById('fechaInicioPresion').value;
    const fechaFin = document.getElementById('fechaFinPresion').value;
    
    if (!fechaInicio || !fechaFin) {
        alert('Por favor selecciona un rango de fecha y hora válido');
        return;
    }
    
    // Convertir a formato compatible con Django usando función utilitaria
    const fechaInicioISO = formatearFechaParaAPI(fechaInicio);
    const fechaFinISO = formatearFechaParaAPI(fechaFin);
    
    // Crear URL para descarga
    const url = `/monitoreo/api/datos-presion/${sistemaId}/?fecha_inicio=${fechaInicioISO}&fecha_fin=${fechaFinISO}&export=csv`;
    
    // Abrir en nueva ventana para descargar
    window.open(url, '_blank');
    
    console.log('📥 Descargando datos de presión para el período:', fechaInicio, 'al', fechaFin);
}

// ====================================================================
// FUNCIONES PARA TEMPERATURA
// ====================================================================

// Función para cargar datos históricos de temperatura (MODO FILTRADO o MODO TIEMPO REAL)
async function cargarDatosHistoricosTemperatura(sistemaId, fechaInicio = null, fechaFin = null) {
    try {
        let url;
        
        if (fechaInicio && fechaFin) {
            // Modo filtrado - usar fechas específicas
            const fechaInicioISO = formatearFechaParaAPI(fechaInicio);
            const fechaFinISO = formatearFechaParaAPI(fechaFin);
            url = `/monitoreo/api/datos-temperatura/${sistemaId}/?fecha_inicio=${fechaInicioISO}&fecha_fin=${fechaFinISO}`;
        } else {
            // Modo tiempo real - usar fechas calculadas automáticamente
            const fechaFinCalc = new Date();
            const fechaInicioCalc = new Date();
            fechaInicioCalc.setDate(fechaFinCalc.getDate() - CONFIG.PERIODOS.DIAS_POR_DEFECTO);
            
            const fechaInicioStr = formatearFechaParaAPI(fechaInicioCalc);
            const fechaFinStr = formatearFechaParaAPI(fechaFinCalc);
            
            url = `/monitoreo/api/datos-temperatura/${sistemaId}/?fecha_inicio=${fechaInicioStr}&fecha_fin=${fechaFinStr}`;
        }
        
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.success) {
            // Renderizar gráficos con datos históricos
            renderGraficosTemperatura(data);
            
            if (fechaInicio && fechaFin) {
                // Modo filtrado - contadores sin indicación de tiempo real
                document.getElementById('contador-temperatura-coriolis').textContent = 
                    `${data.coriolis_temperature.total_registros} registros`;
                document.getElementById('contador-temperatura-diagnostic').textContent = 
                    `${data.diagnostic_temperature.total_registros} registros`;
                document.getElementById('contador-temperatura-redundant').textContent = 
                    `${data.redundant_temperature.total_registros} registros`;
                
                // Actualizar indicador de modo
                actualizarIndicadorModoTemperatura(false, fechaInicio, fechaFin);
            } else {
                // Modo tiempo real - contadores con indicación de tiempo real usando CONFIG
                document.getElementById('contador-temperatura-coriolis').textContent = 
                    CONFIG.TEXTOS.REGISTROS_TIEMPO_REAL_TEMPERATURA_CORIOLIS(data.coriolis_temperature.total_registros);
                document.getElementById('contador-temperatura-diagnostic').textContent = 
                    CONFIG.TEXTOS.REGISTROS_TIEMPO_REAL_TEMPERATURA_DIAGNOSTIC(data.diagnostic_temperature.total_registros);
                document.getElementById('contador-temperatura-redundant').textContent = 
                    CONFIG.TEXTOS.REGISTROS_TIEMPO_REAL_TEMPERATURA_REDUNDANT(data.redundant_temperature.total_registros);
                
                // Actualizar período mostrado con CONFIG
                document.getElementById('info-periodo-temperatura').textContent = 
                    CONFIG.TEXTOS.INFO_PERIODO_TIEMPO_REAL;
                
                // Actualizar indicador de modo
                actualizarIndicadorModoTemperatura(true);
            }
                
            console.log('✅ Datos históricos de temperatura cargados:', {
                coriolis: data.coriolis_temperature.total_registros,
                diagnostic: data.diagnostic_temperature.total_registros,
                redundant: data.redundant_temperature.total_registros
            });
        } else {
            console.error('❌ Error cargando datos históricos de temperatura:', data.error);
            renderGraficosTemperaturaVacios('Error: ' + data.error);
        }
    } catch (error) {
        console.error('❌ Error en la petición de datos históricos de temperatura:', error);
        renderGraficosTemperaturaVacios('Error de conexión');
    }
}

// Función para exportar datos de temperatura como CSV
function exportarDatosTemperatura() {
    const sistemaId = obtenerSistemaActual();
    if (!sistemaId) {
        alert('No se pudo obtener el sistema actual');
        return;
    }
    
    const fechaInicio = document.getElementById('fechaInicioTemperatura').value;
    const fechaFin = document.getElementById('fechaFinTemperatura').value;
    
    if (!fechaInicio || !fechaFin) {
        alert('Por favor selecciona un rango de fecha y hora válido');
        return;
    }
    
    // Convertir a formato compatible con Django usando función utilitaria
    const fechaInicioISO = formatearFechaParaAPI(fechaInicio);
    const fechaFinISO = formatearFechaParaAPI(fechaFin);
    
    // Crear URL para descarga
    const url = `/monitoreo/api/datos-temperatura/${sistemaId}/?fecha_inicio=${fechaInicioISO}&fecha_fin=${fechaFinISO}&export=csv`;
    
    // Abrir en nueva ventana para descargar
    window.open(url, '_blank');
    
    console.log('📥 Descargando datos de temperatura para el período:', fechaInicio, 'al', fechaFin);
}