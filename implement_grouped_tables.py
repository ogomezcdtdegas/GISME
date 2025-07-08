"""
Script para implementar agrupación visual en todas las tablas de complementos
"""

import os
import shutil

# Definir las configuraciones para cada sección
SECTIONS = {
    'tipoCriticidad': {
        'folder': 'static_tipoCriticidad',
        'group_by': 'tipo_criticidad_id',
        'group_name': 'tipo_criticidad_name',
        'main_column': 'Tipo de Criticidad',
        'related_columns': ['Criticidad', 'Fecha']
    },
    'tipoEquipo': {
        'folder': 'static_tipoEquipo',
        'group_by': 'tipo_equipo_id',
        'group_name': 'tipo_equipo_name',
        'main_column': 'Tipo de Equipo',
        'related_columns': ['Producto', 'Tipo Criticidad', 'Criticidad']
    },
    'tecnologia': {
        'folder': 'static_tecnologia',
        'group_by': 'tecnologia_id',
        'group_name': 'tecnologia_name',
        'main_column': 'Tecnología',
        'related_columns': ['Tipo Equipo', 'Producto', 'Criticidad']
    }
}

def create_grouped_css():
    """Crear CSS común para todas las tablas agrupadas"""
    css_content = """/* CSS común para todas las tablas agrupadas */
.grouped-table {
    border-collapse: separate;
    border-spacing: 0;
}

/* Remover el patrón de rayas por defecto de Bootstrap */
.grouped-table tbody tr {
    background-color: transparent !important;
    transition: all 0.2s ease;
}

/* Celdas de nombres principales */
.grouped-table .name-cell {
    vertical-align: middle !important;
    font-weight: 600 !important;
    position: relative;
}

.grouped-table .name-container {
    padding: 0.5rem;
}

.grouped-table .name-text {
    display: block;
    font-size: 1rem;
    color: #212529;
}

/* Celdas de relaciones */
.grouped-table .relation-cell {
    padding: 0.75rem;
    vertical-align: middle;
}

/* Grupos impares (gris) */
.grouped-table .group-odd {
    background-color: #f8f9fa !important;
}

.grouped-table .group-odd .name-cell {
    background-color: #f8f9fa !important;
}

.grouped-table .group-odd .relation-cell {
    background-color: #f8f9fa !important;
}

.grouped-table .group-odd .action-cell {
    background-color: #f8f9ห !important;
}

/* Grupos pares (blanco) */
.grouped-table .group-even {
    background-color: #ffffff !important;
}

.grouped-table .group-even .name-cell {
    background-color: #ffffff !important;
}

.grouped-table .group-even .relation-cell {
    background-color: #ffffff !important;
}

.grouped-table .group-even .action-cell {
    background-color: #ffffff !important;
}

/* Efectos hover para grupos completos */
.grouped-table tbody tr:hover {
    background-color: #e3f2fd !important;
}

.grouped-table tbody tr:hover .name-cell {
    background-color: #bbdefb !important;
}

.grouped-table tbody tr:hover .relation-cell {
    background-color: #e3f2fd !important;
}

.grouped-table tbody tr:hover .action-cell {
    background-color: #e3f2fd !important;
}

.grouped-table tbody tr.table-active {
    background-color: #e3f2fd !important;
}

.grouped-table tbody tr.table-active .name-cell {
    background-color: #bbdefb !important;
}

.grouped-table tbody tr.table-active .relation-cell {
    background-color: #e3f2fd !important;
}

.grouped-table tbody tr.table-active .action-cell {
    background-color: #e3f2fd !important;
}

/* Estilos para badges */
.grouped-table .badge {
    font-size: 0.75em;
    display: inline-block;
    margin-top: 4px;
    font-weight: normal;
}

/* Separación visual entre grupos */
.grouped-table .group-start {
    border-top: 2px solid #dee2e6;
}

/* Eliminar separación del primer grupo */
.grouped-table tbody tr:first-child {
    border-top: none !important;
}

/* Espaciado de botones */
.grouped-table .btn-group {
    gap: 0.25rem;
}

/* Responsive */
@media (max-width: 768px) {
    .grouped-table {
        font-size: 0.875rem;
    }
    
    .grouped-table .btn-sm {
        padding: 0.125rem 0.375rem;
        font-size: 0.75rem;
    }
    
    .grouped-table .name-text {
        font-size: 0.875rem;
    }
}"""

    # Crear el archivo CSS común
    os.makedirs('static/css/common', exist_ok=True)
    with open('static/css/common/grouped-table.css', 'w', encoding='utf-8') as f:
        f.write(css_content)
    
    print("✅ CSS común creado en static/css/common/grouped-table.css")

