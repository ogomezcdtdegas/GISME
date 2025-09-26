// ====================================================================
// CHARTS.JS - Funciones para renderizar gráficos con Chart.js
// ====================================================================

// Función genérica para renderizar cualquier gráfico de flujo
function renderGrafico(datos, tipoGrafico, chartInstance, configGrafico) {
    const ctx = document.getElementById(configGrafico.canvasId).getContext('2d');
    
    // Destruir gráfico existente si hay uno
    if (chartInstance) {
        chartInstance.destroy();
    }
    
    const labels = datos.datos.map(item => item.fecha);
    const valores = datos.datos.map(item => item.valor);
    
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
                duration: 750,
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
function renderGraficoFlujoVolumetrico(datosVolumetrico) {
    // Destruir gráfico existente si existe
    if (window.chartFlujoVolumetrico) {
        window.chartFlujoVolumetrico.destroy();
    }
    
    window.chartFlujoVolumetrico = renderGrafico(
        datosVolumetrico, 
        'volumetrico', 
        window.chartFlujoVolumetrico, 
        CONFIG.GRAFICOS.FLUJO_VOLUMETRICO
    );
}

// Función para renderizar gráfico de flujo másico CON DATOS REALES
function renderGraficoFlujoMasico(datosMasico) {
    // Destruir gráfico existente si existe
    if (window.chartFlujoMasico) {
        window.chartFlujoMasico.destroy();
    }
    
    window.chartFlujoMasico = renderGrafico(
        datosMasico, 
        'masico', 
        window.chartFlujoMasico, 
        CONFIG.GRAFICOS.FLUJO_MASICO
    );
}

// Función para renderizar gráfico de presión CON DATOS REALES
function renderGraficoPresion(datosPresion) {
    // Destruir gráfico existente si existe
    if (window.chartPresion) {
        console.log('🗑️ Destruyendo gráfico de presión existente');
        window.chartPresion.destroy();
        window.chartPresion = null;
    }
    
    window.chartPresion = renderGrafico(
        datosPresion, 
        'presion', 
        window.chartPresion, 
        CONFIG.GRAFICOS.PRESION
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