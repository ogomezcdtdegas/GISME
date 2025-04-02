// events.js - Eventos y listeners
document.addEventListener("DOMContentLoaded", function () {
    console.log("🟢 Página cargada - Inicializando...");
    loadTipCriticidadesPag(); // Cargar equipos al iniciar

    document.getElementById('recordsPerPage').addEventListener('change', function() {
        loadTipCriticidadesPag();
    });

    document.getElementById('tipcritForm').addEventListener('submit', async function(event) {
        event.preventDefault();
        
        const name = document.getElementById('name').value;
        const criticidadInput = document.getElementById('criticidadDropdown');
    
        if (!criticidadInput) {
            console.error("❌ No se encontró el campo criticidadDropdown en el formulario.");
            return;
        }
    
        const criticidad_id = criticidadInput.value;
    
        if (!criticidad_id) {
            alert("❌ Debes seleccionar una criticidad.");
            return;
        }
    
        const data = await crearTipCriticidad(name, criticidad_id);
        
        if (data.success) {
            alert("✅ " + data.message);
            loadTipCriticidadesPag();
            document.getElementById('tipcritForm').reset();
        } else {
            alert("⚠️ " + data.error);  // 🔹 Ahora tomamos correctamente el mensaje
        }
    });

    document.getElementById("edittipCritForm").addEventListener("submit", async function(event) {
        event.preventDefault();
        const id = document.getElementById("edittipCritId").value;
        const name = document.getElementById("editName").value;
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        const data = await actualizarTipCriticidad(id, name, csrftoken);
        if (data?.success) location.reload();
        else alert("Error al actualizar el tipo de criticidad");
    });
});
