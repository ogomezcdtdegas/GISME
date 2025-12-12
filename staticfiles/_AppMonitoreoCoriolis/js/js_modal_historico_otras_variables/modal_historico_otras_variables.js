/**
 * JavaScript para el modal de histórico de otras variables del sistema
 * Incluye: Presión, Flujo Másico, Temperatura Salida, Frecuencia, Densidad,
 * Intensidad Señal Gateway y Temperatura Gateway
 */

let chartOtrasVariables = null;
let sistemaIdActualOtrasVars = null;
let cargaInicial = true;

// Función para abrir el modal
function abrirModalOtrasVariables(sistemaId) {
    sistemaIdActualOtrasVars = sistemaId;
    cargaInicial = true;
    
    // Configurar fechas iniciales (últimas 3 horas)
    const ahora = new Date();
    const hace3Horas = new Date(ahora.getTime() - (3 * 60 * 60 * 1000));
    
    document.getElementById('fechaInicioOtrasVars').value = formatearFechaParaInput(hace3Horas);
    document.getElementById('fechaFinOtrasVars').value = formatearFechaParaInput(ahora);
    
    // Restablecer checkboxes de escalas a su estado inicial
    document.getElementById('scalePresion').checked = true;
    document.getElementById('scaleTempSalida').checked = true;
    document.getElementById('scaleFrecuencia').checked = false;
    document.getElementById('scaleDensidad').checked = false;
    document.getElementById('scaleIntensidadGateway').checked = false;
    document.getElementById('scaleTempGateway').checked = false;
    
    // Mostrar el modal
    const modal = new bootstrap.Modal(document.getElementById('modalHistoricoOtrasVariables'));
    modal.show();
    
    // Cargar datos iniciales (últimas 3 horas desde último dato)
    cargarDatosOtrasVariables();
    
    // Configurar listeners para checkboxes
    configurarListenersCheckboxes();
}

// Función para formatear fecha para input datetime-local
function formatearFechaParaInput(fecha) {
    const year = fecha.getFullYear();
    const month = String(fecha.getMonth() + 1).padStart(2, '0');
    const day = String(fecha.getDate()).padStart(2, '0');
    const hours = String(fecha.getHours()).padStart(2, '0');
    const minutes = String(fecha.getMinutes()).padStart(2, '0');
    return `${year}-${month}-${day}T${hours}:${minutes}`;
}

// Función para cargar datos desde el API
function cargarDatosOtrasVariables() {
    if (!sistemaIdActualOtrasVars) {
        console.error('No hay sistema seleccionado');
        return;
    }
    
    let url;
    
    // En la carga inicial, usar tiempo_real=true (últimas 3 horas desde último dato)
    if (cargaInicial) {
        url = `/monitoreo/api/datos-otras-variables/${sistemaIdActualOtrasVars}/?tiempo_real=true&horas_atras=3`;
        //console.log('📊 Cargando otras variables (últimas 3 horas desde último dato):', url);
    } else {
        // En búsquedas personalizadas, usar las fechas seleccionadas
        const fechaInicio = document.getElementById('fechaInicioOtrasVars').value + ':00';
        const fechaFin = document.getElementById('fechaFinOtrasVars').value + ':00';
        url = `/monitoreo/api/datos-otras-variables/${sistemaIdActualOtrasVars}/?fecha_inicio=${fechaInicio}&fecha_fin=${fechaFin}`;
        //console.log('📊 Cargando otras variables (rango personalizado):', url);
    }
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            //console.log('✅ Datos recibidos:', data);
            
            if (data.success) {
                renderizarGraficoOtrasVariables(data);
                actualizarInfoModal(data);
            } else {
                console.error('❌ Error en respuesta:', data.error);
                mostrarError(data.error || 'Error al cargar datos');
            }
        })
        .catch(error => {
            console.error('❌ Error en fetch:', error);
            mostrarError('Error de conexión al cargar datos');
        });
}

