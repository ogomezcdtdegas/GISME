/**
 * JavaScript para Coriolis SPA
 * Single Page Application para monitoreo de sistemas
 */

// Namespace para SPA para evitar conflictos
const CoriolisSPA = {
    // Variables del SPA
    sistemasData: [],
    filteredSistemas: [],
    currentSortField: '',
    currentSortDirection: 'asc',
    currentSistema: null,
    spaMap: null,  // Renombrado para evitar conflicto
    trendChart: null,

    // Función para obtener CSRF token
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    },

    // Router básico para SPA
    initRouter() {
        const path = window.location.pathname;
        const sistemaIdMatch = path.match(/\/monitoreo\/([a-f0-9-]+)\//);
        
        if (sistemaIdMatch) {
            const sistemaId = sistemaIdMatch[1];
            this.loadSistemaDetail(sistemaId);
        } else {
            this.showSelectorView();
        }
    },

    // Mostrar vista de selección
    showSelectorView() {
        // Mostrar la vista de selección
        this.showView('sistema-selector-view');
        
        // Cargar sistemas
        this.loadSistemas().then(() => {
            this.renderSistemasTable();
        }).catch(error => {
            console.error('Error al cargar sistemas:', error);
            this.showError('Error al cargar la lista de sistemas');
        });
        
        // Actualizar URL
        this.updateURL('selector');
    },

    // Cargar lista de sistemas
    async loadSistemas() {
        try {
            const response = await fetch('/complementos/listar-todo-sistemas/', {
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin'
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            this.sistemasData = data.results || data;
            this.filteredSistemas = [...this.sistemasData];
            
            console.log('Sistemas cargados:', this.sistemasData.length);
            
        } catch (error) {
            console.error('Error cargando sistemas:', error);
            throw error;
        }
    },

    // Cargar detalle del sistema
    async loadSistemaDetail(sistemaId) {
        try {
            this.showLoadingOverlay();
            
            // Cargar sistemas si no están cargados
            if (this.sistemasData.length === 0) {
                await this.loadSistemas();
            }
            
            const sistema = this.sistemasData.find(s => s.id.toString() === sistemaId.toString());
            
            if (!sistema) {
                console.error('Sistema no encontrado:', sistemaId);
                this.showSelectorView();
                return;
            }
            
            this.currentSistema = sistema;
            this.showMonitoringView(sistema);
            
        } catch (error) {
            console.error('Error cargando detalle del sistema:', error);
            this.hideLoadingOverlay();
            this.showError('Error al cargar información del sistema');
        }
    },

    // Mostrar vista de monitoreo
    showMonitoringView(sistema) {
        // Actualizar información del sistema
        const sistemaTitle = document.getElementById('sistemaTitle');
        const breadcrumbSistema = document.getElementById('breadcrumbSistema');
        
        if (sistemaTitle) {
            sistemaTitle.innerHTML = `<i class="bi bi-diagram-3"></i> ${sistema.tag} ${sistema.sistema_id}`;
        }
        if (breadcrumbSistema) {
            breadcrumbSistema.textContent = `${sistema.tag} ${sistema.sistema_id}`;
        }
        
        // Mostrar la vista de monitoreo
        this.showView('sistema-monitoring-view');
        
        // Actualizar URL
        this.updateURL('monitoring', sistema.id);
        
        // Cargar datos del sistema
        this.loadSistemaData(sistema);
        
        // Inicializar mapa del sistema
        this.initSistemaMap(sistema);
        
        // Inicializar gráfico con un pequeño delay
        setTimeout(() => this.initTrendChart(), 200);
        
        this.hideLoadingOverlay();
    },

    // Inicializar mapa del sistema
    initSistemaMap(sistema) {
        const mapContainer = document.getElementById('sistemaMap');
        if (!mapContainer) return;
        
        // Limpiar mapa anterior si existe
        if (this.spaMap) {
            this.spaMap.remove();
        }
        
        try {
            // Verificar que Leaflet esté disponible
            if (typeof L === 'undefined') {
                console.error('Leaflet no está disponible');
                mapContainer.innerHTML = '<div class="alert alert-warning">Error: Leaflet no disponible</div>';
                return;
            }
            
            // Validar coordenadas
            const lat = parseFloat(sistema.ubicacion_lat);
            const lng = parseFloat(sistema.ubicacion_lng);
            
            if (isNaN(lat) || isNaN(lng)) {
                console.warn('Coordenadas no válidas para el sistema:', sistema);
                mapContainer.innerHTML = '<div class="alert alert-info">Sin coordenadas disponibles para este sistema</div>';
                return;
            }
            
            // Crear mapa
            this.spaMap = L.map('sistemaMap').setView([lat, lng], 15);
            
            // Agregar tiles
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors'
            }).addTo(this.spaMap);
            
            // Icono del sistema
            const sistemaIcon = L.divIcon({
                html: '<i class="bi bi-gear-fill text-primary" style="font-size: 20px;"></i>',
                iconSize: [25, 25],
                className: 'custom-marker'
            });
            
            // Agregar marcador
            L.marker([lat, lng], { icon: sistemaIcon })
            .addTo(this.spaMap)
            .bindPopup(`
                <div class="text-center">
                    <h6><i class="bi bi-gear"></i> ${sistema.tag} ${sistema.sistema_id}</h6>
                    <p class="mb-1"><strong>Ubicación:</strong> ${sistema.ubicacion_nombre}</p>
                    <p class="mb-0"><strong>Coordenadas:</strong><br>${sistema.ubicacion_lat}, ${sistema.ubicacion_lng}</p>
                </div>
            `)
            .openPopup();
            
        } catch (error) {
            console.error('Error inicializando mapa del sistema:', error);
            mapContainer.innerHTML = '<div class="alert alert-warning">Error al cargar el mapa</div>';
        }
    },

    // Renderizar tabla de sistemas
    renderSistemasTable() {
        const tbody = document.getElementById('sistemasTableBody');
        if (!tbody) return;
        
        if (this.filteredSistemas.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center text-muted">
                        <i class="bi bi-info-circle"></i> No se encontraron sistemas
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = this.filteredSistemas.map(sistema => `
            <tr>
                <td><strong class="text-primary">${sistema.tag}</strong></td>
                <td>${sistema.sistema_id}</td>
                <td>
                    <i class="bi bi-geo-alt text-success"></i> ${sistema.ubicacion_nombre}
                </td>
                <td><small class="text-muted">${sistema.ubicacion_coordenadas}</small></td>
                <td>
                    <button class="btn btn-primary btn-sm me-1" onclick="window.location.href='/monitoreo/sistema/${sistema.id}/'">
                        <i class="bi bi-activity"></i> Monitorear
                    </button>
                    <button class="btn btn-outline-secondary btn-sm" 
                            onclick="showMapModal('${sistema.ubicacion_lat}', '${sistema.ubicacion_lng}', '${sistema.tag}', '${sistema.sistema_id}', '${sistema.ubicacion_nombre}')">
                        <i class="bi bi-geo-alt"></i>
                    </button>
                </td>
            </tr>
        `).join('');
    },

    // Cargar datos del sistema específico
    loadSistemaData(sistema) {
        const sistemaInfo = document.getElementById('sistemaInfo');
        if (!sistemaInfo) return;
        
        // Simular carga de datos (en producción vendría de una API específica)
        sistemaInfo.innerHTML = `
            <div class="row">
                <div class="col-md-6 mb-3">
                    <div class="metric-card">
                        <h6 class="text-success"><i class="bi bi-speedometer2"></i> Presión</h6>
                        <h3 id="currentPressure" class="metric-value">125.3 PSI</h3>
                        <small class="text-muted">Normal</small>
                    </div>
                </div>
                <div class="col-md-6 mb-3">
                    <div class="metric-card">
                        <h6 class="text-primary"><i class="bi bi-water"></i> Flujo</h6>
                        <h3 id="currentFlow" class="metric-value">87.2 m³/h</h3>
                        <small class="text-muted">Normal</small>
                    </div>
                </div>
                <div class="col-md-6 mb-3">
                    <div class="metric-card">
                        <h6 class="text-warning"><i class="bi bi-thermometer-half"></i> Temperatura</h6>
                        <h3 id="currentTemp" class="metric-value">24.8 °C</h3>
                        <small class="text-muted">Normal</small>
                    </div>
                </div>
                <div class="col-md-6 mb-3">
                    <div class="metric-card">
                        <h6 class="text-info"><i class="bi bi-droplet"></i> Densidad</h6>
                        <h3 id="currentDensity" class="metric-value">0.825 kg/m³</h3>
                        <small class="text-muted">Normal</small>
                    </div>
                </div>
            </div>
            
            <div class="row mt-3">
                <div class="col-12">
                    <div class="alert alert-info">
                        <i class="bi bi-info-circle"></i>
                        <strong>Estado:</strong> Sistema operativo - Última actualización: ${new Date().toLocaleString()}
                    </div>
                </div>
            </div>
        `;
        
        // Iniciar actualización en tiempo real
        this.startRealTimeUpdates();
    },

    // Actualización en tiempo real de valores
    startRealTimeUpdates() {
        // Limpiar intervalo anterior si existe
        if (window.realTimeInterval) {
            clearInterval(window.realTimeInterval);
        }
        
        window.realTimeInterval = setInterval(() => {
            // Simular cambios en los valores con variación realista
            const baseValues = {
                pressure: 125.3,
                flow: 87.2,
                temp: 24.8,
                density: 0.825
            };
            
            const pressure = baseValues.pressure + (Math.random() - 0.5) * 10;
            const flow = Math.max(0, baseValues.flow + (Math.random() - 0.5) * 15);
            const temp = baseValues.temp + (Math.random() - 0.5) * 3;
            const density = Math.max(0, baseValues.density + (Math.random() - 0.5) * 0.05);
            
            // Actualizar elementos si existen
            const elements = {
                'currentPressure': pressure.toFixed(1) + ' PSI',
                'currentFlow': flow.toFixed(1) + ' m³/h',
                'currentTemp': temp.toFixed(1) + ' °C',
                'currentDensity': density.toFixed(3) + ' kg/m³'
            };
            
            Object.entries(elements).forEach(([id, value]) => {
                const element = document.getElementById(id);
                if (element) {
                    element.textContent = value;
                    
                    // Agregar efecto de actualización
                    element.style.transition = 'color 0.3s ease';
                    element.style.color = '#007bff';
                    
                    setTimeout(() => {
                        element.style.color = '';
                    }, 300);
                }
            });
            
            // Actualizar gráfico si existe
            if (this.trendChart) {
                this.updateTrendChart(pressure, flow, temp);
            }
        }, 100); // Actualizar cada 100ms
    },

    // Inicializar gráfico de tendencias
    initTrendChart() {
        const ctx = document.getElementById('trendChart');
        if (!ctx) return;
        
        // Destruir gráfico anterior si existe
        if (this.trendChart) {
            this.trendChart.destroy();
        }
        
        // Generar datos iniciales de las últimas 2 horas
        const now = new Date();
        const labels = [];
        const pressureData = [];
        const flowData = [];
        const tempData = [];
        
        for (let i = 19; i >= 0; i--) {
            const time = new Date(now.getTime() - i * 6 * 60 * 1000); // cada 6 minutos
            labels.push(time.toLocaleTimeString());
            
            // Datos simulados con variación realista
            pressureData.push((125.3 + Math.sin(i * 0.3) * 5 + (Math.random() - 0.5) * 3).toFixed(1));
            flowData.push((87.2 + Math.cos(i * 0.2) * 8 + (Math.random() - 0.5) * 4).toFixed(1));
            tempData.push((24.8 + Math.sin(i * 0.1) * 2 + (Math.random() - 0.5) * 1).toFixed(1));
        }
        
        this.trendChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Presión (PSI)',
                        data: pressureData,
                        borderColor: '#28a745',
                        backgroundColor: 'rgba(40, 167, 69, 0.1)',
                        tension: 0.4,
                        fill: true
                    },
                    {
                        label: 'Flujo (m³/h)',
                        data: flowData,
                        borderColor: '#007bff',
                        backgroundColor: 'rgba(0, 123, 255, 0.1)',
                        tension: 0.4,
                        fill: true
                    },
                    {
                        label: 'Temperatura (°C)',
                        data: tempData,
                        borderColor: '#dc3545',
                        backgroundColor: 'rgba(220, 53, 69, 0.1)',
                        tension: 0.4,
                        fill: true
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: 100,
                    easing: 'linear'
                },
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: true,
                        text: 'Tendencias en Tiempo Real (últimas 2 horas)'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        grid: {
                            color: 'rgba(0,0,0,0.1)'
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(0,0,0,0.1)'
                        }
                    }
                }
            }
        });
    },

    // Actualizar gráfico de tendencias
    updateTrendChart(pressure, flow, temp) {
        if (!this.trendChart) return;
        
        const now = new Date();
        const timeLabel = now.toLocaleTimeString();
        
        // Agregar nuevos datos
        this.trendChart.data.labels.push(timeLabel);
        this.trendChart.data.datasets[0].data.push(pressure.toFixed(1));
        this.trendChart.data.datasets[1].data.push(flow.toFixed(1));
        this.trendChart.data.datasets[2].data.push(temp.toFixed(1));
        
        // Mantener solo los últimos 50 puntos (5 segundos con updates cada 100ms)
        if (this.trendChart.data.labels.length > 50) {
            this.trendChart.data.labels.shift();
            this.trendChart.data.datasets.forEach(dataset => dataset.data.shift());
        }
        
        this.trendChart.update('none');
    },

    // Funciones de utilidad
    showView(viewId) {
        // Ocultar todas las vistas
        document.querySelectorAll('#sistema-selector-view, #sistema-monitoring-view').forEach(view => {
            view.classList.add('hidden');
        });
        
        // Mostrar vista específica
        const targetView = document.getElementById(viewId);
        if (targetView) {
            targetView.classList.remove('hidden');
        }
    },

    updateURL(view, sistemaId = null) {
        const url = new URL(window.location);
        
        if (view === 'selector') {
            url.searchParams.delete('sistema');
            window.history.pushState({view: 'selector'}, 'Selector de Sistemas', url);
        } else if (view === 'monitoring' && sistemaId) {
            url.searchParams.set('sistema', sistemaId);
            window.history.pushState({view: 'monitoring', sistemaId: sistemaId}, 'Monitoreo Sistema', url);
        }
    },

    showLoadingOverlay() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.style.display = 'flex';
        }
    },

    hideLoadingOverlay() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
    },

    showError(message) {
        console.error(message);
        // Implementar notificación de error más elegante aquí
        alert(message);
    },

    // Función de búsqueda
    filterSistemas() {
        const searchInput = document.getElementById('searchInput');
        if (!searchInput) return;
        
        const searchTerm = searchInput.value.toLowerCase();
        this.filteredSistemas = this.sistemasData.filter(sistema => 
            sistema.tag.toLowerCase().includes(searchTerm) ||
            sistema.sistema_id.toLowerCase().includes(searchTerm) ||
            sistema.ubicacion_nombre.toLowerCase().includes(searchTerm)
        );
        this.renderSistemasTable();
    }
};

