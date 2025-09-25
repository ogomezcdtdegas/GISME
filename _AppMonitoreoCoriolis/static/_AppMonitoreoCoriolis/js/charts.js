// ====================================================================
// CHARTS.JS - Funciones para renderizar gráficos con Chart.js
// ====================================================================

// Función para renderizar gráfico de flujo volumétrico CON DATOS REALES
function renderGraficoFlujoVolumetrico(datosVolumetrico) {
    const ctx = document.getElementById('graficaFlujoVolumetrico').getContext('2d');
    
    if (chartFlujoVolumetrico) {
        chartFlujoVolumetrico.destroy();
    }
    
    const labels = datosVolumetrico.datos.map(item => item.fecha);
    const valores = datosVolumetrico.datos.map(item => item.valor);
    
    chartFlujoVolumetrico = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: `Flujo Volumétrico (${datosVolumetrico.unidad})`,
                data: valores,
                borderColor: '#007bff',
                backgroundColor: 'rgba(0, 123, 255, 0.1)',
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
                    borderColor: '#007bff',
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
                        text: `Flujo Volumétrico (${datosVolumetrico.unidad})`,
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
}

// Función para renderizar gráfico de flujo másico CON DATOS REALES
function renderGraficoFlujoMasico(datosMasico) {
    const ctx = document.getElementById('graficaFlujoMasico').getContext('2d');
    
    if (chartFlujoMasico) {
        chartFlujoMasico.destroy();
    }
    
    const labels = datosMasico.datos.map(item => item.fecha);
    const valores = datosMasico.datos.map(item => item.valor);
    
    chartFlujoMasico = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: `Flujo Másico (${datosMasico.unidad})`,
                data: valores,
                borderColor: '#28a745',
                backgroundColor: 'rgba(40, 167, 69, 0.1)',
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
                    borderColor: '#28a745',
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
                        text: `Flujo Másico (${datosMasico.unidad})`,
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
}

// Función para renderizar gráficos vacíos con mensaje de error
function renderGraficosVacios(mensaje) {
    // Flujo Volumétrico
    const ctxVol = document.getElementById('graficaFlujoVolumetrico').getContext('2d');
    if (chartFlujoVolumetrico) chartFlujoVolumetrico.destroy();
    
    chartFlujoVolumetrico = new Chart(ctxVol, {
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
    
    // Flujo Másico
    const ctxMas = document.getElementById('graficaFlujoMasico').getContext('2d');
    if (chartFlujoMasico) chartFlujoMasico.destroy();
    
    chartFlujoMasico = new Chart(ctxMas, {
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