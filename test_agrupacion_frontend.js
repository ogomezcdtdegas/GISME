// Script de prueba para verificar la funcionalidad de agrupación
// Ejecutar este script en la consola del navegador en la página de productos

console.log('🧪 Iniciando prueba de agrupación de productos...');

// Verificar que la tabla existe
const table = document.querySelector('.grouped-table');
if (!table) {
    console.error('❌ No se encontró la tabla con clase .grouped-table');
} else {
    console.log('✅ Tabla encontrada');
}

// Verificar filas con rowspan (productos agrupados)
const rowspanCells = table.querySelectorAll('td[rowspan]');
console.log(`📊 Productos con múltiples combinaciones: ${rowspanCells.length}`);

rowspanCells.forEach((cell, index) => {
    const rowspan = parseInt(cell.getAttribute('rowspan'));
    const productName = cell.querySelector('.product-name')?.textContent || cell.textContent.split('\n')[0];
    console.log(`   ${index + 1}. ${productName.trim()}: ${rowspan} combinaciones`);
});

// Verificar efectos hover
console.log('🎨 Verificando efectos hover...');
const firstGroupRow = table.querySelector('tbody tr');
if (firstGroupRow) {
    // Simular hover
    firstGroupRow.dispatchEvent(new Event('mouseenter'));
    
    setTimeout(() => {
        const activeRows = table.querySelectorAll('tbody tr.table-active');
        console.log(`   Filas destacadas en hover: ${activeRows.length}`);
        
        // Quitar hover
        firstGroupRow.dispatchEvent(new Event('mouseleave'));
        
        setTimeout(() => {
            const activeRowsAfter = table.querySelectorAll('tbody tr.table-active');
            console.log(`   Filas destacadas después del hover: ${activeRowsAfter.length}`);
        }, 200);
    }, 100);
}

// Verificar estructura de datos
console.log('📋 Verificando estructura de datos...');
fetch('/complementos/productos/?format=json&per_page=100')
    .then(response => response.json())
    .then(data => {
        console.log(`   Total de registros: ${data.results.length}`);
        
        // Agrupar datos por producto_id
        const grouped = {};
        data.results.forEach(item => {
            if (!grouped[item.producto_id]) {
                grouped[item.producto_id] = {
                    name: item.producto_name,
                    combinations: []
                };
            }
            grouped[item.producto_id].combinations.push({
                tipo: item.tipo_criticidad_name,
                criticidad: item.criticidad_name
            });
        });
        
        console.log('   Agrupación por productos:');
        Object.values(grouped).forEach(product => {
            console.log(`     • ${product.name}: ${product.combinations.length} combinación${product.combinations.length > 1 ? 'es' : ''}`);
            product.combinations.forEach(combo => {
                console.log(`       - ${combo.tipo} / ${combo.criticidad}`);
            });
        });
        
        console.log('✅ ¡Prueba de agrupación completada!');
    })
    .catch(error => {
        console.error('❌ Error al obtener datos:', error);
    });

// Verificar CSS aplicado
console.log('🎨 Verificando estilos CSS...');
const groupedTableCSS = document.querySelector('link[href*="grouped-table.css"]');
if (groupedTableCSS) {
    console.log('✅ CSS de tabla agrupada cargado');
} else {
    console.log('⚠️  CSS de tabla agrupada no encontrado');
}

console.log('🏁 Prueba iniciada. Revisa los resultados arriba.');
