/**
 * JavaScript para el modal de detalle de batch
 * Incluye funciones para mostrar información del batch, crear gráficos y manejar diagnósticos
 */

document.addEventListener('DOMContentLoaded', function() {
    // Manejar el evento cuando el modal se cierra para evitar advertencias de aria-hidden
    const modalDetalleBatch = document.getElementById('modalDetalleBatch');
    if (modalDetalleBatch) {
        modalDetalleBatch.addEventListener('hidden.bs.modal', function () {
            // Quitar el foco de cualquier elemento que pueda estar enfocado
            if (document.activeElement) {
                document.activeElement.blur();
            }
        });
        
        modalDetalleBatch.addEventListener('hide.bs.modal', function () {
            // Quitar el foco antes de que el modal se cierre
            if (document.activeElement) {
                document.activeElement.blur();
            }
        });
    }
});

// Registrar el plugin de anotaciones
if (typeof window.chartjs_plugin_annotation !== 'undefined') {
    Chart.register(window.chartjs_plugin_annotation.default || window.chartjs_plugin_annotation);
} else if (typeof ChartAnnotation !== 'undefined') {
    Chart.register(ChartAnnotation);
} else {
    //console.warn('Plugin de anotaciones de Chart.js no está disponible');
}

let batchChart = null;
let batchChartTecnico = null;
let datosActualesBatch = null;

// Función para mostrar el detalle del batch
function mostrarDetalleBatch(data) {
    // Guardar datos para uso posterior
    datosActualesBatch = data;
    
    // Debug: Verificar valor de num_ticket
    //console.log('Número de ticket:', data.batch_info.num_ticket);
    //console.log('Tipo:', typeof data.batch_info.num_ticket);
    //console.log('Valor evaluado:', data.batch_info.num_ticket ? 'Tiene valor' : 'Sin valor');
    
    // Actualizar título del modal con el número de ticket si existe
    const modalTitle = document.getElementById('modalDetalleBatchLabel');
    if (modalTitle) {
        // Validar que num_ticket no sea null, undefined, 0 o string vacío
        if (data.batch_info.num_ticket && data.batch_info.num_ticket !== 0) {
            modalTitle.innerHTML = `
                <div class="d-flex align-items-center justify-content-center w-100">
                    <i class="bi bi-graph-up"></i> 
                    <span class="ms-2">Detalle del Batch Detectado</span>
                    <span class="badge bg-success ms-2">Ticket #${data.batch_info.num_ticket}</span>
                </div>
            `;
        } else {
            modalTitle.innerHTML = `<i class="bi bi-graph-up"></i> Detalle del Batch Detectado`;
        }
    }
    
    // Mostrar información básica
    document.getElementById('infoBatchBasica').innerHTML = `
      <p><strong>Sistema:</strong> ${data.batch_info.sistema_tag}</p>
      <p><strong>Inicio:</strong> ${data.batch_info.fecha_inicio}</p>
      <p><strong>Fin:</strong> ${data.batch_info.fecha_fin}</p>
      <p><strong>Duración:</strong> ${
        data.batch_info.duracion_minutos != null
          ? (Math.trunc(data.batch_info.duracion_minutos * 100) / 100)
          : 'N/A'
      } minutos</p>
    `;

    // Mostrar estadísticas
    document.getElementById('estadisticasBatch').innerHTML = `
      <div class="row">
        <div class="col-md-6">
          <p><strong>Masa Total:</strong> ${
            data.batch_info.mass_total_kg != null
              ? (Math.trunc(data.batch_info.mass_total_kg * 100) / 100)
              : 'N/A'
          } kg</p>

          <p><strong>Volumen Bruto:</strong> ${
            data.batch_info.vol_total != null
              ? (Math.trunc(data.batch_info.vol_total * 100) / 100)
              : 'N/A'
          } gal</p>

          <p><strong>Temp. Promedio:</strong> ${
            data.batch_info.temperatura_coriolis_prom_f != null
              ? (Math.trunc(data.batch_info.temperatura_coriolis_prom_f * 100) / 100)
              : 'N/A'
          } °F</p>
        </div>

        <div class="col-md-6">
          <p><strong>Presión Promedio:</strong> ${
            data.batch_info.presion_out_prom != null
              ? (Math.trunc(data.batch_info.presion_out_prom * 100) / 100)
              : 'N/A'
          } psi</p>

          <p><strong>Densidad Promedio:</strong> ${
            data.batch_info.densidad_prom != null
              ? (Math.trunc(data.batch_info.densidad_prom * 1000000) / 1000000)
              : 'N/A'
          } g/cc</p>

          <p><strong>Total Registros:</strong> ${data.batch_info.total_registros}</p>
        </div>
      </div>
    `;

    // Mostrar diagnóstico
    renderDiagnosticoBatch(data.diagnostico);
    
    // Controlar estado del botón de asignar ticket
    actualizarEstadoBotonTicket(data.batch_info.num_ticket);
    
    // Crear el gráfico principal
    const limites = {
        lim_inf: data.lim_inf_caudal_masico,
        lim_sup: data.lim_sup_caudal_masico
    };
    crearGraficoBatch(data.datos_grafico, limites);
    
    // Crear el gráfico técnico
    crearGraficoTecnicoBatch(data.datos_grafico, limites);
    
    // Configurar eventos de los checkboxes
    configurarEventosGraficoBatch();
    configurarEventosGraficoTecnicoBatch();

    // Actualizar sección de Incertidumbre (si hay datos)
    actualizarSeccionIncertidumbre(data.incertidumbre);
    
    // Cerrar otros modales antes de mostrar el detalle
    const modalTickets = document.getElementById('modalListarTickets');
    const modalBatches = document.getElementById('modalBuscarBatches');
    
    if (modalTickets) {
        const bsModalTickets = bootstrap.Modal.getInstance(modalTickets);
        if (bsModalTickets) {
            bsModalTickets.hide();
        }
    }
    
    if (modalBatches) {
        const bsModalBatches = bootstrap.Modal.getInstance(modalBatches);
        if (bsModalBatches) {
            bsModalBatches.hide();
        }
    }
    
    // Mostrar el modal de detalle después de un pequeño delay para que se cierren los otros modales
    setTimeout(() => {
        const modal = new bootstrap.Modal(document.getElementById('modalDetalleBatch'));
        modal.show();
    }, 300);
}

