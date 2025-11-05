/**
 * JavaScript común para manejo de mapas en Coriolis
 * Funciones reutilizables para modales de mapa y marcadores
 */

// Variables globales para el mapa
let map;
let marker;

/**
 * Mostrar modal con mapa de ubicación del sistema
 * @param {string} lat - Latitud
 * @param {string} lng - Longitud  
 * @param {string} sistemaTag - Tag del sistema
 * @param {string} sistemaId - ID del sistema
 * @param {string} ubicacionNombre - Nombre de la ubicación
 */
function showMapModal(lat, lng, sistemaTag, sistemaId, ubicacionNombre) {
    // Actualizar información del modal
    document.getElementById('modal-sistema-info').textContent = `${sistemaTag} ${sistemaId}`;
    document.getElementById('modal-ubicacion-info').textContent = ubicacionNombre;
    document.getElementById('modal-coordenadas-info').textContent = `${lat}, ${lng}`;
    
    // Mostrar el modal
    const mapModal = new bootstrap.Modal(document.getElementById('mapModal'));
    mapModal.show();
    
    // Esperar a que el modal se muestre para inicializar el mapa
    document.getElementById('mapModal').addEventListener('shown.bs.modal', function initMap() {
        // Solo inicializar una vez
        this.removeEventListener('shown.bs.modal', initMap);
        
        // Limpiar mapa anterior si existe
        if (map) {
            map.remove();
        }
        
        // Verificar que Leaflet esté disponible
        if (typeof L === 'undefined') {
            console.error('Leaflet no está disponible. Asegúrate de incluir la librería Leaflet.');
            document.getElementById('map').innerHTML = '<div class="alert alert-warning">Error: No se pudo cargar el mapa. Falta la librería Leaflet.</div>';
            return;
        }
        
        try {
            // Crear el mapa
            map = L.map('map').setView([parseFloat(lat), parseFloat(lng)], 15);
            
            // Agregar tiles de OpenStreetMap
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors'
            }).addTo(map);
            
            // Crear icono personalizado para el sistema
            const sistemaIcon = L.divIcon({
                html: '<i class="bi bi-gear-fill text-primary" style="font-size: 24px;"></i>',
                iconSize: [30, 30],
                className: 'custom-marker'
            });
            
            // Agregar marcador
            marker = L.marker([parseFloat(lat), parseFloat(lng)], { icon: sistemaIcon })
                .addTo(map)
                .bindPopup(`
                    <div class="text-center">
                        <h6><i class="bi bi-gear"></i> ${sistemaTag} ${sistemaId}</h6>
                        <p class="mb-1"><strong>Ubicación:</strong> ${ubicacionNombre}</p>
                        <p class="mb-0"><strong>Coordenadas:</strong><br>${lat}, ${lng}</p>
                    </div>
                `)
                .openPopup();
                
        } catch (error) {
            console.error('Error inicializando el mapa:', error);
            document.getElementById('map').innerHTML = '<div class="alert alert-danger">Error al cargar el mapa.</div>';
        }
    });
}

/**
 * Copiar coordenadas al portapapeles
 */
function copyCoordinates() {
    const coordenadas = document.getElementById('modal-coordenadas-info').textContent;
    
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(coordenadas).then(() => {
            showCopySuccess();
        }).catch(err => {
            console.error('Error al copiar:', err);
            fallbackCopyCoordinates(coordenadas);
        });
    } else {
        // Fallback para navegadores sin soporte de clipboard API
        fallbackCopyCoordinates(coordenadas);
    }
}

/**
 * Fallback para copiar coordenadas sin clipboard API
 * @param {string} coordenadas - Coordenadas a copiar
 */
function fallbackCopyCoordinates(coordenadas) {
    const textArea = document.createElement('textarea');
    textArea.value = coordenadas;
    document.body.appendChild(textArea);
    textArea.select();
    document.execCommand('copy');
    document.body.removeChild(textArea);
    showCopySuccess();
}

/**
 * Mostrar mensaje de éxito al copiar coordenadas
 */
function showCopySuccess() {
    const btn = event.target.closest('button');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<i class="bi bi-check"></i> Copiado!';
    btn.classList.remove('btn-primary');
    btn.classList.add('btn-success');
    
    setTimeout(() => {
        btn.innerHTML = originalText;
        btn.classList.remove('btn-success');
        btn.classList.add('btn-primary');
    }, 2000);
}

/**
 * Inicializar mapa inline (para vistas que no usan modal)
 * @param {string} containerId - ID del contenedor del mapa
 * @param {number} lat - Latitud
 * @param {number} lng - Longitud
 * @param {string} sistemaTag - Tag del sistema
 * @param {string} sistemaId - ID del sistema
 * @param {string} ubicacionNombre - Nombre de la ubicación
 * @returns {L.Map} - Instancia del mapa
 */
function initInlineMap(containerId, lat, lng, sistemaTag, sistemaId, ubicacionNombre) {
    // Coordenadas por defecto (Centro de Colombia)
    let finalLat = lat || 4.6097;
    let finalLng = lng || -74.0817;

    // Crear mapa con zoom apropiado
    const zoom = (finalLat === 4.6097 && finalLng === -74.0817) ? 6 : 12;
    const inlineMap = L.map(containerId).setView([finalLat, finalLng], zoom);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(inlineMap);

    // Crear icono personalizado para el sistema
    const sistemaIcon = L.divIcon({
        html: '<i class="bi bi-gear-fill text-primary" style="font-size: 20px;"></i>',
        iconSize: [25, 25],
        className: 'custom-marker-sistema'
    });

    // Agregar marcador
    const inlineMarker = L.marker([finalLat, finalLng], { icon: sistemaIcon }).addTo(inlineMap);
    
    if (sistemaTag && sistemaId) {
        inlineMarker.bindPopup(`
            <div>
                <h6><i class="bi bi-gear"></i> ${sistemaTag} ${sistemaId}</h6>
                <p><strong>Ubicación:</strong> ${ubicacionNombre}</p>
                <p><strong>Coordenadas:</strong> ${finalLat}, ${finalLng}</p>
            </div>
        `).openPopup();
    }

    return inlineMap;
}

/**
 * Parsear coordenadas desde string
 * @param {string} coordStr - String de coordenadas "(-3.6900000, -80.0000000)"
 * @returns {object} - {lat: number, lng: number} o null si falla
 */
function parseCoordinates(coordStr) {
    try {
        if (!coordStr) return null;
        
        // Parsear formato: "(-3.6900000, -80.0000000)" -> [-3.6900000, -80.0000000]
        const cleanStr = coordStr.replace(/[()]/g, '');
        const coords = cleanStr.split(',').map(coord => parseFloat(coord.trim()));
        
        if (coords.length === 2 && !isNaN(coords[0]) && !isNaN(coords[1])) {
            return { lat: coords[0], lng: coords[1] };
        }
        
        return null;
    } catch (error) {
        console.error('Error parseando coordenadas:', error);
        return null;
    }
}
