// events.js - Eventos específicos de tipo criticidad
import { TipoCriticidadService, CriticidadService } from '../../../../static/js/global/api/index.js';
import { UI } from '../../../../static/js/global/utils/ui.js';

let currentPage = 1;
const DEFAULT_PER_PAGE = 10;

// Función para actualizar la tabla de tipos de criticidad con agrupación
function actualizarTablaTipoCriticidades(data) {
    const tbody = document.getElementById('tipcritTableBody');
    if (!tbody) return;

    tbody.innerHTML = '';
    
    if (!data || data.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="4" class="text-center">No hay tipos de criticidad registrados</td>
            </tr>`;
        return;
    }

    // Agrupar datos por tipo_criticidad_id
    const groupedData = {};
    data.forEach(item => {
        if (!groupedData[item.tipo_criticidad_id]) {
            groupedData[item.tipo_criticidad_id] = {
                tipo_criticidad_name: item.tipo_criticidad_name,
                total_relations: item.total_relations,
                relations: []
            };
        }
        groupedData[item.tipo_criticidad_id].relations.push(item);
    });

    // Renderizar filas agrupadas
    Object.values(groupedData).forEach((tipoGroup, groupIndex) => {
        const firstRelation = tipoGroup.relations[0];
        const hasMultipleRelations = tipoGroup.total_relations > 1;
        const groupClass = groupIndex % 2 === 0 ? 'group-odd' : 'group-even';
        
        // Crear la primera fila con el nombre del tipo
        const firstRow = document.createElement('tr');
        firstRow.className = `${groupClass} ${hasMultipleRelations ? 'group-start' : ''}`;
        firstRow.innerHTML = `
            <td class="align-middle name-cell" ${hasMultipleRelations ? `rowspan="${tipoGroup.relations.length}"` : ''}>
                <div class="name-container">
                    <span class="name-text">${UI.utils.escapeHtml(tipoGroup.tipo_criticidad_2name)}</span>
                    <br><span class="badge bg-info mt-1" title="Este tipo tiene ${tipoGroup.total_relations} ${tipoGroup.total_relations === 1 ? 'relación' : 'relaciones'}">${tipoGroup.total_relations} ${tipoGroup.total_relations === 1 ? 'relación' : 'relaciones'}</span>
                </div>
            </td>
            <td class="relation-cell">${UI.utils.escapeHtml(firstRelation.criticidad_name)}</td>
            <td class="relation-cell">${UI.utils.formatDate(firstRelation.created_at)}</td>
            <td class="text-center action-cell">
                <div class="btn-group" role="group">
                    <button class="btn btn-primary btn-sm me-1" 
                        data-id="${firstRelation.id}"
                        data-tipo-name="${UI.utils.escapeHtml(tipoGroup.tipo_criticidad_name)}"
                        data-criticidad-id="${String(firstRelation.criticidad_id || firstRelation.criticidad)}"
                        onclick="openEditModal(this.dataset.id, this.dataset.tipoName, this.dataset.criticidadId)"
                        title="Editar esta relación">
                        <i class="bi bi-pencil-square"></i>
                    </button>
                    <button class="btn btn-danger btn-sm" 
                        onclick="deleteTipoCriticidad('${firstRelation.tipo_criticidad_id}', '${UI.utils.escapeHtml(tipoGroup.tipo_criticidad_name)}', '${firstRelation.id}')"
                        title="${hasMultipleRelations ? 'Eliminar esta relación' : 'Eliminar tipo de criticidad'}">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(firstRow);

        // Crear filas adicionales para las demás relaciones
        for (let i = 1; i < tipoGroup.relations.length; i++) {
            const relation = tipoGroup.relations[i];
            const additionalRow = document.createElement('tr');
            additionalRow.className = `${groupClass} group-continuation`;
            additionalRow.innerHTML = `
                <td class="relation-cell">${UI.utils.escapeHtml(relation.criticidad_name)}</td>
                <td class="relation-cell">${UI.utils.formatDate(relation.created_at)}</td>
                <td class="text-center action-cell">
                    <div class="btn-group" role="group">
                        <button class="btn btn-primary btn-sm me-1" 
                            data-id="${relation.id}"
                            data-tipo-name="${UI.utils.escapeHtml(tipoGroup.tipo_criticidad_name)}"
                            data-criticidad-id="${String(relation.criticidad_id || relation.criticidad)}"
                            onclick="openEditModal(this.dataset.id, this.dataset.tipoName, this.dataset.criticidadId)"
                            title="Editar esta relación">
                            <i class="bi bi-pencil-square"></i>
                        </button>
                        <button class="btn btn-danger btn-sm" 
                            onclick="deleteTipoCriticidad('${relation.tipo_criticidad_id}', '${UI.utils.escapeHtml(tipoGroup.tipo_criticidad_name)}', '${relation.id}')"
                            title="Eliminar esta relación">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </td>
            `;
            tbody.appendChild(additionalRow);
        }
    });
    
    // Agregar efecto hover para grupos completos
    addGroupHoverEffect();
}

// Función para agregar efecto hover a grupos
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

// Continuar con el resto del código existente...
// [Aquí iría el resto del código original]