// Renderiza el bloque de diagnóstico del medidor
function renderDiagnosticoBatch(diagnostico) {
    const contenedor = document.getElementById('diagnosticoBatch');
    if (!contenedor) return;

    if (!diagnostico) {
        contenedor.innerHTML = `
            <div class="alert alert-secondary mb-0">
                <i class="bi bi-info-circle"></i> Diagnóstico no disponible para este batch.
            </div>
        `;
        return;
    }

    const estados = {
        'OK': { clase: 'success', icono: 'bi-check-circle', texto: 'Diagnóstico dentro de parámetros' },
        'ALERTA': { clase: 'danger', icono: 'bi-exclamation-triangle', texto: 'Diagnóstico con alertas' },
        'SIN_DATOS': { clase: 'secondary', icono: 'bi-info-circle', texto: 'Sin datos de diagnóstico' }
    };

    const estado = estados[diagnostico.estado_general] || estados['SIN_DATOS'];
    const mensajes = Array.isArray(diagnostico.mensajes) ? diagnostico.mensajes : [];
    const mensajesHTML = mensajes.length
        ? `<ul class="mb-0 ps-3">${mensajes.map(msg => `<li>${msg}</li>`).join('')}</ul>`
        : '<p class="mb-0">Sin mensajes adicionales.</p>';

    const alarmas = Array.isArray(diagnostico.alarmas_detectadas) ? diagnostico.alarmas_detectadas : [];
    const alarmasHTML = alarmas.length
        ? `<p class="mb-0"><strong>Alarmas detectadas:</strong> ${alarmas.join(', ')}</p>`
        : '';

    const multifaseHTML = renderDiagnosticoMultifase(diagnostico.multifase);
    const saludHTML = renderDiagnosticoSalud(diagnostico.salud_medidor);
    const parametrosHTML = renderDiagnosticoParametros(diagnostico.parametros);

    contenedor.innerHTML = `
        <div class="d-flex align-items-center mb-2">
            <i class="bi ${estado.icono} text-${estado.clase} fs-4 me-2"></i>
            <h6 class="mb-0">${estado.texto}</h6>
        </div>
        <div class="alert alert-${estado.clase} mb-3">
            ${mensajesHTML}
        </div>
        ${alarmasHTML}
        ${multifaseHTML}
        ${saludHTML}
        ${parametrosHTML}
    `;
}

function renderDiagnosticoMultifase(multifase) {
    if (!multifase) {
        return `
            <div class="alert alert-secondary">
                <i class="bi bi-info-circle"></i> Sin datos para diagnóstico de fluido/multifase.
            </div>
        `;
    }

    const detalles = Array.isArray(multifase.detalles) ? multifase.detalles : [];
    const cards = detalles.length ? detalles.map(renderDiagnosticoDetalleCard).join('') : '<div class="text-muted"><em>Sin indicadores configurados.</em></div>';

    return `
        <div class="mt-3">
            <h6 class="fw-bold mb-2"><i class="bi bi-droplet-half me-1"></i> Fluido / Multífases</h6>
            <div class="text-muted small mb-2">
                <strong>Densidad GLP ref:</strong> ${formatearDiagnosticoValor(multifase.densidad_glp_referencia)} g/cc ·
                <strong>Variación:</strong> ${formatearDiagnosticoValor(multifase.variacion_glp_pct)} %
            </div>
            <div class="row g-3">
                ${cards}
            </div>
        </div>
    `;
}

