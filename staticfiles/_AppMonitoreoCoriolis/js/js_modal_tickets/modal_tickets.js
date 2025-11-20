/**
 * JavaScript para el modal de tickets
 * Incluye funciones para listar, filtrar y mostrar tickets asignados a batches
 */

document.addEventListener('DOMContentLoaded', function() {
    const modalTickets = document.getElementById('modalListarTickets');
    const btnActualizarTickets = document.getElementById('btnActualizarTickets');
    const buscarTicket = document.getElementById('buscarTicket');
    const spinnerTickets = document.getElementById('spinnerTickets');
    const resultadosTickets = document.getElementById('resultadosTickets');
    const listaTickets = document.getElementById('listaTickets');
    
    // Variables para almacenar tickets y paginación
    let todosLosTickets = [];
    let ticketsFiltrados = [];
    let paginacionInfo = null;
    let paginaActual = 1;
    let tamañoPagina = 10;
    
    // ================================
    // FUNCIÓN PARA CARGAR TICKETS CON PAGINACIÓN
    // ================================
    async function cargarTodosLosTickets(pagina = 1, pageSize = 10) {
        const sistemaId = obtenerSistemaActual();
        if (!sistemaId) {
            alert('No se ha seleccionado un sistema');
            return false;
        }
        
        try {
            spinnerTickets.style.display = 'block';
            btnActualizarTickets.disabled = true;
            
            const response = await fetch(`/monitoreo/api/listar-tickets/${sistemaId}/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                todosLosTickets = data.batches || [];
                paginacionInfo = data.pagination || null;
                paginaActual = pagina;
                tamañoPagina = pageSize;
                
                // Ordenar por número de ticket (numérico descendente)
                todosLosTickets.sort((a, b) => {
                    const ticketA = a.num_ticket || 0;
                    const ticketB = b.num_ticket || 0;
                    return ticketB - ticketA;
                });
                
                ticketsFiltrados = [...todosLosTickets];
                mostrarTicketsEnTabla();
                mostrarControlesPaginacion();
                return true;
            } else {
                alert('Error al cargar tickets: ' + data.error);
                listaTickets.innerHTML = '<div class="alert alert-warning">No se pudieron cargar los tickets</div>';
                return false;
            }
        } catch (error) {
            //console.error('Error al cargar tickets:', error);
            alert('Error de conexión al cargar tickets');
            listaTickets.innerHTML = '<div class="alert alert-danger">Error de conexión</div>';
            return false;
        } finally {
            spinnerTickets.style.display = 'none';
            btnActualizarTickets.disabled = false;
        }
    }
    
    // ================================
    // FUNCIÓN PARA FILTRAR TICKETS POR NÚMERO (lado cliente)
    // ================================
    function filtrarTickets() {
        const termino = buscarTicket.value.toLowerCase().trim();
        
        if (termino === '') {
            ticketsFiltrados = [...todosLosTickets];
        } else {
            ticketsFiltrados = todosLosTickets.filter(ticket => 
                String(ticket.num_ticket || '').toLowerCase().includes(termino)
            );
        }
        
        // Al filtrar, ocultar controles de paginación porque filtramos la página actual
        document.getElementById('paginacionTickets').innerHTML = '';
        mostrarTicketsEnTabla();
    }
    
    // ================================
    // FUNCIÓN PARA MOSTRAR TICKETS EN TABLA
    // ================================
    function mostrarTicketsEnTabla() {
        if (ticketsFiltrados.length === 0) {
            listaTickets.innerHTML = `
                <div class="alert alert-info">
                    <i class="bi bi-info-circle"></i>
                    ${buscarTicket.value.trim() !== '' ? 
                        'No se encontraron tickets que coincidan con la búsqueda.' : 
                        'No hay batches con tickets asignados en este sistema.'}
                </div>
            `;
            document.getElementById('paginacionTickets').innerHTML = '';
            return;
        }
        
        let html = `
            <div class="alert alert-success">
                <i class="bi bi-check-circle"></i>
                <strong>Se encontraron ${ticketsFiltrados.length} batch(es) con tickets${buscarTicket.value.trim() !== '' ? ' (filtrados)' : ''}</strong>
                <br>
                <small>Total de batches con tickets en el sistema: ${todosLosTickets.length}</small>
            </div>
            
            <div class="table-responsive">
                <table class="table table-striped table-sm">
                    <thead class="table-dark">
                        <tr>
                            <th># Ticket</th>
                            <th>Inicio</th>
                            <th>Fin</th>
                            <th>Duración</th>
                            <th>Masa. Total (kg)</th>
                            <th>Temp. Prom. (°F)</th>
                            <th>Densidad Prom.</th>
                            <th>Vol. Mín. (kg)</th>
                            <th>Tiempo Cierre (min)</th>
                            <th>Registros</th>
                            <th>Detalle</th>
                        </tr>
                    </thead>
                    <tbody>
        `;
        
        ticketsFiltrados.forEach((ticket, index) => {
            // Formatear el número de ticket con badge amarillo más grande si existe
            const ticketDisplay = ticket.num_ticket 
                ? `<span class="badge bg-warning text-dark" style="font-size: 0.9rem; padding: 0.4rem 0.8rem;">${ticket.num_ticket}</span>` 
                : '-';
            
            html += `
                <tr>
                    <td><small>${ticketDisplay}</small></td>
                    <td><small>${ticket.fecha_inicio}</small></td>
                    <td><small>${ticket.fecha_fin}</small></td>
                    <td><small>${ticket.duracion_minutos} min</small></td>
                    <td><strong>${ticket.mas_total}</strong></td>
                    <td>${ticket.temperatura_prom}</td>
                    <td>${ticket.densidad_prom}</td>
                    <td><small>${ticket.perfil_vol_min || '-'}</small></td>
                    <td><span class="badge bg-secondary">${ticket.time_finished_batch || '-'}</span></td>
                    <td>${ticket.total_registros}</td>
                    <td>
                        <button class="btn btn-info btn-sm" onclick="verDetalleBatch('${ticket.id}')">
                            <i class="bi bi-graph-up"></i> Ver
                        </button>
                    </td>
                </tr>
            `;
        });
        
        html += `
                    </tbody>
                </table>
            </div>
        `;
        
        listaTickets.innerHTML = html;
        
        // Solo mostrar paginación si no hay filtro activo
        if (buscarTicket.value.trim() === '') {
            mostrarControlesPaginacion();
        }
    }
    
    // ================================
    // FUNCIÓN PARA MOSTRAR CONTROLES DE PAGINACIÓN
    // ================================
    function mostrarControlesPaginacion() {
        const contenedorPaginacion = document.getElementById('paginacionTickets');
        
        if (!paginacionInfo || paginacionInfo.total_pages <= 1) {
            contenedorPaginacion.innerHTML = '';
            return;
        }
        
        const { current_page, total_pages, has_previous, has_next, previous_page, next_page, total_batches } = paginacionInfo;
        
        let html = `
            <div class="d-flex justify-content-between align-items-center w-100">
                <div>
                    <small class="text-muted">
                        Página ${current_page} de ${total_pages} (${total_batches} tickets totales)
                    </small>
                </div>
                <div class="btn-group" role="group">
                    <button type="button" class="btn btn-sm btn-outline-primary" 
                            id="btnPaginaAnterior" 
                            ${!has_previous ? 'disabled' : ''}>
                        <i class="bi bi-chevron-left"></i> Anterior
                    </button>
                    <button type="button" class="btn btn-sm btn-outline-primary" 
                            id="btnPaginaSiguiente" 
                            ${!has_next ? 'disabled' : ''}>
                        Siguiente <i class="bi bi-chevron-right"></i>
                    </button>
                </div>
            </div>
        `;
        
        contenedorPaginacion.innerHTML = html;
        
        // Agregar eventos a botones de paginación
        if (has_previous) {
            document.getElementById('btnPaginaAnterior').addEventListener('click', () => {
                cargarTodosLosTickets(previous_page, tamañoPagina);
            });
        }
        
        if (has_next) {
            document.getElementById('btnPaginaSiguiente').addEventListener('click', () => {
                cargarTodosLosTickets(next_page, tamañoPagina);
            });
        }
    }
    
    // ================================
    // EVENT LISTENERS
    // ================================
    
    // Botón actualizar
    if (btnActualizarTickets) {
        btnActualizarTickets.addEventListener('click', () => cargarTodosLosTickets(1, tamañoPagina));
    }
    
    // Campo de búsqueda con filtrado en tiempo real
    if (buscarTicket) {
        buscarTicket.addEventListener('input', filtrarTickets);
        
        // Limpiar búsqueda con Enter
        buscarTicket.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                filtrarTickets();
            }
        });
    }
    
    // Cuando se abre el modal, cargar automáticamente los tickets
    if (modalTickets) {
        modalTickets.addEventListener('shown.bs.modal', function() {
            if (buscarTicket) {
                buscarTicket.value = ''; // Limpiar búsqueda
            }
            cargarTodosLosTickets(1, 10);
        });
        
        // Manejar foco para accesibilidad - eliminar advertencias aria-hidden
        modalTickets.addEventListener('hidden.bs.modal', function() {
            // Quitar foco de cualquier elemento dentro del modal cuando se cierra
            if (document.activeElement && modalTickets.contains(document.activeElement)) {
                document.activeElement.blur();
            }
        });
        
        modalTickets.addEventListener('hide.bs.modal', function() {
            // Antes de ocultar el modal, quitar foco de elementos internos
            const focusedElement = document.activeElement;
            if (focusedElement && modalTickets.contains(focusedElement)) {
                focusedElement.blur();
            }
        });
    }
    
    // Función para obtener CSRF token
    function getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    }
});

// Función global para ver detalle de ticket
function verDetalleTicket(ticketId) {
    //console.log('Ver detalle del ticket:', ticketId);
    // Aquí puedes implementar la lógica para mostrar el detalle del ticket
    alert(`Funcionalidad de detalle para el ticket ${ticketId} - Por implementar`);
}

// Función global para abrir el modal de tickets
function abrirModalTickets() {
    const modal = new bootstrap.Modal(document.getElementById('modalListarTickets'));
    modal.show();
}