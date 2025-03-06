
console.log("✅ script.js cargado correctamente.");

async function calcularIncertidumbre() {
    console.log("Iniciando cálculo de incertidumbre...");

    const densidad_medida = document.getElementById("densidad_medida").value;
    const u_cal = document.getElementById("u_cal").value;
    const u_res = document.getElementById("u_res").value;
    const u_der = document.getElementById("u_der").value;

    if (!densidad_medida || !u_cal || !u_res || !u_der) {
        console.log("⚠️ Falta ingresar valores.");
        document.getElementById("resultado_incertidumbre").innerText = "⚠️ Por favor, ingresa todos los valores.";
        return;
    }

    try {
        console.log("Enviando solicitud a la API...");

        const response = await fetch("/calc2/incertidumbre/", {  // 🔹 Se usa la misma URL para GET y POST
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                densidad_medida: parseFloat(densidad_medida),
                u_cal: parseFloat(u_cal),
                u_res: parseFloat(u_res),
                u_der: parseFloat(u_der)
            })
        });

        console.log("Respuesta recibida:", response);

        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status} ${response.statusText}`);
        }

        const data = await response.json();  // 🔹 Intentar parsear la respuesta como JSON
        console.log("📌 Datos recibidos:", data);

        if (data.error) {
            document.getElementById("resultado_incertidumbre").innerText = "❌ Error: " + data.error;
            return;
        }

        // 🔹 Mostrar los resultados en el HTML
        document.getElementById("resultado_incertidumbre").innerHTML = 
            `<b>✅ Densidad Medida:</b> ${data.valor_medido.toFixed(5)}<br>` +
            `<b>📊 Incertidumbre Expandida (95%):</b> ${data.incertidumbre_expandida.toFixed(5)}`;

    } catch (error) {
        console.error("❌ Error:", error);
        document.getElementById("resultado_incertidumbre").innerText = "⚠️ Hubo un problema al calcular la incertidumbre.";
    }
}

document.addEventListener("DOMContentLoaded", function() {
    console.log("📌 DOM completamente cargado.");

    const form = document.getElementById("incertidumbreForm");

    if (form) {
        console.log("✅ Formulario encontrado en el DOM.");
        form.addEventListener("submit", function(event) {
            event.preventDefault();  // 🔹 Evita que la página se recargue
            console.log("✅ Formulario enviado.");
            calcularIncertidumbre();
        });
    } else {
        console.error("❌ Error: No se encontró el formulario con id='incertidumbreForm'.");
    }
});


