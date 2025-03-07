
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
        
        generarHistograma( data.histograma_data); 
            

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

function generarHistograma(histogramaData) {
    const chartContainer = document.getElementById("chartContainer");

    // 💡 Eliminar el canvas anterior y crear uno nuevo para evitar errores
    chartContainer.innerHTML = '<canvas id="histogramaChart"></canvas>';
    const ctx = document.getElementById("histogramaChart").getContext("2d");

    // 📌 Verificar si `histogramaData` tiene datos antes de graficar
    if (!histogramaData || histogramaData.length === 0) {
        console.error("Error: histogramaData está vacío.");
        return;
    }

    // 📌 Definir bins (intervalos del histograma)
    const bins = 100;
    const min = Math.min(...histogramaData);
    const max = Math.max(...histogramaData);
    const step = (max - min) / bins;

    let histogramCounts = Array(bins).fill(0);
    let histogramLabels = [];

    for (let i = 0; i < bins; i++) {
        histogramLabels.push((min + i * step).toFixed(2));
    }

    histogramaData.forEach(value => {
        let index = Math.floor((value - min) / step);
        if (index >= bins) index = bins - 1;
        histogramCounts[index]++;
    });

    // 📊 Crear el histograma con Chart.js y almacenarlo en la variable global
    histogramaChart = new Chart(ctx, {
    type: "bar",
    data: {
        labels: histogramLabels,
        datasets: [{
            label: "Frecuencia",
            data: histogramCounts,
            backgroundColor: "rgba(75, 192, 192, 0.5)", // Color con transparencia
            borderColor: "rgba(75, 192, 192, 1)",       // Borde más intenso
            borderWidth: 2,
            hoverBackgroundColor: "rgba(255, 99, 132, 0.6)", // Color al pasar el mouse
            hoverBorderColor: "rgba(255, 99, 132, 1)"
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: {
            duration: 2000,  // Duración de la animación
            easing: 'easeOutBounce' // Tipo de animación
        },
        plugins: {
            legend: { position: "top" }, // Posición de la leyenda
            tooltip: { enabled: true, mode: "index", intersect: false } // Tooltips avanzados
        },
        scales: {
            x: { title: { display: true, text: "Valores Simulados", color: "#333", font: { size: 14 } } },
            y: { title: { display: true, text: "Frecuencia", color: "#333", font: { size: 14 } } }
        }
    }
});

    console.log("Histograma actualizado correctamente.");
}      


