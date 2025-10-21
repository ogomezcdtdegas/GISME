"""
Views para generación de reportes PDF - Módulo Monitoreo Coriolis
"""
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from _AppMonitoreoCoriolis.models import BatchDetectado
from _AppComplementos.models import Sistema


class DescargarTicketBatchPDFView(LoginRequiredMixin, View):
    """
    View para generar y descargar PDF del ticket de un batch detectado
    """
    
    def get(self, request, batch_id):
        """
        Genera PDF con información del ticket del batch
        """
        try:
            # Obtener datos del batch
            batch = get_object_or_404(BatchDetectado, id=batch_id)
            
            # Crear respuesta HTTP para PDF
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="ticket_batch_{batch_id}.pdf"'
            
            # Crear canvas para PDF
            p = canvas.Canvas(response, pagesize=A4)
            width, height = A4
            
            # === HEADER SECTION ===
            # Logo (simulado como rectángulo negro)
            p.setFillColorRGB(0, 0, 0)
            p.rect(40, height-100, 100, 70, fill=1)
            
            # Título y número de ticket
            p.setFont("Helvetica-Bold", 18)
            p.drawString(180, height-60, "COLGAS S.A E.S.P")
            
            p.setFont("Helvetica", 14)
            p.drawString(180, height-85, "Ticket #:")
            ticket_num = batch.num_ticket if batch.num_ticket else "SIN ASIGNAR"
            p.setFont("Helvetica-Bold", 14)
            p.drawString(250, height-85, str(ticket_num))
            
            # === INFORMACIÓN BÁSICA ===
            y_pos = height - 130
            p.setFont("Helvetica-Bold", 16)
            p.drawCentredString(width/2, y_pos, "INFORMACIÓN BÁSICA")
            
            # Tabla de información básica
            y_pos -= 30
            
            # Fecha (fila completa)
            p.setFillColorRGB(0.9, 0.9, 0.9)  # Fondo gris claro
            p.rect(40, y_pos-20, 250, 20, fill=1, stroke=1)
            p.setFillColorRGB(0, 0, 0)  # Texto negro
            p.setFont("Helvetica", 12)
            p.drawString(50, y_pos-10, "Fecha")
            p.drawString(200, y_pos-10, batch.fecha_inicio.strftime("%d/%m/%Y") if batch.fecha_inicio else "N/A")
            
            # Hora inicio y final (dos columnas)
            y_pos -= 20
            # Hora inicio
            p.rect(40, y_pos-20, 125, 20, stroke=1)
            p.drawString(50, y_pos-10, "Hora inicio")
            p.drawString(100, y_pos-10, batch.fecha_inicio.strftime("%H:%M") if batch.fecha_inicio else "N/A")
            
            # Hora final
            p.rect(165, y_pos-20, 125, 20, stroke=1)
            p.drawString(175, y_pos-10, "Hora final")
            p.drawString(225, y_pos-10, batch.fecha_fin.strftime("%H:%M") if batch.fecha_fin else "N/A")
            
            # === SECCIÓN PRODUCTO Y RECIBIDO ===
            y_pos -= 40
            
            # Headers de las dos columnas
            p.setFont("Helvetica-Bold", 14)
            p.setFillColorRGB(0.8, 0.8, 0.8)  # Fondo gris
            p.rect(40, y_pos-20, 125, 20, fill=1, stroke=1)
            p.rect(165, y_pos-20, 125, 20, fill=1, stroke=1)
            p.setFillColorRGB(0, 0, 0)  # Texto negro
            p.drawCentredString(102.5, y_pos-10, "PRODUCTO:")
            p.drawCentredString(227.5, y_pos-10, "RECIBIDO")
            
            y_pos -= 20
            
            # Datos del producto y recibido
            producto_datos = [
                ("Gravedad Específica a 60°F:", "10654,0000"),
                ("Temperatura:", f"{batch.temperatura_coriolis_prom:.2f}°C" if batch.temperatura_coriolis_prom else "N/A"),
                ("Volumen bruto:", f"{batch.vol_total:.2f}" if batch.vol_total else "N/A")
            ]
            
            recibido_datos = [
                ("Masa Total (kg):", f"{batch.vol_total:.2f}" if batch.vol_total else "N/A"),
                ("Volumen a 60°F:", "597,25"),  # Dato quemado por ahora
                ("Densidad:", f"{batch.densidad_prom:.3f}" if batch.densidad_prom else "N/A")
            ]
            
            # Dibujar filas de datos
            for i in range(3):
                # Columna PRODUCTO
                p.rect(40, y_pos-20, 125, 20, stroke=1)
                p.setFont("Helvetica", 10)
                p.drawString(45, y_pos-10, producto_datos[i][0])
                p.setFont("Helvetica-Bold", 10)
                p.drawString(45, y_pos-15, producto_datos[i][1])
                
                # Columna RECIBIDO
                p.rect(165, y_pos-20, 125, 20, stroke=1)
                p.setFont("Helvetica", 10)
                p.drawString(170, y_pos-10, recibido_datos[i][0])
                p.setFont("Helvetica-Bold", 10)
                p.drawString(170, y_pos-15, recibido_datos[i][1])
                
                y_pos -= 20
            
            # === INFORMACIÓN ADICIONAL ===
            y_pos -= 30
            p.setFont("Helvetica", 10)
            p.drawString(40, y_pos, f"Sistema: {batch.systemId.tag if batch.systemId else 'N/A'}")
            p.drawString(40, y_pos-15, f"Duración: {batch.duracion_minutos if batch.duracion_minutos else 'N/A'} minutos")
            p.drawString(40, y_pos-30, f"Total registros: {batch.total_registros if batch.total_registros else 'N/A'}")
            
            # === FOOTER ===
            p.setFont("Helvetica", 8)
            p.drawString(40, 40, f"Generado el {batch.created_at.strftime('%d/%m/%Y %H:%M:%S') if batch.created_at else 'N/A'}")
            p.drawString(40, 30, "GISME - Sistema de Gestión Integral de Medición de Energía")
            
            # Finalizar PDF
            p.showPage()
            p.save()
            
            return response
            
        except Exception as e:
            # En caso de error, devolver respuesta de error
            return HttpResponse(f"Error al generar PDF: {str(e)}", status=500)