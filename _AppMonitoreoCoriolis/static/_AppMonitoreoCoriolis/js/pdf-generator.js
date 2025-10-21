// ====================================================================
// PDF-GENERATOR.JS - Generación de reportes PDF
// ====================================================================

// Función para descargar reporte PDF
async function descargarReportePDF() {
    const { jsPDF } = window.jspdf;
    const pdf = new jsPDF('p', 'mm', 'a4');

    // Logo (simulado como rectángulo negro)
    pdf.setFillColor(0, 0, 0);
    pdf.rect(20, 20, 50, 35, 'F');

    // Título y ticket
    pdf.setFontSize(16);
    pdf.text('COLGAS S.A E.S.P', 80, 35);
    pdf.setFontSize(12);
    pdf.text('Ticket #:', 80, 45);
    pdf.text('1530', 110, 45);

    // Información básica
    pdf.setFontSize(13);
    pdf.setFont(undefined, 'bold');
    pdf.text('INFORMACIÓN BÁSICA', 60, 60);
    pdf.setFont(undefined, 'normal');
    pdf.setFontSize(11);

    // Fecha
    pdf.rect(20, 65, 200, 10);
    pdf.text('Fecha', 22, 72);
    pdf.text('17/10/2025', 70, 72);

    // Hora inicio y final
    pdf.rect(20, 75, 40, 10);
    pdf.text('Hora inicio', 22, 82);
    pdf.text('14:23', 45, 82);

    pdf.rect(60, 75, 40, 10);
    pdf.text('Hora final', 62, 82);
    pdf.text('14:36', 85, 82);

    // Producto
    pdf.rect(20, 90, 60, 7);
    pdf.setFont(undefined, 'bold');
    pdf.text('PRODUCTO:', 22, 95);
    pdf.setFont(undefined, 'normal');
    pdf.rect(20, 97, 60, 7);
    pdf.text('Gravedad Específica a 60°F:', 22, 102);
    pdf.text('10654,0000', 65, 102);
    pdf.rect(20, 104, 60, 7);
    pdf.text('Temperatura:', 22, 109);
    pdf.text('69,37', 65, 109);
    pdf.rect(20, 111, 60, 7);
    pdf.text('Volumen bruto:', 22, 116);
    pdf.text('629,84', 65, 116);

    // Recibido
    pdf.rect(85, 90, 60, 7);
    pdf.setFont(undefined, 'bold');
    pdf.text('RECIBIDO', 87, 95);
    pdf.setFont(undefined, 'normal');
    pdf.rect(85, 97, 60, 7);
    pdf.text('Masa Total (kg):', 87, 102);
    pdf.text('2390,31', 135, 102);
    pdf.rect(85, 104, 60, 7);
    pdf.text('Volumen a 60°F:', 87, 109);
    pdf.text('597,25', 135, 109);
    pdf.rect(85, 111, 60, 7);
    pdf.text('Densidad:', 87, 116);
    pdf.text('10.026,000', 135, 116);

    pdf.save('ticket_batch.pdf');
}