// Función para renderizar el gráfico con Chart.js
function renderizarGraficoOtrasVariables(data) {
    const ctx = document.getElementById('chartOtrasVariables');
    
    if (!ctx) {
        console.error('Canvas no encontrado');
        return;
    }
    
    // Destruir gráfico anterior si existe
    if (chartOtrasVariables) {
        chartOtrasVariables.destroy();
    }
    
    // Preparar datasets para cada variable
    const datasets = [];
    
    // Flujo Másico (kg/min) - EJE IZQUIERDO - VISIBLE POR DEFECTO
    if (data.flujo_masico && data.flujo_masico.datos && data.flujo_masico.datos.length > 0) {
        datasets.push({
            label: 'Flujo Másico (kg/min)',
            data: data.flujo_masico.datos.map(d => ({ x: d.timestamp, y: d.valor })),
            borderColor: '#3498db',
            backgroundColor: 'rgba(52, 152, 219, 0.1)',
            yAxisID: 'y-flujo',
            hidden: false,
            tension: 0.4,
            pointRadius: 2,
            borderWidth: 2
        });
    }
    
    // Presión (PSI) - EJE DERECHO - VISIBLE POR DEFECTO
    if (data.presion && data.presion.datos && data.presion.datos.length > 0) {
        datasets.push({
            label: 'Presión (PSI)',
            data: data.presion.datos.map(d => ({ x: d.timestamp, y: d.valor })),
            borderColor: '#e74c3c',
            backgroundColor: 'rgba(231, 76, 60, 0.1)',
            yAxisID: 'y-presion',
            hidden: false,
            tension: 0.4,
            pointRadius: 2
        });
    }
    
    // Temperatura Salida (°F) - EJE DERECHO - VISIBLE POR DEFECTO
    if (data.temperatura_salida && data.temperatura_salida.datos && data.temperatura_salida.datos.length > 0) {
        datasets.push({
            label: 'Temp. Salida (°F)',
            data: data.temperatura_salida.datos.map(d => ({ x: d.timestamp, y: d.valor })),
            borderColor: '#e67e22',
            backgroundColor: 'rgba(230, 126, 34, 0.1)',
            yAxisID: 'y-temp-salida',
            hidden: false,
            tension: 0.4,
            pointRadius: 2
        });
    }
    
    // Frecuencia (Hz) - EJE DERECHO - OCULTA POR DEFECTO
    if (data.frecuencia && data.frecuencia.datos && data.frecuencia.datos.length > 0) {
        datasets.push({
            label: 'Frecuencia (Hz)',
            data: data.frecuencia.datos.map(d => ({ x: d.timestamp, y: d.valor })),
            borderColor: '#9b59b6',
            backgroundColor: 'rgba(155, 89, 182, 0.1)',
            yAxisID: 'y-frecuencia',
            hidden: true,
            tension: 0.4,
            pointRadius: 2
        });
    }
    
    // Densidad (g/cc) - EJE DERECHO - OCULTA POR DEFECTO
    if (data.densidad && data.densidad.datos && data.densidad.datos.length > 0) {
        datasets.push({
            label: 'Densidad (g/cc)',
            data: data.densidad.datos.map(d => ({ x: d.timestamp, y: d.valor })),
            borderColor: '#f39c12',
            backgroundColor: 'rgba(243, 156, 18, 0.1)',
            yAxisID: 'y-densidad',
            hidden: true,
            tension: 0.4,
            pointRadius: 2
        });
    }
    
    // Intensidad Señal Gateway (dB) - EJE DERECHO - OCULTA POR DEFECTO
    if (data.intensidad_gateway && data.intensidad_gateway.datos && data.intensidad_gateway.datos.length > 0) {
        datasets.push({
            label: 'Señal Gateway (dB)',
            data: data.intensidad_gateway.datos.map(d => ({ x: d.timestamp, y: d.valor })),
            borderColor: '#16a085',
            backgroundColor: 'rgba(22, 160, 133, 0.1)',
            yAxisID: 'y-intensidad-gateway',
            hidden: true,
            tension: 0.4,
            pointRadius: 2
        });
    }
    
    // Temperatura Gateway (°C) - EJE DERECHO - OCULTA POR DEFECTO
    if (data.temperatura_gateway && data.temperatura_gateway.datos && data.temperatura_gateway.datos.length > 0) {
        datasets.push({
            label: 'Temp. Gateway (°C)',
            data: data.temperatura_gateway.datos.map(d => ({ x: d.timestamp, y: d.valor })),
            borderColor: '#c0392b',
            backgroundColor: 'rgba(192, 57, 43, 0.1)',
            yAxisID: 'y-temp-gateway',
            hidden: true,
            tension: 0.4,
            pointRadius: 2
        });
    }
    
    // Configuración del gráfico
    chartOtrasVariables = new Chart(ctx, {
        type: 'line',
        data: { datasets: datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: { duration: 0 },
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    enabled: true,
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.parsed.y.toFixed(2)}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'minute',
                        displayFormats: {
                            minute: 'HH:mm',
                            hour: 'HH:mm'
                        }
                    },
                    title: {
                        display: true,
                        text: 'Tiempo'
                    }
                },
                'y-flujo': {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Flujo Másico (kg/min)',
                        color: '#3498db'
                    },
                    ticks: {
                        color: '#3498db'
                    },
                    grid: {
                        drawOnChartArea: true,
                        color: 'rgba(52, 152, 219, 0.1)'
                    }
                },
                'y-presion': {
                    type: 'linear',
                    display: document.getElementById('scalePresion')?.checked || false,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Presión (PSI)',
                        color: '#e74c3c'
                    },
                    ticks: {
                        color: '#e74c3c'
                    },
                    grid: {
                        drawOnChartArea: false
                    }
                },
                'y-temp-salida': {
                    type: 'linear',
                    display: document.getElementById('scaleTempSalida')?.checked || false,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Temp. Salida (°F)',
                        color: '#e67e22'
                    },
                    ticks: {
                        color: '#e67e22'
                    },
                    grid: {
                        drawOnChartArea: false
                    }
                },
                'y-frecuencia': {
                    type: 'linear',
                    display: document.getElementById('scaleFrecuencia')?.checked || false,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Frecuencia (Hz)',
                        color: '#9b59b6'
                    },
                    ticks: {
                        color: '#9b59b6'
                    },
                    grid: {
                        drawOnChartArea: false
                    }
                },
                'y-densidad': {
                    type: 'linear',
                    display: document.getElementById('scaleDensidad')?.checked || false,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Densidad (g/cc)',
                        color: '#f39c12'
                    },
                    ticks: {
                        color: '#f39c12'
                    },
                    grid: {
                        drawOnChartArea: false
                    }
                },
                'y-intensidad-gateway': {
                    type: 'linear',
                    display: document.getElementById('scaleIntensidadGateway')?.checked || false,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Señal Gateway (dB)',
                        color: '#16a085'
                    },
                    ticks: {
                        color: '#16a085'
                    },
                    grid: {
                        drawOnChartArea: false
                    }
                },
                'y-temp-gateway': {
                    type: 'linear',
                    display: document.getElementById('scaleTempGateway')?.checked || false,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Temp. Gateway (°C)',
                        color: '#c0392b'
                    },
                    ticks: {
                        color: '#c0392b'
                    },
                    grid: {
                        drawOnChartArea: false
                    }
                }
            }
        }
    });
    
    //console.log('📊 Gráfico renderizado con', datasets.length, 'variables');
}

