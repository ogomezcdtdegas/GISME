/**
 * JavaScript para el modal de configuración del sistema
 * Incluye funciones para cargar, validar y actualizar coeficientes del sistema
 */

document.addEventListener('DOMContentLoaded', function() {
    // Elementos del DOM
    const modal = document.getElementById('modalConfiguracionSistema');
    const btnActualizar = document.getElementById('btnActualizarCoeficientes');
    const form = document.getElementById('formConfiguracionSistema');
    
    // Funciones de utilidad para manejar inputs
    const setInputValue = (id, value) => {
        const el = document.getElementById(id);
        if (el) {
            el.value = value;
        }
    };
    
    const getInputValue = (id, parser = parseFloat) => {
        const el = document.getElementById(id);
        if (!el) {
            return null;
        }
        return parser === null ? el.value : parser(el.value);
    };
    
    // Manejar eventos del modal
    if (modal) {
        modal.addEventListener('hidden.bs.modal', function () {
            // Quitar el foco de cualquier elemento que pueda estar enfocado
            if (document.activeElement) {
                document.activeElement.blur();
            }
        });
        
        modal.addEventListener('hide.bs.modal', function () {
            // Quitar el foco antes de que el modal se cierre
            if (document.activeElement) {
                document.activeElement.blur();
            }
        });
        
        // Cargar valores actuales al abrir el modal
        modal.addEventListener('show.bs.modal', function () {
            cargarCoeficientesActuales();
        });
    }

    // Manejar click del botón Actualizar (si el usuario tiene permisos)
    if (btnActualizar) {
        btnActualizar.addEventListener('click', function() {
            actualizarCoeficientes();
        });
    }

    function cargarCoeficientesActuales() {
        //console.log('Cargando coeficientes actuales...');
        
        // Obtener el ID del sistema desde la URL
        const sistemaId = obtenerSistemaIdDesdeURL();
        
        if (!sistemaId) {
            //console.warn('No se encontró ID del sistema actual. Usando valores por defecto.');
            cargarValoresPorDefecto();
            return;
        }

        // Guardar el ID del sistema para uso posterior
        window.SISTEMA_ACTUAL = { id: sistemaId };

        // Cargar coeficientes desde el backend
        fetch(`/complementos/api/coeficientes/${sistemaId}/`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success && data.data) {
                setInputValue('tempSalidaM', data.data.mt ?? '1.0');
                setInputValue('tempSalidaB', data.data.bt ?? '0.0');
                setInputValue('presionSalidaM', data.data.mp ?? '1.0');
                setInputValue('presionSalidaB', data.data.bp ?? '0.0');
                
                // Nuevos campos de configuración de batch
                setInputValue('limInfCaudalMasico', data.data.lim_inf_caudal_masico ?? '0.0');
                setInputValue('limSupCaudalMasico', data.data.lim_sup_caudal_masico ?? '1000000.0');
                setInputValue('volMasicoIniBatch', data.data.vol_masico_ini_batch ?? '0.0');
                setInputValue('timeFinishedBatch', data.data.time_finished_batch ?? '2.0');

                // Campos de incertidumbre
                setInputValue('MF', data.data.mf ?? '1.0');
                setInputValue('vis', data.data.vis ?? '0.0');
                setInputValue('deltavis', data.data.deltavis ?? '0.0');
                setInputValue('DN', data.data.dn ?? '0.0');
                setInputValue('ucalDens', data.data.ucal_dens ?? '0.0');
                setInputValue('kcalDens', data.data.kcal_dens ?? '0.0');
                setInputValue('tipdens', data.data.tipdens ?? '');
                setInputValue('desvdens', data.data.desv_dens ?? '0.0');
                setInputValue('ucalMet', data.data.ucal_met ?? '0.0');
                setInputValue('kcalMet', data.data.kcal_met ?? '0.0');
                setInputValue('esisMet', data.data.esis_met ?? '0.0');
                setInputValue('ucartaMet', data.data.ucarta_met ?? '0.0');
                setInputValue('zeroStab', data.data.zero_stab ?? '0.0');
                
                const diagInputs = {
                    diagnosticGlpDensityRef: data.data.diagnostic_glp_density_ref ?? '0.55',
                    diagnosticGlpDensityTolerance: data.data.diagnostic_glp_density_tolerance_pct ?? '5',
                    diagnosticDriverAmpBase: data.data.diagnostic_driver_amp_base ?? '',
                    diagnosticDriverAmpMultiplier: data.data.diagnostic_driver_amp_multiplier ?? '1.3',
                    diagnosticN1Threshold: data.data.diagnostic_n1_threshold ?? '',
                    diagnosticN2Threshold: data.data.diagnostic_n2_threshold ?? '',
                    diagnosticAmpImbalanceThreshold: data.data.diagnostic_amp_imbalance_threshold_pct ?? '5'
                };
                
                Object.entries(diagInputs).forEach(([id, value]) => {
                    const input = document.getElementById(id);
                    if (input) {
                        input.value = value;
                    }
                });
                
                if (!data.exists) {
                    //console.info('Coeficientes no configurados. Mostrando valores por defecto.');
                }
            } else {
                //console.warn('Error al cargar coeficientes:', data.error);
                cargarValoresPorDefecto();
            }
        })
        .catch(error => {
            //console.error('Error de conexión al cargar coeficientes:', error);
            cargarValoresPorDefecto();
        });
    }

    function obtenerSistemaIdDesdeURL() {
        // Obtener el ID del sistema desde la URL actual
        // Patrón: /monitoreo/sistema/ID_DEL_SISTEMA/
        const urlPath = window.location.pathname;
        const sistemaMatch = urlPath.match(/\/sistema\/([a-f0-9-]{36})\//);
        
        if (sistemaMatch && sistemaMatch[1]) {
            //console.log('ID del sistema obtenido desde URL:', sistemaMatch[1]);
            return sistemaMatch[1];
        }
        
        //console.warn('No se pudo extraer el ID del sistema desde la URL:', urlPath);
        return null;
    }

    function cargarValoresPorDefecto() {
        const defaults = {
            tempSalidaM: '1.0',
            tempSalidaB: '0.0',
            presionSalidaM: '1.0',
            presionSalidaB: '0.0',
            limInfCaudalMasico: '0.0',
            limSupCaudalMasico: '1000000.0',
            volMasicoIniBatch: '0.0',
            timeFinishedBatch: '2.0',
            MF: '1.0',
            vis: '0.0',
            deltavis: '0.0',
            DN: '0.0',
            ucalDens: '0.0',
            kcalDens: '0.0',
            tipdens: '',
            desvdens: '0.0',
            ucalMet: '0.0',
            kcalMet: '0.0',
            esisMet: '0.0',
            ucartaMet: '0.0',
            zeroStab: '0.0',
            diagnosticGlpDensityRef: '0.55',
            diagnosticGlpDensityTolerance: '5',
            diagnosticDriverAmpBase: '',
            diagnosticDriverAmpMultiplier: '1.3',
            diagnosticN1Threshold: '',
            diagnosticN2Threshold: '',
            diagnosticAmpImbalanceThreshold: '5'
        };
        Object.entries(defaults).forEach(([id, value]) => setInputValue(id, value));
    }

    function actualizarCoeficientes() {
        // Obtener el ID del sistema actual
        const sistemaId = window.SISTEMA_ACTUAL ? window.SISTEMA_ACTUAL.id : null;
        
        if (!sistemaId) {
            showErrorAlert('No se encontró el ID del sistema actual');
            return;
        }

        // Obtener valores del formulario
        const mt = getInputValue('tempSalidaM');
        const bt = getInputValue('tempSalidaB');
        const mp = getInputValue('presionSalidaM');
        const bp = getInputValue('presionSalidaB');
        
        // Obtener valores de configuración de batch
        const limInfCaudalMasico = getInputValue('limInfCaudalMasico');
        const limSupCaudalMasico = getInputValue('limSupCaudalMasico');
        const volMasicoIniBatch = getInputValue('volMasicoIniBatch');
        const timeFinishedBatch = getInputValue('timeFinishedBatch');

        // Lectura campos incertidumbre
        const mfVal = getInputValue('MF');
        const visVal = getInputValue('vis');
        const deltavisVal = getInputValue('deltavis');
        const dnVal = getInputValue('DN');
        const ucalDensVal = getInputValue('ucalDens');
        const kcalDensVal = getInputValue('kcalDens');
        const tipdensVal = getInputValue('tipdens', null) || '';
        const desvDensVal = getInputValue('desvdens');
        const ucalMetVal = getInputValue('ucalMet');
        const kcalMetVal = getInputValue('kcalMet');
        const esisMetVal = getInputValue('esisMet');
        const ucartaMetVal = getInputValue('ucartaMet');
        const zeroStabVal = getInputValue('zeroStab');
        
        const diagGlpRefRaw = getInputValue('diagnosticGlpDensityRef', null) ?? '';
        const diagGlpToleranceRaw = getInputValue('diagnosticGlpDensityTolerance', null) ?? '';
        const diagDriverAmpBaseRaw = getInputValue('diagnosticDriverAmpBase', null) ?? '';
        const diagDriverAmpMultiplierRaw = getInputValue('diagnosticDriverAmpMultiplier', null) ?? '';
        const diagN1Raw = getInputValue('diagnosticN1Threshold', null) ?? '';
        const diagN2Raw = getInputValue('diagnosticN2Threshold', null) ?? '';
        const diagImbalanceRaw = getInputValue('diagnosticAmpImbalanceThreshold', null) ?? '';

        const diagGlpRefVal = diagGlpRefRaw === '' ? null : parseFloat(diagGlpRefRaw);
        const diagGlpToleranceVal = diagGlpToleranceRaw === '' ? null : parseFloat(diagGlpToleranceRaw);
        const diagDriverAmpBaseVal = diagDriverAmpBaseRaw === '' ? null : parseFloat(diagDriverAmpBaseRaw);
        const diagDriverAmpMultiplierVal = diagDriverAmpMultiplierRaw === '' ? null : parseFloat(diagDriverAmpMultiplierRaw);
        const diagN1Val = diagN1Raw === '' ? null : parseFloat(diagN1Raw);
        const diagN2Val = diagN2Raw === '' ? null : parseFloat(diagN2Raw);
        const diagImbalanceVal = diagImbalanceRaw === '' ? null : parseFloat(diagImbalanceRaw);

        // Validar que todos los valores son números válidos
        const requeridos = [mt, bt, mp, bp, limInfCaudalMasico, limSupCaudalMasico, volMasicoIniBatch, timeFinishedBatch];
        if (requeridos.some(v => v === null || Number.isNaN(v))) {
            showErrorAlert('Todos los valores deben ser números válidos');
            return;
        }

        // Validar campos de incertidumbre (solo si no son NaN; permitir que estén en 0)
        const incertidumbreNumericos = [mfVal, visVal, deltavisVal, dnVal, ucalDensVal, kcalDensVal, desvDensVal, ucalMetVal, kcalMetVal, esisMetVal, ucartaMetVal, zeroStabVal];
        const algunNaN = incertidumbreNumericos.some(v => isNaN(v));
        if (algunNaN) {
            showErrorAlert('Campos de incertidumbre contienen valores no numéricos');
            return;
        }

        const diagnosticoValores = [diagGlpRefVal, diagGlpToleranceVal, diagDriverAmpBaseVal, diagDriverAmpMultiplierVal, diagN1Val, diagN2Val, diagImbalanceVal];
        const diagnosticoInvalido = diagnosticoValores.some(v => v !== null && Number.isNaN(v));
        if (diagnosticoInvalido) {
            showErrorAlert('Campos de diagnóstico contienen valores no numéricos');
            return;
        }

        if (diagGlpRefVal !== null && diagGlpRefVal <= 0) {
            showErrorAlert('La densidad de referencia debe ser mayor a 0');
            return;
        }

        if (diagGlpToleranceVal !== null && diagGlpToleranceVal < 0) {
            showErrorAlert('La variación de densidad no puede ser negativa');
            return;
        }

        if (diagDriverAmpMultiplierVal !== null && diagDriverAmpMultiplierVal < 1) {
            showErrorAlert('El multiplicador de Driver Amp debe ser mayor o igual a 1');
            return;
        }

        if (diagImbalanceVal !== null && diagImbalanceVal < 0) {
            showErrorAlert('El umbral de desbalance no puede ser negativo');
            return;
        }
        
        // Validaciones adicionales
        if (limInfCaudalMasico < 0 || limSupCaudalMasico < 0 || volMasicoIniBatch < 0 || timeFinishedBatch < 0.1) {
            showErrorAlert('Los valores de configuración no pueden ser negativos y el tiempo de cierre debe ser mayor a 0.1 minutos');
            return;
        }
        
        if (limInfCaudalMasico >= limSupCaudalMasico) {
            showErrorAlert('Error: El límite inferior debe ser menor que el límite superior');
            return;
        }

        const coeficientes = {
            mt: mt,
            bt: bt,
            mp: mp,
            bp: bp,
            lim_inf_caudal_masico: limInfCaudalMasico,
            lim_sup_caudal_masico: limSupCaudalMasico,
            vol_masico_ini_batch: volMasicoIniBatch,
            time_finished_batch: timeFinishedBatch,
            // Campos incertidumbre (sin densidad manual)
            mf: mfVal,
            vis: visVal,
            deltavis: deltavisVal,
            dn: dnVal,
            ucal_dens: ucalDensVal,
            kcal_dens: kcalDensVal,
            tipdens: tipdensVal,
            desv_dens: desvDensVal,
            ucal_met: ucalMetVal,
            kcal_met: kcalMetVal,
            esis_met: esisMetVal,
            ucarta_met: ucartaMetVal,
            zero_stab: zeroStabVal,
            diagnostic_glp_density_ref: diagGlpRefVal,
            diagnostic_glp_density_tolerance_pct: diagGlpToleranceVal,
            diagnostic_driver_amp_base: diagDriverAmpBaseVal,
            diagnostic_driver_amp_multiplier: diagDriverAmpMultiplierVal,
            diagnostic_n1_threshold: diagN1Val,
            diagnostic_n2_threshold: diagN2Val,
            diagnostic_amp_imbalance_threshold_pct: diagImbalanceVal
        };

        //console.log('Actualizando coeficientes:', coeficientes);

        // Mostrar indicador de carga
        btnActualizar.disabled = true;
        btnActualizar.innerHTML = '<i class="bi bi-hourglass-split"></i> Guardando...';

        // Llamada al backend para guardar los coeficientes
        fetch(`/monitoreo/api/configuracion/actualizar/${sistemaId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify(coeficientes)
        })
        .then(async response => {
            // Verificar si hay error de permisos
            if (response.status === 403) {
                const data = await response.json();
                const errorMsg = data.error || 'No tiene permisos para esta acción. Contacte al administrador.';
                const permissionError = new Error(errorMsg);
                permissionError.isPermissionError = true;
                throw permissionError;
            }
            
            // Manejar otros errores HTTP (incluyendo 400)
            if (!response.ok) {
                const data = await response.json();
                // Extraer el mensaje personalizado del backend
                const errorMsg = data.error || data.message || `Error ${response.status}: ${response.statusText}`;
                throw new Error(errorMsg);
            }
            
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Mostrar mensaje de éxito con SweetAlert2
                showSuccessAlert(data.message || 'Coeficientes actualizados correctamente');
                // Cerrar modal
                bootstrap.Modal.getInstance(modal).hide();
            } else {
                showErrorAlert('Error al actualizar coeficientes: ' + (data.error || 'Error desconocido'));
            }
        })
        .catch(error => {
            //console.error('Error:', error);
            // Verificar si es error de permisos
            if (error.isPermissionError || error.message.includes('permisos') || error.message.includes('administrador')) {
                showPermissionDeniedAlert(error.message);
            } else {
                showErrorAlert(error.message || 'Error de conexión al actualizar coeficientes');
            }
        })
        .finally(() => {
            // Restaurar botón
            btnActualizar.disabled = false;
            btnActualizar.innerHTML = '<i class="bi bi-check-circle"></i> Actualizar';
        });
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

    function aplicarModoSoloLectura() {
        // Obtener todos los campos del formulario
        const formElements = form.querySelectorAll('input, select, textarea');
        
        formElements.forEach(element => {
            // Hacer los campos de solo lectura
            element.setAttribute('readonly', 'readonly');
            element.style.backgroundColor = '#f8f9fa';
            element.style.cursor = 'not-allowed';
            
            // Agregar tooltip explicativo
            element.setAttribute('title', 'Solo lectura - Supervisor no puede modificar configuraciones');
        });

        // Deshabilitar también cualquier botón dentro del formulario
        const formButtons = form.querySelectorAll('button[type="button"]:not(.btn-close)');
        formButtons.forEach(button => {
            button.disabled = true;
            button.style.cursor = 'not-allowed';
        });
        
        //console.log('✅ Modo solo lectura aplicado para rol Supervisor');
    }
});