// Funciones globales para compatibilidad
function showSelectorView() {
    CoriolisSPA.showSelectorView();
}

function filterSistemas() {
    CoriolisSPA.filterSistemas();
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Iniciando Coriolis SPA');
    
    // Hacer el SPA disponible globalmente
    window.CoriolisSPA = CoriolisSPA;
    
    // Ocultar loading overlay inicialmente
    CoriolisSPA.hideLoadingOverlay();
    
    // Inicializar router
    CoriolisSPA.initRouter();
    
    // Configurar event listeners
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', () => CoriolisSPA.filterSistemas());
    }
    
    const clearSearch = document.getElementById('clearSearch');
    if (clearSearch) {
        clearSearch.addEventListener('click', function() {
            const searchInput = document.getElementById('searchInput');
            if (searchInput) {
                searchInput.value = '';
                CoriolisSPA.filterSistemas();
            }
        });
    }

    // Manejar navegación del navegador
    window.addEventListener('popstate', function(event) {
        if (event.state) {
            if (event.state.view === 'selector') {
                CoriolisSPA.showSelectorView();
            } else if (event.state.view === 'monitoring') {
                CoriolisSPA.loadSistemaDetail(event.state.sistemaId);
            }
        } else {
            CoriolisSPA.showSelectorView();
        }
    });
});
