// ====================================================================
// CHARTS.JS - Funciones para renderizar gráficos con Chart.js
// ====================================================================

// Función genérica para renderizar cualquier gráfico de flujo
function renderGrafico(datos, tipoGrafico, chartInstance, configGrafico, modoTiempoReal = false) {
    const ctx = document.getElementById(configGrafico.canvasId).getContext('2d');
    
    const labels = datos.datos.map(item => item.fecha);
    const valores = datos.datos.map(item => item.valor);
    
    // Si el gráfico existe y estamos en modo tiempo real, solo actualizar datos sin animación
    if (chartInstance && modoTiempoReal) {
        chartInstance.data.labels = labels;
        chartInstance.data.datasets[0].data = valores;
        chartInstance.update('none'); // Sin animación
        return chartInstance;
    }
    
    // Destruir gráfico existente si hay uno (solo cuando no es tiempo real)
    if (chartInstance) {
        chartInstance.destroy();
    }
    
    const nuevoChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: `${configGrafico.label} (${datos.unidad})`,
                data: valores,
                borderColor: configGrafico.color,
                backgroundColor: configGrafico.colorFondo,
                tension: 0.3,
                pointRadius: 1,
                pointHoverRadius: 4,
                borderWidth: 2,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { 
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: configGrafico.color,
                    borderWidth: 1,
                    callbacks: {
                        title: function(tooltipItems) {
                            return 'Fecha: ' + tooltipItems[0].label;
                        },
                        label: function(tooltipItem) {
                            return `${tooltipItem.dataset.label}: ${tooltipItem.parsed.y.toFixed(2)}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: { 
                        display: true, 
                        text: 'Fecha y Hora',
                        color: '#666',
                        font: { size: 12, weight: 'bold' }
                    },
                    ticks: { 
                        maxRotation: 45, 
                        minRotation: 45, 
                        autoSkip: true,
                        maxTicksLimit: 10,
                        color: '#666'
                    },
                    grid: {
                        color: '#e0e0e0',
                        lineWidth: 0.5
                    }
                },
                y: {
                    title: { 
                        display: true, 
                        text: `${configGrafico.label} (${datos.unidad})`,
                        color: '#666',
                        font: { size: 12, weight: 'bold' }
                    },
                    beginAtZero: false,
                    ticks: {
                        color: '#666',
                        callback: function(value) {
                            return value.toFixed(1);
                        }
                    },
                    grid: {
                        color: '#e0e0e0',
                        lineWidth: 0.5
                    }
                }
            },
            animation: {
                duration: modoTiempoReal ? 0 : 750,
                easing: 'easeInOutQuart'
            },
            interaction: {
                intersect: false,
                mode: 'index'
            },
            hover: {
                mode: 'nearest',
                intersect: false
            }
        }
    });
    
    return nuevoChart;
}

// Función para renderizar gráfico de flujo volumétrico CON DATOS REALES
function renderGraficoFlujoVolumetrico(datosVolumetrico, esTiempoReal = false) {
    window.chartFlujoVolumetrico = renderGrafico(
        datosVolumetrico, 
        'volumetrico', 
        window.chartFlujoVolumetrico, 
        CONFIG.GRAFICOS.FLUJO_VOLUMETRICO,
        esTiempoReal
    );
}

// Función para renderizar gráfico de flujo másico CON DATOS REALES
function renderGraficoFlujoMasico(datosMasico, esTiempoReal = false) {
    window.chartFlujoMasico = renderGrafico(
        datosMasico, 
        'masico', 
        window.chartFlujoMasico, 
        CONFIG.GRAFICOS.FLUJO_MASICO,
        esTiempoReal
    );
}

// Función para renderizar gráfico de presión CON DATOS REALES
function renderGraficoPresion(datosPresion, esTiempoReal = false) {
    window.chartPresion = renderGrafico(
        datosPresion, 
        'presion', 
        window.chartPresion, 
        CONFIG.GRAFICOS.PRESION,
        esTiempoReal
    );
}

// Función para renderizar gráficos vacíos con mensaje de error
function renderGraficosVacios(mensaje) {
    const datosVacios = {
        datos: [{ fecha: 'Sin datos', valor: 0 }],
        unidad: ''
    };
    
    // Usar la función genérica para ambos gráficos vacíos
    chartFlujoVolumetrico = renderGraficoVacio(datosVacios, mensaje, CONFIG.GRAFICOS.FLUJO_VOLUMETRICO);
    chartFlujoMasico = renderGraficoVacio(datosVacios, mensaje, CONFIG.GRAFICOS.FLUJO_MASICO);
}

// Función para renderizar gráfico de presión vacío
function renderGraficoPresionVacio(mensaje) {
    const datosVacios = {
        datos: [{ fecha: 'Sin datos', valor: 0 }],
        unidad: ''
    };
    
    chartPresion = renderGraficoVacio(datosVacios, mensaje, CONFIG.GRAFICOS.PRESION);
}

// Función auxiliar para renderizar un gráfico vacío
function renderGraficoVacio(datosVacios, mensaje, configGrafico) {
    const ctx = document.getElementById(configGrafico.canvasId).getContext('2d');
    
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Sin datos'],
            datasets: [{
                label: mensaje,
                data: [0],
                borderColor: '#6c757d',
                backgroundColor: '#6c757d20'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: { display: true, text: mensaje }
            }
        }
    });
}

// ====================================================================
// FUNCIONES PARA TEMPERATURA
// ====================================================================

// Función para renderizar gráficos de temperatura CON DATOS REALES
function renderGraficosTemperatura(data, esTiempoReal = false) {
    // Renderizar gráfico de temperatura Coriolis
    if (data.coriolis_temperature && data.coriolis_temperature.datos.length > 0) {
        renderGraficoTemperaturaCoriolis(data.coriolis_temperature, esTiempoReal);
    } else {
        renderGraficoTemperaturaCoriolisVacio('Sin datos de temperatura Coriolis');
    }
    
    // Renderizar gráfico de temperatura Diagnóstico
    if (data.diagnostic_temperature && data.diagnostic_temperature.datos.length > 0) {
        renderGraficoTemperaturaDiagnostic(data.diagnostic_temperature, esTiempoReal);
    } else {
        renderGraficoTemperaturaDiagnosticVacio('Sin datos de temperatura diagnóstico');
    }
    
    // Renderizar gráfico de temperatura Redundante
    if (data.redundant_temperature && data.redundant_temperature.datos.length > 0) {
        renderGraficoTemperaturaRedundant(data.redundant_temperature, esTiempoReal);
    } else {
        renderGraficoTemperaturaRedundantVacio('Sin datos de temperatura redundante');
    }
}

// Función para renderizar gráfico de temperatura Coriolis
function renderGraficoTemperaturaCoriolis(datosCoriolis, esTiempoReal = false) {
    window.chartTemperaturaCoriolis = renderGrafico(
        datosCoriolis, 
        'temperatura_coriolis', 
        window.chartTemperaturaCoriolis, 
        CONFIG.GRAFICOS.TEMPERATURA_CORIOLIS,
        esTiempoReal
    );
}

// Función para renderizar gráfico de temperatura Diagnóstico
function renderGraficoTemperaturaDiagnostic(datosDiagnostic, esTiempoReal = false) {
    window.chartTemperatureDiagnostic = renderGrafico(
        datosDiagnostic, 
        'temperatura_diagnostic', 
        window.chartTemperatureDiagnostic, 
        CONFIG.GRAFICOS.TEMPERATURA_DIAGNOSTIC,
        esTiempoReal
    );
}

// Función para renderizar gráfico de temperatura Redundante
function renderGraficoTemperaturaRedundant(datosRedundant, esTiempoReal = false) {
    window.chartTemperaturaRedundant = renderGrafico(
        datosRedundant, 
        'temperatura_redundant', 
        window.chartTemperaturaRedundant, 
        CONFIG.GRAFICOS.TEMPERATURA_REDUNDANT,
        esTiempoReal
    );
}

// Funciones para renderizar gráficos vacíos de temperatura
function renderGraficosTemperaturaVacios(mensaje) {
    renderGraficoTemperaturaCoriolisVacio(mensaje);
    renderGraficoTemperaturaDiagnosticVacio(mensaje);
    renderGraficoTemperaturaRedundantVacio(mensaje);
}

function renderGraficoTemperaturaCoriolisVacio(mensaje) {
    // Destruir gráfico existente si existe
    if (window.chartTemperaturaCoriolis) {
        window.chartTemperaturaCoriolis.destroy();
        window.chartTemperaturaCoriolis = null;
    }
    
    const datosVacios = {
        datos: [{ fecha: 'Sin datos', valor: 0 }],
        unidad: ''
    };
    
    window.chartTemperaturaCoriolis = renderGraficoVacio(datosVacios, mensaje, CONFIG.GRAFICOS.TEMPERATURA_CORIOLIS);
}

function renderGraficoTemperaturaDiagnosticVacio(mensaje) {
    // Destruir gráfico existente si existe
    if (window.chartTemperatureDiagnostic) {
        window.chartTemperatureDiagnostic.destroy();
        window.chartTemperatureDiagnostic = null;
    }
    
    const datosVacios = {
        datos: [{ fecha: 'Sin datos', valor: 0 }],
        unidad: ''
    };
    
    window.chartTemperatureDiagnostic = renderGraficoVacio(datosVacios, mensaje, CONFIG.GRAFICOS.TEMPERATURA_DIAGNOSTIC);
}

function renderGraficoTemperaturaRedundantVacio(mensaje) {
    // Destruir gráfico existente si existe
    if (window.chartTemperaturaRedundant) {
        window.chartTemperaturaRedundant.destroy();
        window.chartTemperaturaRedundant = null;
    }
    
    const datosVacios = {
        datos: [{ fecha: 'Sin datos', valor: 0 }],
        unidad: ''
    };
    
    window.chartTemperaturaRedundant = renderGraficoVacio(datosVacios, mensaje, CONFIG.GRAFICOS.TEMPERATURA_REDUNDANT);
}