function renderDiagnosticoDetalleCard(detalle) {
    const estado = detalle.estado || 'SIN_DATOS';
    const color = estado === 'ALERTA' ? 'danger' : (estado === 'OK' ? 'success' : 'secondary');
    const valor = detalle.valor !== undefined && detalle.valor !== null
        ? `<div class="text-muted small mb-0">Valor: ${formatearDiagnosticoValor(detalle.valor)} ${detalle.unidad || ''}</div>`
        : '';

    return `
        <div class="col-md-6 col-xl-3">
            <div class="border rounded h-100 p-3">
                <div class="d-flex align-items-center mb-2">
                    <span class="badge bg-${color} me-2">${estado}</span>
                    <h6 class="mb-0">${detalle.titulo || detalle.id}</h6>
                </div>
                <p class="mb-2">${detalle.mensaje || 'Sin descripción.'}</p>
                ${valor}
            </div>
        </div>
    `;
}

function renderDiagnosticoSalud(salud) {
    if (!salud) {
        return `
            <div class="alert alert-secondary mt-3">
                <i class="bi bi-info-circle"></i> Sin datos para diagnóstico de la salud del medidor.
            </div>
        `;
    }

    const indicadores = Array.isArray(salud.indicadores) ? salud.indicadores : [];
    const filas = indicadores.length
        ? indicadores.map(ind => {
            const estado = ind.estado || 'SIN_DATOS';
            const color = estado === 'ALERTA' ? 'danger' : (estado === 'OK' ? 'success' : 'secondary');
            const umbral = ind.umbral !== undefined && ind.umbral !== null ? formatearDiagnosticoValor(ind.umbral) : 'N/A';
            return `
                <tr>
                    <td>${ind.label || ind.id}</td>
                    <td>${formatearDiagnosticoValor(ind.valor)} ${ind.unidad || ''}</td>
                    <td>${umbral} ${ind.unidad || ''}</td>
                    <td><span class="badge bg-${color}">${estado}</span></td>
                    <td>${ind.descripcion || ''}</td>
                </tr>
            `;
        }).join('')
        : '';

    const tablaIndicadores = filas
        ? `
            <div class="table-responsive">
                <table class="table table-sm align-middle mb-2">
                    <thead>
                        <tr>
                            <th>Indicador</th>
                            <th>Valor</th>
                            <th>Umbral</th>
                            <th>Estado</th>
                            <th>Detalle</th>
                        </tr>
                    </thead>
                    <tbody>${filas}</tbody>
                </table>
            </div>
        `
        : '<p class="mb-2"><em>No hay indicadores definidos.</em></p>';

    const mensajes = Array.isArray(salud.mensajes) ? salud.mensajes : [];
    const mensajesHTML = mensajes.length
        ? `<ul class="mb-0 ps-3">${mensajes.map(msg => `<li>${msg}</li>`).join('')}</ul>`
        : '<p class="mb-0 text-muted">Sin observaciones adicionales.</p>';

    return `
        <div class="mt-4">
            <h6 class="fw-bold mb-2"><i class="bi bi-activity me-1"></i> Salud del medidor</h6>
            ${tablaIndicadores}
            <div class="alert alert-light border mb-0">${mensajesHTML}</div>
        </div>
    `;
}

function renderDiagnosticoParametros(parametros) {
    const lista = Array.isArray(parametros) ? parametros : [];
    if (!lista.length) {
        return '<p class="mb-0 mt-3"><em>No hay parámetros de diagnóstico para mostrar.</em></p>';
    }

    const filas = lista.map(param => {
        const metricas = param.metricas || {};
        const unidad = param.unidad ? ` <small class="text-muted">(${param.unidad})</small>` : '';
        const estadoParametro = param.en_alarma
            ? '<span class="badge bg-danger">Alarma</span>'
            : '<span class="badge bg-success">OK</span>';
        return `
            <tr>
                <td>${param.label}${unidad}</td>
                <td>${formatearDiagnosticoValor(metricas.ultimo)}</td>
                <td>${formatearDiagnosticoValor(metricas.promedio)}</td>
                <td>${formatearDiagnosticoValor(metricas.min)}</td>
                <td>${formatearDiagnosticoValor(metricas.max)}</td>
                <td>${estadoParametro}</td>
            </tr>
        `;
    }).join('');

    return `
        <div class="table-responsive mt-4">
            <table class="table table-sm align-middle mb-0">
                <thead>
                    <tr>
                        <th>Parámetro</th>
                        <th>Último</th>
                        <th>Promedio</th>
                        <th>Mínimo</th>
                        <th>Máximo</th>
                        <th>Estado</th>
                    </tr>
                </thead>
                <tbody>${filas}</tbody>
            </table>
        </div>
    `;
}

