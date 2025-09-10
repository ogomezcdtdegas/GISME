// _AppAdmin/js/main.js - Inicialización principal
document.addEventListener("DOMContentLoaded", function() {
    // Verificar que todos los módulos estén disponibles
    if (typeof window.AdminUI !== 'undefined' && 
        typeof window.AdminAPI !== 'undefined' && 
        typeof window.AdminEvents !== 'undefined') {
        
        // Inicializar UI primero
        window.AdminUI.init();
        
        // Luego eventos
        window.AdminEvents.init();
        
        console.log('Módulo AdminMain inicializado correctamente');
    } else {
        console.error('Error: No se pudieron cargar todos los módulos necesarios');
    }
});