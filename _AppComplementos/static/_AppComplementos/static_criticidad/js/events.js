// events.js - Eventos y listeners
document.addEventListener("DOMContentLoaded", function () {
    console.log("🟢 Página cargada - Inicializando...");
    loadCriticidadesPag(); // Cargar equipos al iniciar

    document.getElementById('recordsPerPage').addEventListener('change', function() {
        loadCriticidadesPag();
    });

    document.getElementById('critForm').addEventListener('submit', async function(event) {
        event.preventDefault();
        const name = document.getElementById('name').value;

        const data = await crearCriticidad(name);
        if (data?.success) {
            loadCriticidadesPag();
            document.getElementById('critForm').reset();
        } else {
            alert("❌ Error al registrar criticidad");
        }
    });

    document.getElementById("editCritForm").addEventListener("submit", async function(event) {
        event.preventDefault();
        const id = document.getElementById("editCritId").value;
        const name = document.getElementById("editName").value;
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        const data = await actualizarCriticidad(id, name, csrftoken);
        if (data?.success) location.reload();
        else alert("Error al actualizar la criticidad");
    });
});
