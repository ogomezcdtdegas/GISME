"""
Views para generación de reportes PDF - Módulo Monitoreo Coriolis
"""
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    KeepTogether,
)
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
import datetime
from _AppMonitoreoCoriolis.models import BatchDetectado
from _AppComplementos.models import Sistema
from _AppMonitoreoCoriolis.views.utils import COLOMBIA_TZ
from UTIL_LIB.densidad60Modelo import rho15_from_rhoobs_api1124
from UTIL_LIB.conversiones import fahrenheit_a_celsius, g_cm3_a_kg_m3, kg_m3_a_g_cm3, celsius_a_fahrenheit, m3_a_gal

def _header_footer(ticket_num: str, generado_por: str, generado_dt: datetime.datetime, logo_path: str):
    """Crea un callback para dibujar header y footer en cada página."""

    def draw(c: canvas.Canvas, doc):
        c.saveState()

        page_width, page_height = A4
        margin = 18 * mm

        # Línea superior decorativa
        c.setStrokeColor(colors.HexColor("#0f4c81"))
        c.setLineWidth(1.2)
        c.line(margin, page_height - margin + 6, page_width - margin, page_height - margin + 6)

        # Logo y título empresa
        try:
            c.drawImage(logo_path, margin, page_height - margin - 20, width=28 * mm, height=22 * mm, preserveAspectRatio=True, mask='auto')
        except Exception:
            # Si no hay logo, continuamos sin él
            pass

        c.setFont("Helvetica-Bold", 14)
        c.drawString(margin + 32 * mm, page_height - margin - 20, "COLGAS S.A E.S.P")

        # Ticket a la derecha
        c.setFont("Helvetica", 11)
        text = f"Ticket #: {ticket_num}"
        tw = c.stringWidth(text, "Helvetica", 11)
        c.drawString(page_width - margin - tw, page_height - margin - 4, text)

        # Footer con generación y paginación
        c.setFont("Helvetica", 8)
        generado_str = generado_dt.strftime("%d/%m/%Y a las %H:%M")
        footer_left = f"Generado el {generado_str} por {generado_por}"
        c.drawString(margin, margin - 8, footer_left)
        c.drawString(margin, margin - 18, "GISME - Sistema de Gestión Integral de Medición de Energía")

        page_text = f"Página {doc.page}"
        ptw = c.stringWidth(page_text, "Helvetica", 8)
        c.drawString(page_width - margin - ptw, margin - 8, page_text)

        c.restoreState()

    return draw