function formatearDiagnosticoValor(valor) {
    if (valor === null || valor === undefined || Number.isNaN(valor)) {
        return 'N/A';
    }
    const absValor = Math.abs(valor);
    let decimales = 3;
    if (absValor >= 1000) {
        decimales = 0;
    } else if (absValor >= 100) {
        decimales = 1;
    } else if (absValor >= 10) {
        decimales = 2;
    }
    return Number.parseFloat(valor).toFixed(decimales);
}

// Función para crear el gráfico del batch
function crearGraficoBatch(datos, limites) {
    const ctx = document.getElementById('batchChart').getContext('2d');
    
    // Destruir gráfico anterior si existe
    if (batchChart) {
        batchChart.destroy();
    }
    
    // Preparar datos para Chart.js
    const labels = datos.map(d => d.fecha_hora);
    
    // Separar datos del batch y del contexto para diferentes estilos
    const datosBatch = datos.filter(d => d.dentro_batch);
    const datosContexto = datos.filter(d => !d.dentro_batch);
    
    const datasets = [
        // Flujo másico completo (contexto + batch) como una sola curva continua
        {
            label: 'Flujo Másico - Batch (kg/min)',
            data: datos.map(d => d.mass_rate_kg_min),
            borderColor: datos.map(d => d.dentro_batch ? '#007bff' : '#004085'), // Azul normal para batch, azul oscuro para contexto
            backgroundColor: '#007bff20',
            yAxisID: 'y1',
            tension: 0.4,
            pointRadius: datos.map(d => d.dentro_batch ? 3 : 1), // Puntos más grandes para el batch
            pointBorderColor: datos.map(d => d.dentro_batch ? '#007bff' : '#004085'),
            pointBackgroundColor: datos.map(d => d.dentro_batch ? '#007bff' : '#004085'),
            borderWidth: 2,
            segment: {
                borderColor: function(ctx) {
                    // Cambiar color del segmento según si está en el batch o contexto
                    const currentIndex = ctx.p0DataIndex;
                    const isInBatch = datos[currentIndex]?.dentro_batch;
                    return isInBatch ? '#007bff' : '#004085';
                },
                borderWidth: function(ctx) {
                    // Línea más gruesa para el batch
                    const currentIndex = ctx.p0DataIndex;
                    const isInBatch = datos[currentIndex]?.dentro_batch;
                    return isInBatch ? 3 : 2;
                }
            },
            hidden: false
        },
        // Masa total completa (contexto + batch) como una sola curva continua
        {
            label: 'Masa Total - Batch (kg)',
            data: datos.map(d => d.total_mass_kg),
            borderColor: datos.map(d => d.dentro_batch ? '#28a745' : '#155724'), // Verde normal para batch, verde oscuro para contexto
            backgroundColor: '#28a74520',
            yAxisID: 'y2',
            tension: 0.4,
            pointRadius: datos.map(d => d.dentro_batch ? 3 : 1),
            pointBorderColor: datos.map(d => d.dentro_batch ? '#28a745' : '#155724'),
            pointBackgroundColor: datos.map(d => d.dentro_batch ? '#28a745' : '#155724'),
            borderWidth: 2,
            segment: {
                borderColor: function(ctx) {
                    const currentIndex = ctx.p0DataIndex;
                    const isInBatch = datos[currentIndex]?.dentro_batch;
                    return isInBatch ? '#28a745' : '#155724';
                },
                borderWidth: function(ctx) {
                    const currentIndex = ctx.p0DataIndex;
                    const isInBatch = datos[currentIndex]?.dentro_batch;
                    return isInBatch ? 3 : 2;
                }
            },
            hidden: false
        },
        {
            label: 'Temperatura (°F)',
            data: datos.map(d => d.coriolis_temperature_f),
            borderColor: '#ffc107',
            backgroundColor: '#ffc10720',
            yAxisID: 'y3',
            tension: 0.4,
            pointRadius: 2,
            hidden: true
        },
        {
            label: 'Presión (psi)',
            data: datos.map(d => d.pressure_out),
            borderColor: '#fd7e14',
            backgroundColor: '#fd7e1420',
            yAxisID: 'y4',
            tension: 0.4,
            pointRadius: 2,
            hidden: true
        },
        {
            label: 'Densidad (g/cc)',
            data: datos.map(d => d.density),
            borderColor: '#6f42c1',
            backgroundColor: '#6f42c120',
            yAxisID: 'y5',
            tension: 0.4,
            pointRadius: 2,
            hidden: true
        }
    ];
    
    // Agregar líneas horizontales para los límites usando datasets
    if (limites && limites.lim_inf !== undefined) {
        datasets.push({
            label: `Límite Inferior (${limites.lim_inf} kg/min)`,
            data: datos.map(() => limites.lim_inf),
            borderColor: 'red',
            backgroundColor: 'transparent',
            borderDash: [5, 5],
            borderWidth: 2,
            yAxisID: 'y1',
            pointRadius: 0,
            pointHoverRadius: 0,
            tension: 0,
            hidden: false,
            type: 'line'
        });
    }
    
    if (limites && limites.lim_sup !== undefined) {
        datasets.push({
            label: `Límite Superior (${limites.lim_sup} kg/min)`,
            data: datos.map(() => limites.lim_sup),
            borderColor: 'red',
            backgroundColor: 'transparent',
            borderDash: [5, 5],
            borderWidth: 2,
            yAxisID: 'y1',
            pointRadius: 0,
            pointHoverRadius: 0,
            tension: 0,
            hidden: false,
            type: 'line'
        });
    }
    
    // Encontrar índices de inicio y fin del batch para las líneas verticales
    const indiceInicio = datos.findIndex(d => d.dentro_batch);
    const indiceFin = datos.length - 1 - datos.slice().reverse().findIndex(d => d.dentro_batch);
    
    batchChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 15
                    }
                },
                tooltip: {
                    callbacks: {
                        title: function(context) {
                            return context[0].label;
                        },
                        label: function(context) {
                            const punto = datos[context.dataIndex];
                            const prefijo = punto.dentro_batch ? '🔹 Batch: ' : '⚫ Contexto: ';
                            return prefijo + context.dataset.label + ': ' + context.formattedValue;
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Tiempo'
                    }
                },
                y1: {
                    type: 'linear',
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Flujo Másico (kg/min)'
                    },
                    grid: {
                        color: '#007bff40'
                    }
                },
                y2: {
                    type: 'linear',
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Masa Total (kg)'
                    },
                    grid: {
                        drawOnChartArea: false,
                        color: '#28a74540'
                    }
                },
                y3: {
                    type: 'linear',
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Temperatura (°F)'
                    },
                    grid: {
                        drawOnChartArea: false,
                        color: '#ffc10740'
                    },
                    display: false
                },
                y4: {
                    type: 'linear',
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Presión (psi)'
                    },
                    grid: {
                        drawOnChartArea: false,
                        color: '#fd7e1440'
                    },
                    display: false
                },
                y5: {
                    type: 'linear',
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Densidad (g/cc)'
                    },
                    grid: {
                        drawOnChartArea: false,
                        color: '#6f42c140'
                    },
                    display: false
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.parsed.y?.toFixed(2)}`;
                        }
                    }
                }
            }
        }
    });
}

// Función para configurar eventos de los checkboxes
function configurarEventosGraficoBatch() {
    const checkboxes = ['showMassRate', 'showTotalMass', 'showTemperature', 'showPressure', 'showDensity'];
    const datasets = [0, 1, 2, 3, 4]; // Índices de los datasets
    const scales = ['y1', 'y2', 'y3', 'y4', 'y5']; // Escalas correspondientes
    
    checkboxes.forEach((checkboxId, index) => {
        const checkbox = document.getElementById(checkboxId);
        if (checkbox) {
            checkbox.addEventListener('change', function() {
                if (batchChart) {
                    const dataset = batchChart.data.datasets[datasets[index]];
                    const scale = scales[index];
                    
                    dataset.hidden = !this.checked;
                    batchChart.options.scales[scale].display = this.checked;
                    batchChart.update();
                }
            });
        }
    });
}

// Actualiza los campos de la sección Incertidumbre de forma segura
function actualizarSeccionIncertidumbre(inc) {
    const setVal = (id, val) => {
        const el = document.getElementById(id);
        if (!el) return;
        el.value = (val === null || val === undefined) ? '' : val;
    };
    const setText = (id, val) => {
        const target = document.getElementById(id);
        if (!target) return;
        target.textContent = (val === null || val === undefined || val === '') ? '-' : val;
    };

    // Limpiar si no hay datos
    if (!inc) {
        ['NSV','masa','U','Uexp','k','Urel','uMF','cMF','crMF','udl','cdl','crdl'].forEach(id=>setVal(id, ''));
        setText('valorMasa', '-');
        setText('valorDensidad', '-');
        return;
    }

    // Resumen (columna izquierda) - nombres exactos
    setVal('NSV', inc.NSV);
    setVal('masa', inc.masa);
    setVal('U', inc.U);
    setVal('Uexp', inc.Uexp);
    setVal('k', inc.k);
    setVal('Urel', inc.Urel);

    // Tabla (columna derecha) - nombres exactos
    setVal('uMF', inc.uMF);
    setVal('udl', inc.udl);
    setVal('cMF', inc.cMF);
    setVal('cdl', inc.cdl);
    setVal('crMF', inc.crMF);
    setVal('crdl', inc.crdl);

    setText('valorMasa', inc.masa);
    const densidadProm = datosActualesBatch?.batch_info?.densidad_prom;
    let densidadTexto = '-';
    if (densidadProm !== null && densidadProm !== undefined) {
        densidadTexto = Number.parseFloat(densidadProm).toFixed(3);
    }
    setText('valorDensidad', densidadTexto);
}

// Función para descargar PDF del ticket del batch
function descargarDatosBatch() {
    if (datosActualesBatch && datosActualesBatch.batch_info) {
        const batchId = datosActualesBatch.batch_info.id;
        // Abrir PDF en nueva ventana para descarga
        window.open(`/monitoreo/pdf/ticket-batch/${batchId}/`, '_blank');
    } else {
        alert('No hay datos del batch disponibles para descargar.');
    }
}

// Función para controlar el estado del botón de asignar ticket
function actualizarEstadoBotonTicket(numTicket) {
    const btn = document.getElementById('btnAsignarTicket');
    
    // Verificar si el botón existe (puede no existir si el usuario no tiene permisos)
    if (!btn) {
        return;
    }
    
    if (numTicket) {
        // Ya tiene ticket - deshabilitar botón
        btn.disabled = true;
        btn.className = 'btn btn-secondary';
        btn.innerHTML = '<i class="bi bi-check-circle"></i> Ticket ya asignado';
    } else {
        // No tiene ticket - habilitar botón
        btn.disabled = false;
        btn.className = 'btn btn-warning';
        btn.innerHTML = '<i class="bi bi-ticket-perforated"></i> Asignar Ticket';
    }
}

// Función para asignar ticket al batch
async function asignarTicketBatch() {
    if (!datosActualesBatch || !datosActualesBatch.batch_info) {
        showErrorAlert('Error', 'No hay datos del batch disponibles');
        return;
    }
    
    const batchId = datosActualesBatch.batch_info.id;
    const batchNumTicket = datosActualesBatch.batch_info.num_ticket;
    
    // Verificar si ya tiene ticket asignado - NO permitir reasignación
    if (batchNumTicket) {
        showWarningAlert(
            'Ticket ya asignado', 
            `Este batch ya tiene el ticket #${batchNumTicket} asignado. No se puede reasignar.`
        );
        return;
    }
    
    // Mostrar confirmación antes de asignar
    const confirmResult = await showConfirmAlert(
        'Confirmar asignación de ticket',
        '¿Está seguro que desea asignar un ticket a este batch?',
        {
            confirmButtonText: 'Sí, asignar',
            cancelButtonText: 'Cancelar'
        }
    );
    
    if (!confirmResult.isConfirmed) {
        return;
    }
    
    try {
        // Verificar que el botón existe (permisos)
        const btn = document.getElementById('btnAsignarTicket');
        if (!btn) {
            showPermissionDeniedAlert('No tiene permisos para asignar tickets');
            return;
        }
        
        // Mostrar loading
        showLoadingAlert('Asignando ticket...', 'Por favor espere mientras se procesa la asignación');
        
        const response = await fetch(`/monitoreo/api/asignar-ticket-batch/${batchId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            }
        });
        
        // Cerrar loading
        hideLoadingAlert();
        
        // Verificar si hay error de permisos
        if (response.status === 403) {
            const data = await response.json();
            const errorMsg = data.error || 'No tiene permisos para esta acción. Contacte al administrador.';
            showPermissionDeniedAlert(errorMsg);
            return;
        }
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            // Mostrar éxito con SweetAlert2
            await showSuccessAlert(
                'Ticket asignado exitosamente',
                `¡Ticket #${data.data.ticket_asignado} asignado correctamente al batch!`
            );
            
            // Actualizar la información del batch en el modal
            datosActualesBatch.batch_info.num_ticket = data.data.ticket_asignado;
            
            // Actualizar el título del modal con el número de ticket
            const modalTitle = document.getElementById('modalDetalleBatchLabel');
            if (modalTitle) {
                modalTitle.innerHTML = `
                    <div class="d-flex align-items-center justify-content-center w-100">
                        <i class="bi bi-graph-up"></i> 
                        <span class="ms-2">Detalle del Batch Detectado</span>
                        <span class="badge bg-success ms-2">Ticket #${data.data.ticket_asignado}</span>
                    </div>
                `;
            }
            
            // Actualizar la visualización
            document.getElementById('infoBatchBasica').innerHTML = `
                <p><strong>Sistema:</strong> ${datosActualesBatch.batch_info.sistema_tag}</p>
                <p><strong>Inicio:</strong> ${datosActualesBatch.batch_info.fecha_inicio}</p>
                <p><strong>Fin:</strong> ${datosActualesBatch.batch_info.fecha_fin}</p>
                <p><strong>Duración:</strong> ${(datosActualesBatch.batch_info.duracion_minutos !== null && datosActualesBatch.batch_info.duracion_minutos !== undefined) ? Math.trunc(datosActualesBatch.batch_info.duracion_minutos * 100) / 100 : 'N/A'} minutos</p>
                <div class="alert alert-info mt-2 mb-0" style="padding: 8px 12px; font-size: 0.85em;">
                    <i class="bi bi-info-circle"></i> 
                    <strong>Contexto extendido:</strong> La gráfica muestra 3 minutos antes y después del batch para mejor análisis.
                    <br>🔹 <strong>Línea azul clara:</strong> Datos del batch detectado (línea gruesa, puntos grandes)
                    <br>🔷 <strong>Línea azul oscura:</strong> Datos de contexto - antes/después (línea más fina, puntos pequeños)
                </div>
            `;
            
            // Actualizar el estado del botón (ya no se podrá usar)
            actualizarEstadoBotonTicket(data.data.ticket_asignado);
            
            // Disparar evento personalizado para notificar que se asignó un ticket
            const eventoTicketAsignado = new CustomEvent('ticketAsignado', {
                detail: {
                    batchId: batchId,
                    numTicket: data.data.ticket_asignado
                }
            });
            window.dispatchEvent(eventoTicketAsignado);
            
        } else {
            // Mostrar error con SweetAlert2
            showErrorAlert(
                'Error al asignar ticket',
                data.error || 'Ha ocurrido un error inesperado'
            );
        }
    } catch (error) {
        // Cerrar loading si está abierto
        hideLoadingAlert();
        
        console.error('Error al asignar ticket:', error);
        showErrorAlert(
            'Error de conexión',
            'No se pudo conectar con el servidor. Verifique su conexión a internet.'
        );
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

// Función para crear el gráfico técnico del batch
function crearGraficoTecnicoBatch(datos, limites) {
    const ctx = document.getElementById('batchChartTecnico').getContext('2d');
    
    // Destruir gráfico anterior si existe
    if (batchChartTecnico) {
        batchChartTecnico.destroy();
    }
    
    // Preparar datos para Chart.js
    const labels = datos.map(d => d.fecha_hora);
    
    const datasets = [
        // Caudal másico (igual al gráfico principal)
        {
            label: 'Caudal Másico (kg/min)',
            data: datos.map(d => d.mass_rate_kg_min),
            borderColor: datos.map(d => d.dentro_batch ? '#007bff' : '#004085'),
            backgroundColor: '#007bff20',
            yAxisID: 'y1',
            tension: 0.4,
            pointRadius: datos.map(d => d.dentro_batch ? 3 : 1),
            pointBorderColor: datos.map(d => d.dentro_batch ? '#007bff' : '#004085'),
            pointBackgroundColor: datos.map(d => d.dentro_batch ? '#007bff' : '#004085'),
            borderWidth: 2,
            segment: {
                borderColor: function(ctx) {
                    const currentIndex = ctx.p0DataIndex;
                    const isInBatch = datos[currentIndex]?.dentro_batch;
                    return isInBatch ? '#007bff' : '#004085';
                },
                borderWidth: function(ctx) {
                    const currentIndex = ctx.p0DataIndex;
                    const isInBatch = datos[currentIndex]?.dentro_batch;
                    return isInBatch ? 3 : 2;
                }
            },
            hidden: false
        },
        // Densidad
        {
            label: 'Densidad (g/cc)',
            data: datos.map(d => d.density),
            borderColor: datos.map(d => d.dentro_batch ? '#6f42c1' : '#4a2c7a'),
            backgroundColor: '#6f42c120',
            yAxisID: 'y2',
            tension: 0.4,
            pointRadius: datos.map(d => d.dentro_batch ? 3 : 1),
            pointBorderColor: datos.map(d => d.dentro_batch ? '#6f42c1' : '#4a2c7a'),
            pointBackgroundColor: datos.map(d => d.dentro_batch ? '#6f42c1' : '#4a2c7a'),
            borderWidth: 2,
            segment: {
                borderColor: function(ctx) {
                    const currentIndex = ctx.p0DataIndex;
                    const isInBatch = datos[currentIndex]?.dentro_batch;
                    return isInBatch ? '#6f42c1' : '#4a2c7a';
                },
                borderWidth: function(ctx) {
                    const currentIndex = ctx.p0DataIndex;
                    const isInBatch = datos[currentIndex]?.dentro_batch;
                    return isInBatch ? 3 : 2;
                }
            },
            hidden: false
        },
        // Driver Current
        {
            label: 'Driver Current (mA)',
            data: datos.map(d => d.driver_current_ma || d.driver_current || d.driver_curr),
            borderColor: '#e74c3c',
            backgroundColor: '#e74c3c20',
            yAxisID: 'y3',
            tension: 0.4,
            pointRadius: 2,
            hidden: true
        },
        // Driver Amplitude
        {
            label: 'Driver Amplitude',
            data: datos.map(d => d.dsp_rxmsg_driverAmplitude || d.driver_amplitude || d.dsp_rwsg_driverAmplitude),
            borderColor: '#f39c12',
            backgroundColor: '#f39c1220',
            yAxisID: 'y4',
            tension: 0.4,
            pointRadius: 2,
            hidden: true
        },
        // Noise N1
        {
            label: 'Noise N1',
            data: datos.map(d => d.dsp_rxmsg_noiseEstimatedN1 || d.dsp_rwsg_noiseEstimatedN1 || d.noise_n1 || d.ruido_n1),
            borderColor: '#e91e63',
            backgroundColor: '#e91e6320',
            yAxisID: 'y5',
            tension: 0.4,
            pointRadius: 2,
            hidden: true
        },
        // Noise N2
        {
            label: 'Noise N2',
            data: datos.map(d => d.dsp_rxmsg_noiseEstimatedN2 || d.dsp_rwsg_noiseEstimatedN2 || d.noise_n2 || d.ruido_n2),
            borderColor: '#f48fb1',
            backgroundColor: '#f48fb120',
            yAxisID: 'y6',
            tension: 0.4,
            pointRadius: 2,
            hidden: true
        },
        // Frecuencia
        {
            label: 'Frecuencia (Hz)',
            data: datos.map(d => d.coriolis_frequency || d.coriolis_frecuency || d.frequency_hz || d.frecuencia),
            borderColor: '#1abc9c',
            backgroundColor: '#1abc9c20',
            yAxisID: 'y7',
            tension: 0.4,
            pointRadius: 2,
            hidden: true
        }
    ];
    
    batchChartTecnico = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 15
                    }
                },
                tooltip: {
                    callbacks: {
                        title: function(context) {
                            return context[0].label;
                        },
                        label: function(context) {
                            const punto = datos[context.dataIndex];
                            const prefijo = punto.dentro_batch ? '🔹 Batch: ' : '⚫ Contexto: ';
                            return prefijo + context.dataset.label + ': ' + context.formattedValue;
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Tiempo'
                    }
                },
                y1: {
                    type: 'linear',
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Caudal Másico (kg/min)'
                    },
                    grid: {
                        color: '#007bff40'
                    }
                },
                y2: {
                    type: 'linear',
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Densidad (g/cc)'
                    },
                    grid: {
                        drawOnChartArea: false,
                        color: '#6f42c140'
                    }
                },
                y3: {
                    type: 'linear',
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Driver Current (mA)'
                    },
                    grid: {
                        drawOnChartArea: false,
                        color: '#e74c3c40'
                    },
                    display: false
                },
                y4: {
                    type: 'linear',
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Driver Amplitude'
                    },
                    grid: {
                        drawOnChartArea: false,
                        color: '#f39c1240'
                    },
                    display: false
                },
                y5: {
                    type: 'linear',
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Noise N1'
                    },
                    grid: {
                        drawOnChartArea: false,
                        color: '#e91e6340'
                    },
                    display: false
                },
                y6: {
                    type: 'linear',
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Noise N2'
                    },
                    grid: {
                        drawOnChartArea: false,
                        color: '#f48fb140'
                    },
                    display: false
                },
                y7: {
                    type: 'linear',
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Frecuencia (Hz)'
                    },
                    grid: {
                        drawOnChartArea: false,
                        color: '#1abc9c40'
                    },
                    display: false
                }
            }
        }
    });
}