def create_grouped_js_function():
    """Crear función JavaScript común para agrupación"""
    js_content = """
// Función común para agrupar y renderizar tablas
function renderGroupedTable(data, config) {
    const tbody = document.getElementById(config.tableId);
    if (!tbody) return;

    tbody.innerHTML = '';
    
    if (!data || data.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="${config.columnCount}" class="text-center">No hay registros</td>
            </tr>`;
        return;
    }

    // Agrupar datos
    const groupedData = {};
    data.forEach(item => {
        const groupKey = item[config.groupBy];
        if (!groupedData[groupKey]) {
            groupedData[groupKey] = {
                groupName: item[config.groupName],
                totalRelations: item.total_relations,
                relations: []
            };
        }
        groupedData[groupKey].relations.push(item);
    });

    // Renderizar filas agrupadas
    Object.values(groupedData).forEach((group, groupIndex) => {
        const firstRelation = group.relations[0];
        const hasMultipleRelations = group.totalRelations > 1;
        const groupClass = groupIndex % 2 === 0 ? 'group-odd' : 'group-even';
        
        // Crear la primera fila con el nombre del grupo
        const firstRow = document.createElement('tr');
        firstRow.className = `${groupClass} ${hasMultipleRelations ? 'group-start' : ''}`;
        
        // Construir HTML de la primera fila
        let firstRowHTML = `
            <td class="align-middle name-cell" ${hasMultipleRelations ? `rowspan="${group.relations.length}"` : ''}>
                <div class="name-container">
                    <span class="name-text">${UI.utils.escapeHtml(group.groupName)}</span>
                    <br><span class="badge bg-info mt-1" title="Tiene ${group.totalRelations} ${group.totalRelations === 1 ? 'relación' : 'relaciones'}">${group.totalRelations} ${group.totalRelations === 1 ? 'relación' : 'relaciones'}</span>
                </div>
            </td>`;
        
        // Añadir celdas relacionadas
        config.relationCells.forEach(cellConfig => {
            const value = cellConfig.format ? cellConfig.format(firstRelation) : firstRelation[cellConfig.field];
            firstRowHTML += `<td class="relation-cell">${value}</td>`;
        });
        
        // Añadir botones de acción
        firstRowHTML += `
            <td class="text-center action-cell">
                <div class="btn-group" role="group">
                    ${config.actionButtons(firstRelation, group.groupName, hasMultipleRelations)}
                </div>
            </td>`;
        
        firstRow.innerHTML = firstRowHTML;
        tbody.appendChild(firstRow);

        // Crear filas adicionales para las demás relaciones
        for (let i = 1; i < group.relations.length; i++) {
            const relation = group.relations[i];
            const additionalRow = document.createElement('tr');
            additionalRow.className = `${groupClass} group-continuation`;
            
            let additionalRowHTML = '';
            
            // Añadir celdas relacionadas
            config.relationCells.forEach(cellConfig => {
                const value = cellConfig.format ? cellConfig.format(relation) : relation[cellConfig.field];
                additionalRowHTML += `<td class="relation-cell">${value}</td>`;
            });
            
            // Añadir botones de acción
            additionalRowHTML += `
                <td class="text-center action-cell">
                    <div class="btn-group" role="group">
                        ${config.actionButtons(relation, group.groupName, true)}
                    </div>
                </td>`;
            
            additionalRow.innerHTML = additionalRowHTML;
            tbody.appendChild(additionalRow);
        }
    });
    
    // Agregar efecto hover para grupos completos
    addGroupHoverEffect();
}

// Función común para efecto hover
function addGroupHoverEffect() {
    const tables = document.querySelectorAll('.grouped-table');
    tables.forEach(table => {
        const rows = table.querySelectorAll('tbody tr');
        
        rows.forEach((row, index) => {
            row.addEventListener('mouseenter', function() {
                // Limpiar highlights previos
                rows.forEach(r => r.classList.remove('table-active'));
                
                // Si la fila tiene rowspan (es el inicio de un grupo)
                const groupedCell = this.querySelector('.name-cell[rowspan]');
                if (groupedCell) {
                    const rowspan = parseInt(groupedCell.getAttribute('rowspan'));
                    // Destacar todas las filas del grupo
                    for (let i = 0; i < rowspan; i++) {
                        const targetRow = rows[index + i];
                        if (targetRow) {
                            targetRow.classList.add('table-active');
                        }
                    }
                } else {
                    // Si es una fila de continuación, buscar el grupo completo
                    const allRows = Array.from(rows);
                    const currentIndex = allRows.indexOf(this);
                    
                    // Buscar hacia atrás la fila con rowspan
                    for (let i = currentIndex - 1; i >= 0; i--) {
                        const possibleGroupRow = allRows[i];
                        const groupCell = possibleGroupRow.querySelector('.name-cell[rowspan]');
                        if (groupCell) {
                            const rowspan = parseInt(groupCell.getAttribute('rowspan'));
                            const groupStartIndex = i;
                            const groupEndIndex = groupStartIndex + rowspan - 1;
                            
                            if (currentIndex <= groupEndIndex) {
                                // Destacar todo el grupo
                                for (let j = groupStartIndex; j <= groupEndIndex; j++) {
                                    if (allRows[j]) {
                                        allRows[j].classList.add('table-active');
                                    }
                                }
                            }
                            break;
                        }
                    }
                }
            });
            
            row.addEventListener('mouseleave', function() {
                // Remover highlight después de un pequeño delay
                setTimeout(() => {
                    if (!table.querySelector('tbody tr:hover')) {
                        rows.forEach(r => r.classList.remove('table-active'));
                    }
                }, 100);
            });
        });
    });
}
"""
    
    # Crear el archivo JS común
    os.makedirs('static/js/common', exist_ok=True)
    with open('static/js/common/grouped-table.js', 'i', encoding='utf-8') as f:
        f.write(js_content)
    
    print("✅ JavaScript común creado en static/js/common/grouped-table.js")

if __name__ == "__main__":
    print("🔧 Implementando agrupación visual en todas las tablas...")
    
    # Crear archivos comunes
    create_grouped_css()
    create_grouped_js_function()
    
    print("\n✅ Implementación completada!")
    print("📝 Próximos pasos:")
    print("1. Actualizar cada archivo de eventos para usar la función común")
    print("2. Agregar el CSS común a cada template")
    print("3. Eliminar la clase 'table-striped' de los templates")
    print("4. Probar en cada sección")
