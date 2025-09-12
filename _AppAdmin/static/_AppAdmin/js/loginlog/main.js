/**
 * Punto de entrada principal para Login Logs
 * Inicialización y configuración de eventos
 */

import { loadLoginLogs, setupSearch, setupPagination } from './events.js';

/**
 * Inicializar la aplicación de Login Logs
 */
function initializeLoginLogs() {
    // Configurar eventos
    setupSearch();
    setupPagination();
    
    // Cargar datos iniciales
    loadLoginLogs();
    
    console.log('✅ Login Logs initialized');
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', initializeLoginLogs);