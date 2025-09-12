// _AppAdmin/js/main.js - Inicialización principal (sin módulos ES6)

// AdminMain - Inicialización principal
window.AdminMain = {
    
    // Función de inicialización
    init() {
        console.log('🟢 Inicializando AdminMain...');
        
        // Verificar que todos los módulos estén disponibles
        if (typeof window.AdminAPI !== 'undefined' && 
            typeof window.AdminUI !== 'undefined' && 
            typeof window.AdminEvents !== 'undefined') {
            
            console.log('✅ Todos los módulos están disponibles');
            
            // Cargar usuarios inicialmente
            window.AdminEvents.loadUsers(1);
            
        } else {
            console.error('❌ No se pudieron cargar todos los módulos necesarios');
            console.log('AdminAPI:', typeof window.AdminAPI);
            console.log('AdminUI:', typeof window.AdminUI);
            console.log('AdminEvents:', typeof window.AdminEvents);
        }
    }
};

// Inicialización cuando se carga el DOM
document.addEventListener("DOMContentLoaded", function() {
    console.log('🟢 DOM cargado, iniciando AdminMain...');
    window.AdminMain.init();
});