# VALIDACIÓN FRONTEND TECNOLOGÍA - CHECKLIST COMPLETO

## 🎯 OBJETIVO
Validar que la funcionalidad frontend de Tecnología funcione correctamente con:
- Agrupación visual y badges
- Eliminación en cascada con opciones apropiadas
- Mensajes de advertencia claros
- Actualización correcta de la tabla

## 📋 DATOS DE PRUEBA DISPONIBLES

### Tecnologías creadas:
1. **TechTest Eliminable** - 1 relación
   - Tipo: Única relación
   - Esperado: Modal de confirmación simple
   - Comportamiento: Eliminación completa automática

2. **TechTest Compartida** - 2 relaciones
   - Tipo: Múltiples relaciones
   - Esperado: Modal con opciones
   - Comportamiento: Elegir entre eliminar relación o tecnología completa

3. **TechTest Permanente** - 2 relaciones
   - Tipo: Múltiples relaciones
   - Esperado: Modal con opciones
   - Comportamiento: Elegir entre eliminar relación o tecnología completa

## ✅ CHECKLIST DE VALIDACIÓN

### 1. AGRUPACIÓN VISUAL
- [ ] **Agrupación por rowspan**: Cada tecnología debe aparecer agrupada con su nombre en una celda con rowspan
- [ ] **Badges correctos**: 
  - TechTest Eliminable: "1 combinación"
  - TechTest Compartida: "2 combinaciones"
  - TechTest Permanente: "2 combinaciones"
- [ ] **Alternancia de colores**: Grupos alternos deben tener colores diferentes (gris/blanco)
- [ ] **Efecto hover**: Al pasar el mouse sobre una fila, todo el grupo debe resaltarse

### 2. BOTONES DE ELIMINACIÓN
- [ ] **Presencia**: Cada fila debe tener un botón de eliminar rojo
- [ ] **Parámetros correctos**: Los botones deben pasar relacionId, tecnologiaId, y tecnologiaName correctamente

### 3. TECNOLOGÍA CON ÚNICA RELACIÓN (TechTest Eliminable)
- [ ] **Modal de confirmación**: Debe aparecer un modal de confirmación simple
- [ ] **Título**: "¿Está seguro?"
- [ ] **Mensaje**: "Esta es la última relación de la tecnología 'TechTest Eliminable'"
- [ ] **Advertencia**: "La tecnología será eliminada completamente"
- [ ] **Información**: "La tecnología es el último nivel de la jerarquía, por lo que no hay elementos dependientes que se eliminen en cascada"
- [ ] **Botones**: "Sí, eliminar" y "Cancelar"

### 4. TECNOLOGÍA CON MÚLTIPLES RELACIONES (TechTest Compartida/Permanente)
- [ ] **Modal con opciones**: Debe aparecer un modal con opciones de radio
- [ ] **Título**: "¿Qué desea eliminar?"
- [ ] **Contador**: Debe mostrar el número correcto de relaciones (2 en este caso)
- [ ] **Opción 1**: "Solo eliminar esta relación" (marcada por defecto)
- [ ] **Opción 2**: "Eliminar la tecnología y todas sus relaciones"
- [ ] **Información**: "La tecnología es el último nivel de la jerarquía, por lo que no hay elementos dependientes que se eliminen en cascada"
- [ ] **Botones**: "Eliminar" y "Cancelar"

### 5. ELIMINACIÓN DE RELACIÓN ÚNICA
**Pasos:**
1. Hacer clic en eliminar en TechTest Eliminable
2. Confirmar eliminación
3. Verificar que:
   - [ ] La tecnología desaparezca completamente de la tabla
   - [ ] Aparezca mensaje de éxito
   - [ ] La tabla se actualice automáticamente

### 6. ELIMINACIÓN DE RELACIÓN INDIVIDUAL
**Pasos:**
1. Hacer clic en eliminar en una fila de TechTest Compartida
2. Seleccionar "Solo eliminar esta relación"
3. Confirmar eliminación
4. Verificar que:
   - [ ] Solo esa fila desaparezca
   - [ ] La tecnología siga existiendo con una relación menos
   - [ ] El badge se actualice (de "2 combinaciones" a "1 combinación")
   - [ ] Aparezca mensaje de éxito

### 7. ELIMINACIÓN DE TECNOLOGÍA COMPLETA
**Pasos:**
1. Hacer clic en eliminar en una fila de TechTest Permanente
2. Seleccionar "Eliminar la tecnología y todas sus relaciones"
3. Confirmar eliminación
4. Verificar que:
   - [ ] Toda la tecnología desaparezca (todas las filas del grupo)
   - [ ] Aparezca mensaje de éxito
   - [ ] La tabla se actualice automáticamente

### 8. CANCELAR ELIMINACIÓN
**Pasos:**
1. Hacer clic en eliminar en cualquier fila
2. Hacer clic en "Cancelar"
3. Verificar que:
   - [ ] El modal se cierre
   - [ ] No se elimine nada
   - [ ] La tabla permanezca igual

### 9. MENSAJES DE RESPUESTA
- [ ] **Éxito**: Los mensajes de éxito deben ser claros y específicos
- [ ] **Error**: Si hay errores, deben mostrarse apropiadamente
- [ ] **Posición**: Los mensajes deben aparecer en una posición visible

### 10. ACTUALIZACIÓN DE TABLA
- [ ] **Automática**: La tabla debe actualizarse automáticamente tras eliminaciones
- [ ] **Consistente**: Los datos mostrados deben ser consistentes con el backend
- [ ] **Agrupación**: La agrupación debe mantenerse correcta tras cambios

## 🧪 CASOS DE PRUEBA ESPECÍFICOS

### Caso 1: Eliminación secuencial
1. Eliminar una relación de TechTest Compartida → Verificar que quede 1 relación
2. Eliminar la última relación → Verificar que aparezca modal de confirmación simple
3. Confirmar → Verificar que la tecnología desaparezca completamente

### Caso 2: Eliminación completa vs individual
1. Usar TechTest Permanente para probar ambas opciones
2. Primero eliminar solo una relación
3. Luego eliminar la tecnología completa
4. Verificar comportamientos diferenciados

### Caso 3: Validación de interfaz
1. Verificar que todos los elementos visuales funcionen correctamente
2. Probar hover effects
3. Verificar alternancia de colores
4. Comprobar badges y agrupación

## 📝 NOTAS IMPORTANTES

1. **Nivel de jerarquía**: Tecnología es el último nivel, por lo que no debe haber cascada hacia niveles inferiores
2. **Mensajes claros**: Los mensajes deben ser específicos y comprensibles
3. **Opciones apropiadas**: Las opciones deben aparecer según el número de relaciones
4. **Actualización automática**: La tabla debe actualizarse sin necesidad de recargar la página

## 🎉 CRITERIOS DE ÉXITO

La validación será exitosa cuando:
- [x] Todos los elementos visuales funcionen correctamente
- [x] Los modales aparezcan con las opciones apropiadas
- [x] Las eliminaciones se ejecuten correctamente
- [x] La tabla se actualice automáticamente
- [x] Los mensajes sean claros y precisos
- [x] No haya errores en la consola del navegador

## 📍 URL DE VALIDACIÓN
**http://127.0.0.1:8000/complementos/tecnologias/**

---

*Este checklist debe completarse manualmente en el navegador para validar la funcionalidad frontend de Tecnología.*
