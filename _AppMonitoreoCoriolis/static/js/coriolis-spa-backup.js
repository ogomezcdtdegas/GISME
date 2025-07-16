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
function initRouter() {
    const path = window.location.pathname;
    const sistemaIdMatch = path.match(/\/monitoreo\/([a-f0-9-]+)\//);
    
    if (sistemaIdMatch) {
        const sistemaId = sistemaIdMatch[1];
        loadSistemaDetail(sistemaId);
    } else {
        showSelectorView();
    }
}

// Mostrar vista de selección
function showSelectorView() {
    document.getElementById('loadingOverlay').classList.add('hidden');
    document.getElementById('sistema-selector-view').classList.remove('hidden');
    document.getElementById('sistema-monitoring-view').classList.add('hidden');
    
    // Actualizar URL sin recargar
    history.pushState({view: 'selector'}, '', '/monitoreo/');
    
    // Cargar sistemas si no están cargados
    if (sistemasData.length === 0) {
        loadSistemas();
    }
}

// Mostrar vista de monitoreo
function showMonitoringView(sistemaId) {
    document.getElementById('loadingOverlay').classList.add('hidden');
    document.getElementById('sistema-selector-view').classList.add('hidden');
    document.getElementById('sistema-monitoring-view').classList.remove('hidden');
    
    // Actualizar URL sin recargar
    history.pushState({view: 'monitoring', sistemaId: sistemaId}, '', `/monitoreo/${sistemaId}/`);
    
    loadSistemaDetail(sistemaId);
}

// Cargar sistemas desde la API de Complementos
async function loadSistemas() {
    try {
        const response = await fetch('/complementos/listar-todo-sistemas/', {
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/json',
            },
            credentials: 'same-origin'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Verificar estructura de respuesta
        if (data.success && data.results) {
            sistemasData = data.results; // La respuesta tiene formato {success: true, results: [...]}
            filteredSistemas = [...sistemasData];
            renderSistemasTable();
        } else {
            throw new Error('Estructura de respuesta inválida');
        }
    } catch (error) {
        console.error('Error cargando sistemas:', error);
        document.getElementById('sistemasTableBody').innerHTML = `
            <tr>
                <td colspan="5" class="text-center text-danger">
                    <i class="bi bi-exclamation-circle"></i> Error cargando sistemas
                </td>
            </tr>
        `;
    }
}

// Cargar detalle de sistema desde la API de Complementos
async function loadSistemaDetail(sistemaId) {
    try {
        const response = await fetch(`/complementos/sistema/${sistemaId}/`, {
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/json',
            },
            credentials: 'same-origin'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Verificar estructura de respuesta
        if (data.success && data.data) {
            currentSistema = data.data; // La respuesta tiene formato {success: true, data: {...}}
            renderSistemaDetail();
        } else {
            throw new Error('Estructura de respuesta inválida');
        }
    } catch (error) {
        console.error('Error cargando sistema:', error);
        alert('Error cargando el sistema. Volviendo a la lista...');
        showSelectorView();
    }
}

// Renderizar tabla de sistemas
function renderSistemasTable() {
    const tbody = document.getElementById('sistemasTableBody');
    
    if (filteredSistemas.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5" class="text-center">
                    <i class="bi bi-info-circle"></i> No se encontraron sistemas
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = filteredSistemas.map(sistema => `
        <tr>
            <td>
                <strong class="text-dark">${sistema.tag}</strong>
            </td>
            <td>
                ${sistema.sistema_id}
            </td>
            <td>
                <i class="bi bi-geo-alt text-success"></i> ${sistema.ubicacion_nombre}
            </td>
            <td>
                <small class="text-muted">${sistema.ubicacion_coordenadas}</small>
            </td>
            <td>
                <button class="btn btn-primary btn-sm" onclick="showMonitoringView('${sistema.id}')">
                    <i class="bi bi-activity"></i> Monitorear
                </button>
            </td>
        </tr>
    `).join('');
}

// Renderizar detalle del sistema
function renderSistemaDetail() {
    if (!currentSistema) return;

    // Actualizar título y breadcrumb
    document.getElementById('sistemaTitle').innerHTML = 
        `<i class="bi bi-diagram-3"></i> Monitoreo de Medidores Coriolis "${currentSistema.tag} ${currentSistema.sistema_id}"`;
    document.getElementById('breadcrumbSistema').textContent = 
        `${currentSistema.tag} ${currentSistema.sistema_id}`;

    // Renderizar información del sistema
    document.getElementById('sistemaInfo').innerHTML = `
        <div class="metric-item">
            <span class="metric-label">Tag:</span>
            <span class="metric-value text-primary">${currentSistema.tag}</span>
        </div>
        <div class="metric-item">
            <span class="metric-label">ID Sistema:</span>
            <span class="metric-value">${currentSistema.sistema_id}</span>
        </div>
        <div class="metric-item">
            <span class="metric-label">Ubicación:</span>
            <span class="metric-value">${currentSistema.ubicacion_nombre}</span>
        </div>
        <div class="metric-item">
            <span class="metric-label">Coordenadas:</span>
            <span class="metric-value">${currentSistema.ubicacion_coordenadas}</span>
        </div>
        <div class="metric-item">
            <span class="metric-label">Estado:</span>
            <span class="metric-value text-success">
                <i class="bi bi-check-circle"></i> Activo
            </span>
        </div>
    `;

    // Inicializar mapa
    initSpaMap();
    
    // Inicializar gráfico
    initSpaChart();
}

// Función de búsqueda
function filterSistemas() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    filteredSistemas = sistemasData.filter(sistema => 
        sistema.tag.toLowerCase().includes(searchTerm) ||
        sistema.sistema_id.toLowerCase().includes(searchTerm) ||
        sistema.ubicacion_nombre.toLowerCase().includes(searchTerm)
    );
    renderSistemasTable();
}

// Función de ordenamiento
function sortTable(field) {
    if (currentSortField === field) {
        currentSortDirection = currentSortDirection === 'asc' ? 'desc' : 'asc';
    } else {
        currentSortField = field;
        currentSortDirection = 'asc';
    }

    filteredSistemas.sort((a, b) => {
        let aVal = a[field];
        let bVal = b[field];
        
        if (typeof aVal === 'string') {
            aVal = aVal.toLowerCase();
            bVal = bVal.toLowerCase();
        }
        
        if (currentSortDirection === 'asc') {
            return aVal > bVal ? 1 : -1;
        } else {
            return aVal < bVal ? 1 : -1;
        }
    });

    renderSistemasTable();
    updateSortIcons(field);
}

// Función para actualizar íconos de ordenamiento
function updateSortIcons(field) {
    document.querySelectorAll('[id$="-sort-icon"]').forEach(icon => {
        icon.className = 'bi bi-arrow-up-down ms-1';
    });
    
    const icon = document.getElementById(`${field}-sort-icon`);
    if (icon) {
        icon.className = currentSortDirection === 'asc' ? 
            'bi bi-arrow-up ms-1' : 'bi bi-arrow-down ms-1';
    }
}

// Inicializar mapa en SPA
function initSpaMap() {
    if (!currentSistema) return;

    // Destruir mapa anterior si existe
    if (map) {
        map.remove();
    }

    // Coordenadas por defecto (Centro de Colombia)
    let lat = 4.6097;
    let lng = -74.0817;

    // Intentar obtener coordenadas del sistema
    if (currentSistema.ubicacion_coordenadas) {
        const coords = parseCoordinates(currentSistema.ubicacion_coordenadas);
        if (coords) {
            lat = coords.lat;
            lng = coords.lng;
            console.log('✅ Coordenadas parseadas correctamente:', lat, lng);
        }
    } else if (currentSistema.ubicacion && currentSistema.ubicacion.latitud && currentSistema.ubicacion.longitud) {
        // Formato alternativo: coordenadas separadas en el objeto ubicación
        lat = parseFloat(currentSistema.ubicacion.latitud);
        lng = parseFloat(currentSistema.ubicacion.longitud);
        console.log('✅ Coordenadas obtenidas de ubicación:', lat, lng);
    }

    // Usar la función común para inicializar el mapa
    map = initInlineMap('sistemaMap', lat, lng, currentSistema.tag, currentSistema.sistema_id, currentSistema.ubicacion_nombre);
}

// Inicializar gráfico SPA
function initSpaChart() {
    if (trendChart) {
        trendChart.destroy();
    }

    const ctx = document.getElementById('trendChart').getContext('2d');
    
    // Datos simulados para demo
    const labels = [];
    const presionData = [];
    const flujoData = [];
    const tempData = [];
    
    for (let i = 0; i < 24; i++) {
        labels.push(`${i}:00`);
        presionData.push(Math.random() * 50 + 100);
        flujoData.push(Math.random() * 20 + 30);
        tempData.push(Math.random() * 10 + 20);
    }

    trendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Presión (PSI)',
                    data: presionData,
                    borderColor: '#28a745',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Flujo (m³/h)',
                    data: flujoData,
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
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: 'Tendencias de las últimas 24 horas'
                }
            },
            scales: {
                y: {
                    beginAtZero: false
                }
            }
        }
    });
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar router
    initRouter();
    
    // Búsqueda en tiempo real
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', filterSistemas);
    }
    
    // Limpiar búsqueda
    const clearSearch = document.getElementById('clearSearch');
    if (clearSearch) {
        clearSearch.addEventListener('click', function() {
            document.getElementById('searchInput').value = '';
            filterSistemas();
        });
    }

    // Manejar navegación del navegador
    window.addEventListener('popstate', function(event) {
        if (event.state) {
            if (event.state.view === 'selector') {
                showSelectorView();
            } else if (event.state.view === 'monitoring') {
                showMonitoringView(event.state.sistemaId);
            }
        } else {
            showSelectorView();
        }
    });
});
