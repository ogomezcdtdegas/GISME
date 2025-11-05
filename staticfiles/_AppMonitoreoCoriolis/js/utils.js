// ====================================================================
// UTILS.JS - Funciones utilitarias
// ====================================================================

// Función utilitaria para formatear fechas para Django API
function formatearFechaParaAPI(fechaInput) {
    if (!fechaInput) return null;
    
    // Si es un objeto Date
    if (fechaInput instanceof Date) {
        // Obtener componentes de fecha en UTC
        const year = fechaInput.getFullYear();
        const month = String(fechaInput.getMonth() + 1).padStart(2, '0');
        const day = String(fechaInput.getDate()).padStart(2, '0');
        const hours = String(fechaInput.getHours()).padStart(2, '0');
        const minutes = String(fechaInput.getMinutes()).padStart(2, '0');
        const seconds = String(fechaInput.getSeconds()).padStart(2, '0');
        
        return `${year}-${month}-${day}T${hours}:${minutes}:${seconds}`;
    }
    
    // Si viene de datetime-local (formato: "2024-09-24T14:30")
    if (typeof fechaInput === 'string' && fechaInput.includes('T') && fechaInput.length === 16) {
        return fechaInput + ':00'; // Agregar segundos
    }
    
    // Si ya tiene formato completo, devolverlo tal como está
    return fechaInput;
}

// Función para obtener el sistema actual (prioridad: contexto Django > URL)
function obtenerSistemaActual() {
    // 1. Primero intentar obtener del contexto de Django
    if (typeof SISTEMA_ACTUAL !== 'undefined' && SISTEMA_ACTUAL && SISTEMA_ACTUAL.id) {
        return SISTEMA_ACTUAL.id;
    }
    
    // 2. Fallback: intentar extraer de la URL
    const url = window.location.pathname;
    const match = url.match(/\/sistema\/([a-f0-9-]{36})\//);
    if (match) {
        return match[1];
    }
    
    //console.warn('⚠️ No se pudo obtener ID del sistema desde contexto Django ni URL');
    return null;
}