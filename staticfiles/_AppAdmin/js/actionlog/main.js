/**
 * Punto de entrada principal para Action Logs
 * Inicialización y configuración de eventos
 */

import { loadActionLogs, setupSearch, setupFilters, setupPagination } from './events.js';

/**
 * Inicializar la aplicación de Action Logs
 */
function initializeActionLogs() {
    // Configurar eventos
    setupSearch();
    setupFilters(); // Reactivado para filtros específicos
    setupPagination();
    
    // Cargar datos iniciales
    loadActionLogs();
    
    console.log('✅ Action Logs initialized');
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', initializeActionLogs);