class DescargarTicketBatchPDFView(LoginRequiredMixin, View):
    """
    View para generar y descargar PDF del ticket de un batch detectado
    """
    
    def get(self, request, batch_id):
        """
        Genera PDF con información del ticket del batch usando el nuevo formato de tarjetas
        """
        try:
            # Obtener datos del batch
            batch = get_object_or_404(BatchDetectado, id=batch_id)
            
            # Crear respuesta HTTP para PDF
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="ticket_batch_{batch_id}.pdf"'
            
            # Generar PDF usando la función build_pdf
            self._build_pdf(response, batch, request.user.username)
            
            return response
            
        except Exception as e:
            # En caso de error, devolver respuesta de error
            return HttpResponse(f"Error al generar PDF: {str(e)}", status=500)
    
    def _build_pdf(self, output_stream, batch: BatchDetectado, generado_por: str):
        """Genera un PDF con tres tarjetas centradas (estilo ficha)."""
        
        generado_dt = datetime.datetime.now(COLOMBIA_TZ)
        
        # Extraer datos del batch con conversión a zona horaria de Colombia
        ticket_num = str(batch.num_ticket)[:8]  # Usar los primeros 8 caracteres del ID como ticket
        
        # Convertir fechas UTC a Colombia
        if batch.fecha_inicio:
            fecha_inicio_colombia = batch.fecha_inicio.astimezone(COLOMBIA_TZ)
            fecha = fecha_inicio_colombia.strftime("%d/%m/%Y")
            hora_inicio = fecha_inicio_colombia.strftime("%H:%M")
        else:
            fecha = "N/A"
            hora_inicio = "N/A"
            
        if batch.fecha_fin:
            fecha_fin_colombia = batch.fecha_fin.astimezone(COLOMBIA_TZ)
            hora_final = fecha_fin_colombia.strftime("%H:%M")
        else:
            hora_final = "N/A"
        
        # Datos del batch - Valores quemados y valores reales
        localizacion = "Salgar, Cundinamarca"  # Valor quemado como solicitaste
        nombre_sistema = batch.systemId.tag if batch.systemId else "N/A"
        producto = "GLP"  # Valor quemado como solicitaste
        
        # Datos reales del batch
        rho_obs = g_cm3_a_kg_m3(batch.densidad_prom)  # kg/m3
        T_obs_C = batch.temperatura_coriolis_prom # °C
        rho15, gamma60 = rho15_from_rhoobs_api1124(rho_obs, T_obs_C)
        rho15_g_cm3 = kg_m3_a_g_cm3(rho15)

        densidad_std = f"{rho15_g_cm3:.5f} g/cm³" if rho15_g_cm3 is not None else "N/A"
        temperatura_fluido = f"{celsius_a_fahrenheit(batch.temperatura_coriolis_prom):.2f} °F" if celsius_a_fahrenheit(batch.temperatura_coriolis_prom) is not None else "N/A"
        presion_fluido = f"{batch.pressure_out_prom:.2f} psi" if batch.pressure_out_prom is not None else "N/A"
        masa_total = f"{batch.mass_total:.2f} kg" if batch.mass_total is not None else "N/A"
        densidad_flujo = f"{batch.densidad_prom:.5f} g/cm³" if batch.densidad_prom is not None else "N/A"
        
        # Usar volumen total directamente (ya está en galones)
        if batch.vol_total is not None:
            volumen_bruto = f"{batch.vol_total:.2f} gal"
        else:
            volumen_bruto = "N/A"

        volumen_estandar = m3_a_gal(batch.mass_total/rho15)
        volumen_estandar_60f = f"{volumen_estandar:.5f} gal" if volumen_estandar is not None else "N/A"
        
        # Calcular duración del batch
        if batch.fecha_inicio and batch.fecha_fin:
            duracion_td = batch.fecha_fin - batch.fecha_inicio
            duracion_minutos = duracion_td.total_seconds() / 60
            duracion = f"{duracion_minutos:.2f} minutos"
        else:
            duracion = "N/A"
            
        identificacion_medidor = "Medidor #A-1234"  # Valor quemado como solicitaste
        total_registros = batch.total_registros if hasattr(batch, 'total_registros') and batch.total_registros else 0
        logo_path = "colgasLogo.jpg"  # Path del logo
        
        # Documento y estilos
        doc = SimpleDocTemplate(
            output_stream,
            pagesize=A4,
            leftMargin=18 * mm,
            rightMargin=18 * mm,
            topMargin=25 * mm,
            bottomMargin=20 * mm,
            title="Ticket Colgas",
            author=generado_por,
        )

        styles = getSampleStyleSheet()
        style_card_title = ParagraphStyle(
            name="CardTitle",
            parent=styles["Heading4"],
            fontName="Helvetica-Bold",
            fontSize=11.5,
            textColor=colors.HexColor("#0f4c81"),
            alignment=1,  # CENTER
            spaceBefore=2,
            spaceAfter=2,
        )
        style_label = ParagraphStyle(
            name="Label",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.5,
            textColor=colors.black,
        )
        style_value = ParagraphStyle(
            name="Value",
            parent=styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=9.5,
            textColor=colors.black,
            alignment=2,  # RIGHT
        )

        def make_card(title: str, rows: list, col_widths):
            header = [Paragraph(title, style_card_title)]
            data = [header] + rows
            tbl = Table(data, colWidths=col_widths, hAlign="CENTER")
            tbl.setStyle(
                TableStyle([
                    ("SPAN", (0, 0), (-1, 0)),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e9eef6")),
                    ("BOX", (0, 0), (-1, -1), 0.9, colors.HexColor("#d9dde8")),
                    ("INNERGRID", (0, 1), (-1, -1), 0.25, colors.lightgrey),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("ALIGN", (1, 1), (1, -1), "RIGHT"),
                    ("ALIGN", (3, 1), (3, -1), "RIGHT"),
                ])
            )
            return KeepTogether(tbl)

        content = []

        # Ancho de tarjeta (4 columnas: etq/val | etq/val)
        col_widths = [45 * mm, 40 * mm, 45 * mm, 40 * mm]

        # Tarjeta 1: Información básica
        card1_rows = [
            [Paragraph("Localización", style_label), Paragraph(localizacion, style_value),
             Paragraph("Nombre del sistema", style_label), Paragraph(nombre_sistema, style_value)],
            [Paragraph("Fecha de generación", style_label), Paragraph(generado_dt.strftime("%d/%m/%Y %H:%M"), style_value),
             Paragraph("Producto", style_label), Paragraph(producto, style_value)],
            [Paragraph("Inicio de bache", style_label), Paragraph(f"{fecha} {hora_inicio}", style_value),
             Paragraph("Fin de bache", style_label), Paragraph(f"{fecha} {hora_final}", style_value)],
        ]
        content.append(make_card("Información básica", card1_rows, col_widths))
        content.append(Spacer(1, 8))

        # Tarjeta 2: Datos de operación (dos columnas)
        card2_rows = [
            [Paragraph("Densidad@std", style_label), Paragraph(densidad_std, style_value),
             Paragraph("Masa total", style_label), Paragraph(masa_total, style_value)],
            [Paragraph("Temperatura del fluido", style_label), Paragraph(temperatura_fluido, style_value),
             Paragraph("Densidad@flujo", style_label), Paragraph(densidad_flujo, style_value)],
            [Paragraph("Presión del fluido", style_label), Paragraph(presion_fluido, style_value),
             Paragraph("Volumen bruto", style_label), Paragraph(volumen_bruto, style_value)],
            [Paragraph("Volumen a 60°F", style_label), Paragraph(volumen_estandar_60f, style_value),
             Paragraph("", style_label), Paragraph("", style_value)],
        ]
        content.append(make_card("Datos de operación", card2_rows, col_widths))
        content.append(Spacer(1, 8))

        # Tarjeta 3: Información adicional
        card3_rows = [
            [Paragraph("Duración del bache", style_label), Paragraph(duracion, style_value),
             Paragraph("Identificación del medidor", style_label), Paragraph(identificacion_medidor, style_value)],
        ]
        content.append(make_card("Información adicional", card3_rows, col_widths))

        # Construir documento con callback de header/footer
        draw_cb = _header_footer(ticket_num, generado_por, generado_dt, logo_path)
        doc.build(content, onFirstPage=draw_cb, onLaterPages=draw_cb)