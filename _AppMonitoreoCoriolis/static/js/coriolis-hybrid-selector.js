/**
 * JavaScript para Coriolis Hybrid - Selector de Sistemas
 * Maneja la vista de selección con API DRF
 */

// Variables globales
let sistemasData = [];
let filteredSistemas = [];
let currentSortField = '';
let currentSortDirection = 'asc';

// Función para obtener CSRF token
function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

// Función para cargar sistemas desde la API
async function loadSistemas() {
    try {
        const response = await fetch('/monitoreo/api/sistemas/', {
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
        sistemasData = data.sistemas;
        filteredSistemas = [...sistemasData];
        renderSistemasTable();
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

// Función para renderizar la tabla de sistemas
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
                <strong class="text-primary">${sistema.tag}</strong>
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
                <a href="/monitoreo/${sistema.id}/" class="btn btn-primary btn-sm">
                    <i class="bi bi-activity"></i> Monitorear
                </a>
            </td>
        </tr>
    `).join('');
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
    // Resetear todos los íconos
    document.querySelectorAll('[id$="-sort-icon"]').forEach(icon => {
        icon.className = 'bi bi-arrow-up-down ms-1';
    });
    
    // Actualizar ícono del campo actual
    const icon = document.getElementById(`${field}-sort-icon`);
    if (icon) {
        icon.className = currentSortDirection === 'asc' ? 
            'bi bi-arrow-up ms-1' : 'bi bi-arrow-down ms-1';
    }
}

// Inicialización cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    loadSistemas();
    
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
});
