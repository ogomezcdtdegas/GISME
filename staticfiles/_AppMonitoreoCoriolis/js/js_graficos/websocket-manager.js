// ====================================================================
// WEBSOCKET-MANAGER.JS - Manejo de conexiones WebSocket para tiempo real
// ====================================================================

let tendenciasSocket = null;
let sistemaIdActual = null;
let reconnectAttempts = 0;
const maxReconnectAttempts = 5;
let reconnectTimeout = null;

/**
 * Conectar al WebSocket de tendencias para un sistema específico
 * @param {string} sistemaId - UUID del sistema
 */
function conectarWebSocketTendencias(sistemaId) {
    // ✅ VALIDAR que sistemaId no sea null/undefined
    if (!sistemaId || sistemaId === 'null' || sistemaId === 'undefined') {
        console.error('❌ Error: sistemaId inválido:', sistemaId);
        console.log('🔍 Intentando obtener sistemaId desde obtenerSistemaActual()...');
        
        // Intentar obtener desde función global
        if (typeof obtenerSistemaActual === 'function') {
            sistemaId = obtenerSistemaActual();
            console.log('✅ sistemaId obtenido:', sistemaId);
        }
        
        if (!sistemaId || sistemaId === 'null') {
            console.error('❌ No se pudo obtener sistemaId válido. Abortando conexión WebSocket.');
            mostrarEstadoConexion('error');
            return;
        }
    }
    
    // Si ya hay una conexión activa para este sistema, no reconectar
    if (tendenciasSocket && tendenciasSocket.readyState === WebSocket.OPEN && sistemaIdActual === sistemaId) {
        console.log('✅ WebSocket ya está conectado para este sistema');
        return;
    }

    // Cerrar conexión anterior si existe
    if (tendenciasSocket) {
        console.log('🔌 Cerrando conexión WebSocket anterior...');
        tendenciasSocket.close();
    }

    sistemaIdActual = sistemaId;
    reconnectAttempts = 0;

    // Determinar protocolo (ws o wss)
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/tendencias/${sistemaId}/`;

    console.log(`🔌 Conectando WebSocket: ${wsUrl}`);

    try {
        tendenciasSocket = new WebSocket(wsUrl);

        tendenciasSocket.onopen = function(e) {
            console.log('✅ WebSocket conectado exitosamente');
            reconnectAttempts = 0;
            
            // Mostrar indicador de conexión
            mostrarEstadoConexion('conectado');
        };

        tendenciasSocket.onmessage = function(event) {
            try {
                const data = JSON.parse(event.data);
                console.log('📬 Mensaje WebSocket recibido:', data);
                
                if (data.tipo === 'datos_nuevos') {
                    console.log('📦 Datos nuevos detectados:', data.datos);
                    console.log('🔍 trendChart existe?', typeof trendChart !== 'undefined' && trendChart !== null);
                    
                    // Actualizar gráfica de tendencias con datos nuevos
                    actualizarTendenciasConDatosWebSocket(data.datos);
                    
                    // Actualizar displays en tiempo real
                    actualizarDisplaysConDatosWebSocket(data.datos);
                }
            } catch (error) {
                console.error('❌ Error al procesar mensaje WebSocket:', error);
            }
        };

        tendenciasSocket.onclose = function(event) {
            console.log('🔌 WebSocket cerrado:', event.code, event.reason);
            mostrarEstadoConexion('desconectado');
            
            // Intentar reconectar si no fue cierre intencional
            if (event.code !== 1000 && reconnectAttempts < maxReconnectAttempts) {
                reconectarWebSocket(sistemaId);
            }
        };

        tendenciasSocket.onerror = function(error) {
            console.error('❌ Error en WebSocket:', error);
            mostrarEstadoConexion('error');
        };

    } catch (error) {
        console.error('❌ Error al crear WebSocket:', error);
        mostrarEstadoConexion('error');
    }
}

/**
 * Intentar reconectar al WebSocket con backoff exponencial
 */
function reconectarWebSocket(sistemaId) {
    if (reconnectAttempts >= maxReconnectAttempts) {
        console.error('❌ Máximo de intentos de reconexión alcanzado');
        mostrarEstadoConexion('error');
        // Volver a polling como fallback
        console.log('🔄 Volviendo a polling como fallback...');
        iniciarPolling(sistemaId);
        return;
    }

    reconnectAttempts++;
    const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000); // Max 30 segundos
    
    console.log(`🔄 Reintentando conexión en ${delay}ms (intento ${reconnectAttempts}/${maxReconnectAttempts})...`);
    
    clearTimeout(reconnectTimeout);
    reconnectTimeout = setTimeout(() => {
        conectarWebSocketTendencias(sistemaId);
    }, delay);
}

/**
 * Desconectar WebSocket
 */
function desconectarWebSocket() {
    if (tendenciasSocket) {
        console.log('🔌 Desconectando WebSocket...');
        tendenciasSocket.close(1000, 'Desconexión intencional');
        tendenciasSocket = null;
        sistemaIdActual = null;
    }
    
    clearTimeout(reconnectTimeout);
    mostrarEstadoConexion('desconectado');
}

/**
 * Actualizar gráfica de tendencias con datos del WebSocket
 */
function actualizarTendenciasConDatosWebSocket(datos) {
    // Verificar que trendChart esté disponible (usar window por si acaso)
    const chart = window.trendChart || trendChart;
    
    if (!chart) {
        console.warn('⚠️ Gráfica de tendencias no inicializada todavía');
        return;
    }

    try {
        const timestamp = datos.timestamp ? new Date(datos.timestamp).getTime() : Date.now();
        const datasets = chart.data.datasets;

        console.log('📊 Actualizando gráfico con', datasets.length, 'datasets');

        // Actualizar cada dataset
        const dataMapping = {
            'Flujo Másico (kg/min)': datos.flujo_masico,
            'Flujo Volumétrico (gal/min)': datos.flujo_volumetrico,
            'Temperatura Coriolis (°F)': datos.temperatura_coriolis,
            'Temperatura de Salida (°F)': datos.temperatura_salida,
            'Presión (PSI)': datos.presion,
            'Densidad (g/cm³)': datos.densidad
        };

        let puntosAgregados = 0;
        datasets.forEach(dataset => {
            const valor = dataMapping[dataset.label];
            if (valor !== null && valor !== undefined) {
                // Agregar nuevo punto
                dataset.data.push({
                    x: timestamp,
                    y: valor
                });

                // Mantener solo últimos 100 puntos (30 minutos aprox)
                if (dataset.data.length > 100) {
                    dataset.data.shift();
                }
                puntosAgregados++;
            }
        });

        // Actualizar gráfica sin animación
        chart.update('none');
        
        console.log(`📊 Gráfico actualizado: ${puntosAgregados} líneas con nuevos datos`);
        
    } catch (error) {
        console.error('❌ Error al actualizar tendencias:', error);
    }
}

/**
 * Actualizar displays con datos del WebSocket
 */
function actualizarDisplaysConDatosWebSocket(datos) {
    try {
        // Actualizar displays principales (sensor1-6)
        const displayUpdates = [
            { id: 'display-sensor1', valor: datos.flujo_volumetrico, decimales: 2 },
            { id: 'display-sensor4', valor: datos.flujo_masico, decimales: 2 },
            { id: 'display-sensor2', valor: datos.temperatura_coriolis, decimales: 2 },
            { id: 'display-sensor6', valor: datos.temperatura_salida, decimales: 2 },
            { id: 'display-sensor3', valor: datos.presion, decimales: 2 },
            { id: 'display-sensor5', valor: datos.densidad, decimales: 4 }
        ];

        let actualizados = 0;
        displayUpdates.forEach(({ id, valor, decimales }) => {
            if (valor !== null && valor !== undefined) {
                const elemento = document.getElementById(id);
                if (elemento) {
                    elemento.textContent = valor.toFixed(decimales);
                    actualizados++;
                }
            }
        });
        
        // Actualizar tabla de "Otras variables del Sistema"
        const tablaUpdates = [
            { id: 'tabla-volTotal', valor: datos.vol_total, decimales: 1 },
            { id: 'tabla-masTotal', valor: datos.mas_total, decimales: 1 },
            { id: 'tabla-densidad', valor: datos.densidad, decimales: 4 },
            { id: 'tabla-frecuencia', valor: datos.frecuencia, decimales: 0 },
            { id: 'tabla-NoiseEstimatedN1', valor: datos.noise_n1, decimales: 2 },
            { id: 'tabla-NoiseEstimatedN2', valor: datos.noise_n2, decimales: 2 },
            { id: 'tabla-DriverAmplitude', valor: datos.driver_amplitude, decimales: 2 }
        ];

        tablaUpdates.forEach(({ id, valor, decimales }) => {
            if (valor !== null && valor !== undefined) {
                const elemento = document.getElementById(id);
                if (elemento) {
                    elemento.textContent = valor.toFixed(decimales);
                    actualizados++;
                }
            }
        });
        
        if (actualizados > 0) {
            console.log(`✅ ${actualizados} elementos actualizados (displays + tabla)`);
        }
        
    } catch (error) {
        console.error('❌ Error al actualizar displays:', error);
    }
}

/**
 * Mostrar indicador de estado de conexión
 */
function mostrarEstadoConexion(estado) {
    // Buscar o crear indicador de conexión
    let indicador = document.getElementById('wsConnectionStatus');
    
    if (!indicador) {
        // Crear indicador si no existe
        indicador = document.createElement('div');
        indicador.id = 'wsConnectionStatus';
        indicador.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            z-index: 9999;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            transition: all 0.3s;
        `;
        document.body.appendChild(indicador);
    }

    switch (estado) {
        case 'conectado':
            indicador.textContent = '🟢 Tiempo Real';
            indicador.style.backgroundColor = '#d4edda';
            indicador.style.color = '#155724';
            break;
        case 'desconectado':
            indicador.textContent = '🔴 Desconectado';
            indicador.style.backgroundColor = '#f8d7da';
            indicador.style.color = '#721c24';
            break;
        case 'error':
            indicador.textContent = '⚠️ Error Conexión';
            indicador.style.backgroundColor = '#fff3cd';
            indicador.style.color = '#856404';
            break;
        default:
            indicador.textContent = '⚪ Conectando...';
            indicador.style.backgroundColor = '#e2e3e5';
            indicador.style.color = '#383d41';
    }
}

/**
 * Polling como fallback (si WebSocket falla)
 */
let pollingInterval = null;

function iniciarPolling(sistemaId) {
    detenerPolling();
    
    console.log('🔄 Iniciando polling cada 4 segundos...');
    
    // Cargar datos inmediatamente
    cargarDatosTendenciasPolling(sistemaId);
    
    // Continuar cada 4 segundos
    pollingInterval = setInterval(() => {
        cargarDatosTendenciasPolling(sistemaId);
    }, 4000);
}

function detenerPolling() {
    if (pollingInterval) {
        clearInterval(pollingInterval);
        pollingInterval = null;
    }
}

async function cargarDatosTendenciasPolling(sistemaId) {
    try {
        const response = await fetch(`/monitoreo/api/datos-tendencias/${sistemaId}/`);
        const data = await response.json();
        
        if (data.success && window.actualizarGraficaTendencias) {
            window.actualizarGraficaTendencias(data);
        }
    } catch (error) {
        console.error('❌ Error en polling:', error);
    }
}

// Limpiar al salir de la página
window.addEventListener('beforeunload', () => {
    desconectarWebSocket();
    detenerPolling();
});
