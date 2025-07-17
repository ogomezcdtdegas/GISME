/**
 * JavaScript para Coriolis Hybrid - Monitoreo en Tiempo Real
 * Maneja gráficos, métricas y actualización de datos
 */

// Variables globales para la gráfica
let trendChart;
let chartData = {
    labels: [],
    datasets: [
        {
            label: 'Presión (PSI)',
            data: [],
            borderColor: '#28a745',
            backgroundColor: 'rgba(40, 167, 69, 0.1)',
            tension: 0.4,
            fill: true
        },
        {
            label: 'Flujo (m³/h)',
            data: [],
            borderColor: '#007bff',
            backgroundColor: 'rgba(0, 123, 255, 0.1)',
            tension: 0.4,
            fill: true
        },
        {
            label: 'Temperatura (°C)',
            data: [],
            borderColor: '#dc3545',
            backgroundColor: 'rgba(220, 53, 69, 0.1)',
            tension: 0.4,
            fill: true
        },
        {
            label: 'Densidad (kg/m³)',
            data: [],
            borderColor: '#ffc107',
            backgroundColor: 'rgba(255, 193, 7, 0.1)',
            tension: 0.4,
            fill: true,
            yAxisID: 'y1'
        }
    ]
};

// Valores base para simulación
let baseValues = {
    pressure: 125,
    flow: 87,
    temperature: 25,
    density: 0.82
};

// Función para obtener información del sistema desde el contexto de Django
function getSistemaContext() {
    const sistemaTag = document.querySelector('[data-sistema-tag]')?.dataset.sistemaTag || '';
    const sistemaId = document.querySelector('[data-sistema-id]')?.dataset.sistemaId || '';
    return { sistemaTag, sistemaId };
}

// Inicializar gráfica
function initChart() {
    const ctx = document.getElementById('trendChart');
    if (!ctx) return;

    const { sistemaTag, sistemaId } = getSistemaContext();

    trendChart = new Chart(ctx, {
        type: 'line',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 100,
                easing: 'linear'
            },
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                title: {
                    display: true,
                    text: `Sistema ${sistemaTag} ${sistemaId} - Tendencias en Tiempo Real`,
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                },
                legend: {
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 20
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0,0,0,0.8)',
                    titleColor: 'white',
                    bodyColor: 'white',
                    borderColor: '#007bff',
                    borderWidth: 1
                }
            },
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Tiempo'
                    },
                    ticks: {
                        maxTicksLimit: 20
                    }
                },
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Presión / Flujo / Temperatura'
                    },
                    grid: {
                        color: 'rgba(0,0,0,0.1)'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Densidad (kg/m³)'
                    },
                    grid: {
                        drawOnChartArea: false,
                    },
                }
            }
        }
    });

    // Llenar datos iniciales
    const now = new Date();
    for (let i = 19; i >= 0; i--) {
        const time = new Date(now.getTime() - i * 100);
        addDataPoint(time);
    }
}

// Agregar punto de datos
function addDataPoint(time) {
    const timeStr = time.toLocaleTimeString('es-ES', {hour: '2-digit', minute: '2-digit', second: '2-digit', fractionalSecondDigits: 1});
    
    // Simular variaciones realistas
    const pressure = baseValues.pressure + (Math.random() - 0.5) * 10;
    const flow = Math.max(0, baseValues.flow + (Math.random() - 0.5) * 15);
    const temperature = baseValues.temperature + (Math.random() - 0.5) * 3;
    const density = Math.max(0, baseValues.density + (Math.random() - 0.5) * 0.05);

    // Actualizar valores base con tendencia ligera
    baseValues.pressure += (Math.random() - 0.5) * 0.5;
    baseValues.flow += (Math.random() - 0.5) * 0.3;
    baseValues.temperature += (Math.random() - 0.5) * 0.1;
    baseValues.density += (Math.random() - 0.5) * 0.001;

    // Mantener rangos realistas
    baseValues.pressure = Math.max(100, Math.min(150, baseValues.pressure));
    baseValues.flow = Math.max(60, Math.min(120, baseValues.flow));
    baseValues.temperature = Math.max(20, Math.min(35, baseValues.temperature));
    baseValues.density = Math.max(0.7, Math.min(0.9, baseValues.density));

    // Agregar datos al gráfico
    chartData.labels.push(timeStr);
    chartData.datasets[0].data.push(pressure.toFixed(1));
    chartData.datasets[1].data.push(flow.toFixed(1));
    chartData.datasets[2].data.push(temperature.toFixed(1));
    chartData.datasets[3].data.push(density.toFixed(3));

    // Mantener solo los últimos 20 puntos
    if (chartData.labels.length > 20) {
        chartData.labels.shift();
        chartData.datasets.forEach(dataset => dataset.data.shift());
    }

    // Actualizar gráfico
    if (trendChart) {
        trendChart.update('none'); // Usar 'none' para evitar animaciones y permitir actualizaciones más rápidas
    }

    // Actualizar valores en tiempo real en la interfaz
    updateMetrics(pressure, flow, temperature, density);
}

// Actualizar métricas en la interfaz
function updateMetrics(pressure, flow, temperature, density) {
    const elements = {
        'current-pressure': pressure.toFixed(1),
        'current-flow': flow.toFixed(1),
        'current-temp': temperature.toFixed(1),
        'current-density': density.toFixed(3)
    };

    Object.entries(elements).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) {
            const oldValue = parseFloat(element.textContent);
            const newValue = parseFloat(value);
            
            element.textContent = value;
            
            // Aplicar clase de tendencia
            element.className = element.className.replace(/trend-\w+/g, '');
            if (newValue > oldValue) {
                element.classList.add('metric-value', 'trend-up');
            } else if (newValue < oldValue) {
                element.classList.add('metric-value', 'trend-down');
            } else {
                element.classList.add('metric-value', 'trend-stable');
            }
        }
    });
}

// Countdown para próxima actualización
function initCountdown() {
    let countdown = 10;
    setInterval(() => {
        const countdownElement = document.getElementById('countdown');
        if (countdownElement) {
            countdown--;
            if (countdown <= 0) countdown = 10;
            countdownElement.textContent = (countdown / 10).toFixed(1);
        }
    }, 100);
}

// Inicializar cuando el documento esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Solo inicializar si estamos en la vista de monitoreo (no en selector)
    if (document.getElementById('trendChart')) {
        console.log('Iniciando monitoreo en tiempo real...');
        initChart();
        initCountdown();
        
        // Actualizar datos cada 100ms
        setInterval(() => {
            addDataPoint(new Date());
        }, 100);
    }
});