// Función para configurar eventos de los checkboxes del gráfico técnico
function configurarEventosGraficoTecnicoBatch() {
    const checkboxes = ['showFlowRate', 'showDensityTech', 'showDriverCurrent', 'showDriverAmplitude', 'showNoiseN1', 'showNoiseN2', 'showFrequency'];
    const datasets = [0, 1, 2, 3, 4, 5, 6]; // Índices de los datasets
    const scales = ['y1', 'y2', 'y3', 'y4', 'y5', 'y6', 'y7']; // Escalas correspondientes
    
    checkboxes.forEach((checkboxId, index) => {
        // Usar querySelectorAll para manejar checkboxes duplicados
        const checkboxElements = document.querySelectorAll(`#${checkboxId}`);
        checkboxElements.forEach(checkbox => {
            if (checkbox) {
                checkbox.addEventListener('change', function() {
                    if (batchChartTecnico) {
                        const dataset = batchChartTecnico.data.datasets[datasets[index]];
                        const scale = scales[index];
                        
                        dataset.hidden = !this.checked;
                        batchChartTecnico.options.scales[scale].display = this.checked;
                        
                        // Sincronizar todos los checkboxes con el mismo ID
                        checkboxElements.forEach(cb => {
                            if (cb !== this) {
                                cb.checked = this.checked;
                            }
                        });
                        
                        batchChartTecnico.update();
                    }
                });
            }
        });
    });
}