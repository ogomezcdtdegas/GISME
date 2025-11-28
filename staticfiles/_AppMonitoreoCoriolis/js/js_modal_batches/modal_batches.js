/**
 * JavaScript para el modal de búsqueda de batches
 * Incluye funciones para buscar, listar y detectar batches
 */

document.addEventListener('DOMContentLoaded', function() {
    // Manejar el evento cuando el modal se cierra para evitar advertencias de aria-hidden
    const modalBuscarBatches = document.getElementById('modalBuscarBatches');
    if (modalBuscarBatches) {
        modalBuscarBatches.addEventListener('hidden.bs.modal', function () {
            // Quitar el foco de cualquier elemento que pueda estar enfocado
            if (document.activeElement) {
                document.activeElement.blur();
            }
        });
        
        modalBuscarBatches.addEventListener('hide.bs.modal', function () {
            // Quitar el foco antes de que el modal se cierre
            if (document.activeElement) {
                document.activeElement.blur();
            }
        });
    }

    const modalBatches = document.getElementById('modalBuscarBatches');
    const btnBuscarBatches = document.getElementById('btnBuscarBatches');
    const btnListarBatches = document.getElementById('btnListarBatches');
    const formBuscarBatches = document.getElementById('formBuscarBatches');
    const spinnerBatches = document.getElementById('spinnerBatches');
    const resultadosBatches = document.getElementById('resultadosBatches');
    const listaBatches = document.getElementById('listaBatches');
    
    // Variable para controlar la cancelación de búsquedas
    let buscarBatchesController = null;
    
    // Configurar fechas por defecto (últimos 7 días)
    const hoy = new Date();
    const hace1Dias = new Date();
    hace1Dias.setDate(hoy.getDate() - 1);
    
    document.getElementById('fechaFinBatch').value = hoy.toISOString().split('T')[0];
    document.getElementById('fechaInicioBatch').value = hace1Dias.toISOString().split('T')[0];
    
    // ================================
    // FUNCIÓN COMÚN PARA LISTAR BATCHES
    // ================================
    async function listarBatchesDetectados() {
        const sistemaId = obtenerSistemaActual();
        if (!sistemaId) {
            alert('No se ha seleccionado un sistema');
            return false;
        }
        
        const fechaInicio = document.getElementById('fechaInicioBatch').value;
        const fechaFin = document.getElementById('fechaFinBatch').value;
        
        if (!fechaInicio || !fechaFin) {
            alert('Por favor, seleccione ambas fechas');
            return false;
        }
        
        if (new Date(fechaInicio) > new Date(fechaFin)) {
            alert('La fecha de inicio no puede ser mayor que la fecha de fin');
            return false;
        }
        
        // Convertir fechas a formato con hora completa (igual que las gráficas históricas)
        const fechaInicioConHora = fechaInicio + 'T00:00:00';
        const fechaFinConHora = fechaFin + 'T23:59:59';
        
        try {
            const response = await fetch(`/monitoreo/api/listar-batches/${sistemaId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({
                    fecha_inicio: fechaInicioConHora,
                    fecha_fin: fechaFinConHora
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                mostrarBatchesListados(data);
                return true;
            } else {
                alert('Error al listar batches: ' + data.error);
                return false;
            }
        } catch (error) {
            //console.error('Error al listar batches:', error);
            alert('Error de conexión al listar batches');
            return false;
        }
    }
    
    // ================================
    // BOTÓN BUSCAR BATCHES: Detecta + Lista
    // ================================
    btnBuscarBatches.addEventListener('click', async function() {
        // Si hay una búsqueda anterior en curso, aborta
        if (buscarBatchesController) {
            buscarBatchesController.abort();
        }
        
        // Crear nuevo controller para esta búsqueda
        buscarBatchesController = new AbortController();
        
        const sistemaId = obtenerSistemaActual();
        if (!sistemaId) {
            alert('No se ha seleccionado un sistema');
            buscarBatchesController = null;
            return;
        }
        
        const fechaInicio = document.getElementById('fechaInicioBatch').value;
        const fechaFin = document.getElementById('fechaFinBatch').value;
        
        if (!fechaInicio || !fechaFin) {
            alert('Por favor, seleccione ambas fechas');
            buscarBatchesController = null;
            return;
        }
        
        if (new Date(fechaInicio) > new Date(fechaFin)) {
            alert('La fecha de inicio no puede ser mayor que la fecha de fin');
            buscarBatchesController = null;
            return;
        }
        
        // Convertir fechas a formato con hora completa (igual que las gráficas históricas)
        const fechaInicioConHora = fechaInicio + 'T00:00:00';
        const fechaFinConHora = fechaFin + 'T23:59:59';
        
        // Mostrar spinner para detección
        document.getElementById('spinnerText').textContent = 'Analizando datos y detectando batches...';
        spinnerBatches.style.display = 'block';
        resultadosBatches.style.display = 'none';
        btnBuscarBatches.disabled = true;
        btnListarBatches.disabled = true;
        
        try {
            // PASO 1: Ejecutar detección de batches
            const responseDeteccion = await fetch(`/monitoreo/api/detectar-batches/${sistemaId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({
                    fecha_inicio: fechaInicioConHora,
                    fecha_fin: fechaFinConHora
                }),
                signal: buscarBatchesController.signal
            });
            
            const dataDeteccion = await responseDeteccion.json();
            
            if (!dataDeteccion.success) {
                alert('Error en detección: ' + dataDeteccion.error);
                return;
            }
            
            //console.log(`✅ Detección completada: ${dataDeteccion.batches_detectados} batches encontrados`);
            
            // PASO 2: Cambiar spinner para listado
            document.getElementById('spinnerText').textContent = 'Cargando batches detectados...';
            
            // PASO 3: Listar batches usando la función común
            await listarBatchesDetectados();
            
        } catch (error) {
            if (error.name === 'AbortError') {
                //console.log('Búsqueda de batches cancelada por el usuario');
                return;
            }
            //console.error('Error al buscar batches:', error);
            alert('Error de conexión al buscar batches');
        } finally {
            spinnerBatches.style.display = 'none';
            btnBuscarBatches.disabled = false;
            btnListarBatches.disabled = false;
            buscarBatchesController = null;
        }
    });
    
    // ================================
    // BOTÓN LISTAR BATCHES: Solo Lista
    // ================================
    btnListarBatches.addEventListener('click', async function() {
        // Si hay una búsqueda en curso, aborta
        if (buscarBatchesController) {
            //console.log('Cancelando búsqueda en curso...');
            buscarBatchesController.abort();
            buscarBatchesController = null;
        }
        
        // Validar sistema seleccionado
        const sistemaId = obtenerSistemaActual();
        if (!sistemaId) {
            alert('No se ha seleccionado un sistema');
            return;
        }
        
        // Validar fechas
        const fechaInicio = document.getElementById('fechaInicioBatch').value;
        const fechaFin = document.getElementById('fechaFinBatch').value;
        
        if (!fechaInicio || !fechaFin) {
            alert('Por favor, seleccione ambas fechas');
            return;
        }
        
        if (new Date(fechaInicio) > new Date(fechaFin)) {
            alert('La fecha de inicio no puede ser mayor que la fecha de fin');
            return;
        }
        
        // Mostrar spinner para listado
        document.getElementById('spinnerText').textContent = 'Cargando batches detectados...';
        spinnerBatches.style.display = 'block';
        resultadosBatches.style.display = 'none';
        btnBuscarBatches.disabled = true;
        btnListarBatches.disabled = true;
        
        try {
            // Usar la función común para listar
            await listarBatchesDetectados();
        } catch (error) {
            //console.error('Error al listar batches:', error);
            alert('Error de conexión al listar batches');
        } finally {
            spinnerBatches.style.display = 'none';
            btnBuscarBatches.disabled = false;
            btnListarBatches.disabled = false;
        }
    });
    
    function mostrarBatchesListados(data) {
        // Para listado, no mostramos configuración ya que solo consultamos
        resultadosBatches.style.display = 'block';
        
        if (data.total_batches === 0) {
            listaBatches.innerHTML = `
                <div class="alert alert-info">
                    <i class="bi bi-info-circle"></i>
                    No hay batches detectados en el rango de fechas especificado.
                    <br>
                    <small>Use "Buscar Batches" para ejecutar la detección automática.</small>
                </div>
            `;
            // Resetear total de masa
            document.getElementById('totalMasaBatches').textContent = '0.00';
            return;
        }
        
        // Usar el total de masa calculado por el backend (con la misma precisión que el dashboard)
        const totalMasa = data.total_masa || 0;
        
        // Actualizar el display del total de masa
        document.getElementById('totalMasaBatches').textContent = totalMasa.toFixed(2);
        
        let html = `
            <div class="alert alert-info">
                <i class="bi bi-list-check"></i>
                <strong>Se encontraron ${data.total_batches} batch(es) previamente detectado(s)</strong>
                <br>
                <small>Sistema: ${data.sistema.tag} - ${data.sistema.sistema_id} (${data.sistema.ubicacion})</small>
                <br>
                <small>Rango consultado: ${data.fecha_inicio} - ${data.fecha_fin}</small>
            </div>
            
            <div class="table-responsive">
                <table class="table table-striped table-sm">
                    <thead class="table-secondary">
                        <tr>
                            <th># Ticket</th>
                            <th>Inicio</th>
                            <th>Fin</th>
                            <th>Duración</th>
                            <th>Masa Total (kg)</th>
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
        
        data.batches.forEach(batch => {
            // Formatear el número de ticket con badge amarillo más grande si existe
            const ticketDisplay = batch.num_ticket 
                ? `<span class="badge bg-warning text-dark" style="font-size: 0.9rem; padding: 0.4rem 0.8rem;">${batch.num_ticket}</span>` 
                : '-';
            
            html += `
                <tr>
                    <td><small>${ticketDisplay}</small></td>
                    <td><small>${batch.fecha_inicio}</small></td>
                    <td><small>${batch.fecha_fin}</small></td>
                    <td><small>${batch.duracion_minutos} min</small></td>
                    <td><strong>${batch.mas_total}</strong></td>
                    <td>${batch.temperatura_prom}</td>
                    <td>${batch.densidad_prom}</td>
                    <td><small>${batch.perfil_vol_min || '-'}</small></td>
                    <td><span class="badge bg-secondary">${batch.time_finished_batch || '-'}</span></td>
                    <td>${batch.total_registros}</td>
                    <td>
                        <button class="btn btn-info btn-sm" onclick="verDetalleBatch('${batch.id}')">
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
        
        listaBatches.innerHTML = html;
    }
    
    function mostrarConfiguracion(config) {
        if (!config) {
            //console.warn('No se recibió configuración para mostrar');
            document.getElementById('configuracionUtilizada').style.display = 'none';
            return;
        }
        
        try {
            document.getElementById('limInfCaudal').textContent = config.lim_inf_caudal_masico || 'N/A';
            document.getElementById('limSupCaudal').textContent = config.lim_sup_caudal_masico || 'N/A';
            document.getElementById('volMinBatch').textContent = config.vol_minimo_batch || 'N/A';
            document.getElementById('configuracionUtilizada').style.display = 'block';
        } catch (error) {
            //console.error('Error al mostrar configuración:', error);
            document.getElementById('configuracionUtilizada').style.display = 'none';
        }
    }
    
    // Función para obtener CSRF token (versión robusta)
    function getCSRFToken() {
        // Primero intentar obtener del input hidden
        let token = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        
        // Si no se encuentra, intentar obtener de las cookies
        if (!token) {
            const name = 'csrftoken';
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            token = cookieValue;
        }
        
        // Validar que el token tenga el formato correcto (debería tener 64 caracteres)
        if (token && token.length !== 64) {
            //console.warn('⚠️ Token CSRF con longitud incorrecta:', token.length, 'caracteres. Esperados: 64');
        }
        
        //console.log('🔐 Token CSRF obtenido:', token ? `✅ Válido (${token.length} chars)` : '❌ No encontrado');
        return token || '';
    }
});

// Función global para ver el detalle de un batch
async function verDetalleBatch(batchId) {
    try {
        const response = await fetch(`/monitoreo/api/detalle-batch/${batchId}/`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            mostrarDetalleBatch(data);
        } else {
            alert('Error al cargar detalle: ' + data.error);
        }
    } catch (error) {
        //console.error('Error al cargar detalle del batch:', error);
        alert('Error de conexión al cargar detalle del batch');
    }
}

// Función global para abrir el modal de batches
function abrirModalBatches() {
    const modal = new bootstrap.Modal(document.getElementById('modalBuscarBatches'));
    modal.show();
}

// ================================
// ESCUCHAR EVENTO DE TICKET ASIGNADO
// ================================
window.addEventListener('ticketAsignado', function(event) {
    // Verificar si el modal de batches está abierto
    const modalBatches = document.getElementById('modalBuscarBatches');
    if (modalBatches && modalBatches.classList.contains('show')) {
        // Verificar si hay batches listados
        const listaBatches = document.getElementById('listaBatches');
        if (listaBatches && listaBatches.children.length > 0) {
            // Recargar la lista de batches
            console.log('Recargando lista de batches después de asignar ticket #' + event.detail.numTicket);
            listarBatchesDetectados();
        }
    }
});