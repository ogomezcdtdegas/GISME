// Ejecutar en la consola del navegador para verificar el comportamiento del badge

console.log('🔍 Verificando comportamiento del badge...');

// Obtener todos los badges en la tabla
const badges = document.querySelectorAll('.grouped-table .badge');
console.log(`📊 Total de badges encontrados: ${badges.length}`);

// Obtener todas las filas con rowspan (productos con múltiples combinaciones)
const rowspanCells = document.querySelectorAll('.grouped-table td[rowspan]');
console.log(`📊 Total de productos con rowspan: ${rowspanCells.length}`);

// Verificar productos individuales
const allProductCells = document.querySelectorAll('.grouped-table .product-name-cell');
console.log(`📊 Total de productos: ${allProductCells.length}`);

allProductCells.forEach((cell, index) => {
    const productName = cell.querySelector('.product-name')?.textContent || 'Sin nombre';
    const badge = cell.querySelector('.badge');
    const rowspan = cell.getAttribute('rowspan');
    
    if (badge) {
        console.log(`✅ ${productName}: TIENE badge (${badge.textContent}) - rowspan: ${rowspan || 'no'}`);
    } else {
        console.log(`❌ ${productName}: NO tiene badge - rowspan: ${rowspan || 'no'}`);
    }
});

console.log('\n💡 Resultado esperado:');
console.log('   - Productos con 1 sola combinación: NO deben tener badge');
console.log('   - Productos con múltiples combinaciones: SÍ deben tener badge');
