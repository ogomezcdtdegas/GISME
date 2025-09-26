// ====================================================================
// PDF-GENERATOR.JS - Generación de reportes PDF
// ====================================================================

// Función para descargar reporte PDF
async function descargarReportePDF() {
    // Llena los datos del reporte
    const sistemaNombre = document.getElementById('sistemaTitle').textContent.trim();
    const sistemaEstado = document.getElementById('sistemaInfo')?.textContent.trim() || 'N/A';
    const tempText = document.getElementById('display-sensor2').textContent;
    document.getElementById('pdf-sistema-nombre').textContent = sistemaNombre;
    document.getElementById('pdf-sistema-estado').textContent = sistemaEstado;
    document.getElementById('pdf-temperatura').textContent = tempText;

    // Dibuja el gráfico de temperatura usando Chart.js
    const temp = parseFloat(tempText);
    const ctx = document.getElementById('pdf-grafica-temperatura').getContext('2d');
    if (window.pdfChart) {
        window.pdfChart.destroy();
    }
    window.pdfChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: Array.from({length: 10}, (_, i) => `T-${10 - i}`),
            datasets: [{
                label: 'Temperatura (°F)',
                data: Array.from({length: 9}, () => (90 + Math.random() * 20).toFixed(1)).concat([temp]),
                borderColor: '#28a745',
                backgroundColor: 'rgba(40,167,69,0.1)',
                tension: 0.3,
                pointRadius: 2
            }]
        },
        options: {
            responsive: false,
            maintainAspectRatio: false,
            animation: false,
            plugins: {
                legend: { display: true },
                title: { display: false }
            },
            scales: {
                x: { title: { display: true, text: 'Tiempo' } },
                y: { title: { display: true, text: 'Temperatura (°F)' }, beginAtZero: true }
            }
        }
    });

    // Espera a que Chart.js termine de renderizar
    await new Promise(resolve => setTimeout(resolve, 300));

    // Muestra el contenedor temporalmente para capturarlo
    const reporte = document.getElementById('reportePDF');
    reporte.style.display = 'block';

    // Usa html2canvas para capturar el reporte
    const canvas = await html2canvas(reporte, {backgroundColor: "#fff"});
    const imgData = canvas.toDataURL('image/png');

    // Crea el PDF
    const { jsPDF } = window.jspdf;
    const pdf = new jsPDF();
    // Título y datos generales
    pdf.setFontSize(16);
    pdf.text('Reporte del Sistema Coriolis', 15, 15);
    pdf.setFontSize(12);
    pdf.text('Sistema: ' + sistemaNombre, 15, 25);
    pdf.text('Estado: ' + sistemaEstado, 15, 32);
    pdf.text('Temperatura actual: ' + tempText, 15, 39);
    // Imagen del gráfico
    pdf.addImage(imgData, 'PNG', 10, 45, 190, 0);
    pdf.save('reporte_coriolis.pdf');

    // Oculta el contenedor de nuevo
    reporte.style.display = 'none';
}