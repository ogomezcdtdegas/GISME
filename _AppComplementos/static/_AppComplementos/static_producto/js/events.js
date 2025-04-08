// events.js - Eventos y listeners
document.addEventListener("DOMContentLoaded", function () {
    console.log("🟢 Página cargada - Inicializando...");
    loadProductosPag(); // Cargar equipos al iniciar

    document.getElementById('recordsPerPage').addEventListener('change', function() {
        loadProductosPag();
    });

    document.getElementById('prodForm').addEventListener('submit', async function(event) {
        event.preventDefault();
        
        const name = document.getElementById('name').value;
        const tipoId = document.getElementById('tipocriticidadDropdown').value;
        const critId = document.getElementById('criticidadDropdown').value;
        
        if (!name || !tipoId || !critId) {
            alert("❌ Complete todos los campos obligatorios.");
            return;
        }
        
        const data = await crearProductoCompleto(name, tipoId, critId);
        
        if (data.success) {
            alert("✅ Producto creado correctamente");
            loadProductosPag();
            document.getElementById('prodForm').reset();
            document.getElementById('criticidadDropdown').disabled = true;
            document.getElementById('criticidadDropdown').innerHTML = '<option value="">Seleccione un tipo primero</option>';
        } else {
            alert("⚠️ " + (data.error || "Error al crear el producto"));
        }
    });

    document.getElementById("editprodForm").addEventListener("submit", async function(event) {
        event.preventDefault();
    
        const id = document.getElementById("edittipCritId").value;
        const name = document.getElementById("editName").value;
        const tipoCriticidadId = document.getElementById("edittipCritTipoId").value;
        const criticidadId = document.getElementById("editCriticidad").value;
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
        console.log("📡 Datos para actualizar:", { id, name, tipoCriticidadId, criticidadId });
    
        const data = await actualizarTipCriticidad(id, name, tipoCriticidadId, criticidadId, csrftoken);
        
        if (data.success) {
            alert("✅ Registro actualizado correctamente");
            location.reload();
        } else {
            alert("❌ Error al actualizar: " + data.error);
        }
    });    
});