// Función para actualizar información del modal
function actualizarInfoModal(data) {
    // Total de registros
    const totalRegistros = data.decimacion_info && data.decimacion_info.aplicada 
        ? data.decimacion_info.total_decimado 
        : (data.presion ? data.presion.total_registros : 0);
    
    document.getElementById('totalRegistrosOtrasVars').textContent = `${totalRegistros} registros`;
    
    // Mostrar/ocultar info de decimación
    if (data.decimacion_info && data.decimacion_info.aplicada) {
        //console.log(`🔍 Decimación aplicada: ${data.decimacion_info.total_decimado} de ${data.decimacion_info.total_original} registros (${data.decimacion_info.porcentaje_reduccion}% reducción)`);
    }
}

// Función para configurar listeners de checkboxes
function configurarListenersCheckboxes() {
    // Solo checkboxes para activar/desactivar escalas
    const checkboxesEscalas = [
        { id: 'scalePresion', axis: 'y-presion' },
        { id: 'scaleTempSalida', axis: 'y-temp-salida' },
        { id: 'scaleFrecuencia', axis: 'y-frecuencia' },
        { id: 'scaleDensidad', axis: 'y-densidad' },
        { id: 'scaleIntensidadGateway', axis: 'y-intensidad-gateway' },
        { id: 'scaleTempGateway', axis: 'y-temp-gateway' }
    ];
    
    checkboxesEscalas.forEach(item => {
        const checkbox = document.getElementById(item.id);
        if (checkbox) {
            checkbox.addEventListener('change', function() {
                if (chartOtrasVariables) {
                    chartOtrasVariables.options.scales[item.axis].display = this.checked;
                    chartOtrasVariables.update();
                }
            });
        }
    });
}

// Función para buscar con fechas personalizadas
function buscarOtrasVariables() {
    cargaInicial = false;  // Marcar que ya no es carga inicial
    cargarDatosOtrasVariables();
}

// Función para mostrar errores
function mostrarError(mensaje) {
    const chartContainer = document.querySelector('#chartOtrasVariables').parentElement;
    chartContainer.innerHTML = `
        <div class="alert alert-danger" role="alert">
            <i class="bi bi-exclamation-triangle"></i> <strong>Error:</strong> ${mensaje}
        </div>
    `;
}

// Limpiar al cerrar el modal
document.getElementById('modalHistoricoOtrasVariables')?.addEventListener('hidden.bs.modal', function() {
    if (chartOtrasVariables) {
        chartOtrasVariables.destroy();
        chartOtrasVariables = null;
    }
});
