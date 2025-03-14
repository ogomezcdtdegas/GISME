// events.js - Eventos y listeners
document.addEventListener("DOMContentLoaded", function () {
    console.log("🟢 Página cargada - Inicializando...");
    loadEquiposPag(); // Cargar equipos al iniciar

    document.getElementById('recordsPerPage').addEventListener('change', function() {
        loadEquiposPag();
    });

    document.getElementById('equipoForm').addEventListener('submit', async function(event) {
        event.preventDefault();
        const serial = document.getElementById('serial').value;
        const sap = document.getElementById('sap').value;
        const marca = document.getElementById('marca').value;

        const data = await crearEquipo(serial, sap, marca);
        if (data?.success) {
            loadEquiposPag();
            document.getElementById('equipoForm').reset();
        } else {
            alert("❌ Error al registrar equipo");
        }
    });

    document.getElementById("editEquipoForm").addEventListener("submit", async function(event) {
        event.preventDefault();
        const id = document.getElementById("editEquipoId").value;
        const serial = document.getElementById("editSerial").value;
        const sap = document.getElementById("editSap").value;
        const marca = document.getElementById("editMarca").value;
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        const data = await actualizarEquipo(id, serial, sap, marca, csrftoken);
        if (data?.success) location.reload();
        else alert("Error al actualizar equipo");
    });
});
