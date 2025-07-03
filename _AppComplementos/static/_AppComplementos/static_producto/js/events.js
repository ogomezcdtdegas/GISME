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
        
        const id = document.getElementById("editprodId").value;
        const name = document.getElementById("editprodName").value;
        const tipoCriticidadId = document.getElementById("editTipoCriticidad").value;
        const criticidadId = document.getElementById("editCriticidad").value;
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        if (!name || !tipoCriticidadId || !criticidadId) {
            alert("❌ Complete todos los campos obligatorios.");
            return;
        }
        
        try {
            const response = await fetch(`/complementos/editar-producto/${id}/`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrftoken,
                    "X-Requested-With": "XMLHttpRequest"
                },
                body: JSON.stringify({ 
                    name, 
                    tipo_criticidad_id: tipoCriticidadId,
                    criticidad_id: criticidadId 
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                alert(data.message || "✅ Producto actualizado correctamente");
                loadProductosPag();
                bootstrap.Modal.getInstance(document.getElementById('editModal')).hide();
            } else {
                alert(data.message || "❌ Error al actualizar el producto");
            }
        } catch (error) {
            console.error("Error:", error);
            alert("❌ Error al procesar la solicitud");
        }
    });
});
