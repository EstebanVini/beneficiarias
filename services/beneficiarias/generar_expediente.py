# -*- coding: utf-8 -*-
from odoo import models, api #type: ignore[import]
from io import BytesIO
from reportlab.lib.pagesizes import letter #type: ignore[import]
from reportlab.pdfgen import canvas #type: ignore[import]
from reportlab.lib.units import inch #type: ignore[import]
from reportlab.lib.utils import ImageReader #type: ignore[import]
import base64
import re


class GenerarExpedienteBeneficiariaService(models.AbstractModel):
    _name = "beneficiarias.expediente.service"
    _description = "Servicio para generar el expediente completo de una beneficiaria"
    _table = False

    @api.model
    def generar_expediente_pdf(self, beneficiaria):
        """Genera el PDF completo del expediente y lo guarda como documento adjunto."""
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        # === PORTADA ===
        self._add_portada(p, beneficiaria, width, height)

        # === ÍNDICE ===
        sections = [
            "Información Particular Detallada",
            "Residencia",
            "Canalización y Legal",
            "Fotos",
            "Detalle del Servicio",
            "Acompañante y Referencias",
            "Familiares",
            "Hijos",
            "Relación con el Padre del Bebé",
            "Datos de Violencia",
            "Antecedentes Médicos",
            "Medios de Comunicación",
            "Documentos",
            "Traslados",
            "Talleres",
            "Valoraciones",
            "Proyecto de Vida",
            "Datos del Parto",
            "Alta",
        ]
        self._add_indice(p, sections, width, height)

        # === PRIMERA SECCIÓN: Información Particular Detallada ===
        self._add_section_informacion_particular(p, beneficiaria, width, height)

        # Finalizar PDF
        p.save()
        pdf_data = buffer.getvalue()
        buffer.close()

        # Guardar PDF como documento adjunto
        self.env["beneficiarias.documento"].create({
            "name": f"Expediente - {beneficiaria.nombre_completo}",
            "descripcion": "Expediente completo generado automáticamente.",
            "archivo": base64.b64encode(pdf_data),
            "nombre_archivo": f"Expediente - {beneficiaria.nombre_completo}.pdf",
            "tipo_relacion": "beneficiaria",
            "beneficiaria_id": beneficiaria.id,
        })
        return True

    # ----------------------------------------------------------
    # 🔹 MÉTODOS DE SECCIONES
    # ----------------------------------------------------------
    def _add_portada(self, p, beneficiaria, width, height):
        """Dibuja la portada con el logo, nombre, descripción y marca de agua."""
        margin_top = height - 2.5 * inch  # margen superior más grande
        center_y = height / 2 + inch      # punto de inicio visual centrado

        # === LOGO DE LA COMPAÑÍA ===
        company = self.env.company
        if company.logo:
            try:
                logo_data = base64.b64decode(company.logo)
                logo_image = ImageReader(BytesIO(logo_data))
                p.drawImage(
                    logo_image,
                    width / 2 - inch,  # centrado horizontalmente
                    margin_top,
                    width=2 * inch,
                    preserveAspectRatio=True,
                    mask="auto",
                )
            except Exception as e:
                print(f"[WARN] No se pudo agregar el logo: {e}")

        # === TÍTULO ===
        p.setFont("Helvetica-Bold", 20)
        p.drawCentredString(width / 2, center_y + 120, "EXPEDIENTE DE BENEFICIARIA")

        # === NOMBRE ===
        p.setFont("Helvetica-Bold", 16)
        p.drawCentredString(width / 2, center_y + 70, beneficiaria.nombre_completo or "")

        # === CENTRO VIFAC ===
        p.setFont("Helvetica", 13)
        p.drawCentredString(width / 2, center_y + 40, f"Centro VIFAC: {beneficiaria.atention_center or '-'}")

        # === FECHAS ===
        p.setFont("Helvetica", 12)
        p.drawCentredString(width / 2, center_y + 10, f"Fecha de ingreso: {str(beneficiaria.fecha_ingreso or '-')}")

        # === DESCRIPCIÓN (limpia el HTML) ===
        if beneficiaria.descripcion:
            p.setFont("Helvetica-Oblique", 11)
            clean_desc = re.sub(r"<[^>]*>", "", beneficiaria.descripcion or "")  # quitar etiquetas HTML
            clean_desc = clean_desc.replace("&nbsp;", " ").strip()
            if len(clean_desc) > 200:
                clean_desc = clean_desc[:197] + "..."
            p.drawCentredString(width / 2, center_y - 30, clean_desc)

        # === MARCA DE AGUA (footer) ===
        footer_text = "Expediente generado automáticamente por el módulo de beneficiarias VIFAC en Odoo 17 Community"
        p.setFont("Helvetica-Oblique", 9)
        p.setFillGray(0.5, 0.5)
        p.drawCentredString(width / 2, 0.5 * inch, footer_text)
        p.setFillGray(0, 1)

        # === Finalizar portada ===
        p.showPage()

    
    def _add_footer(self, p, width, height):
        """Agrega pie de página con marca de agua en cada hoja."""
        footer_text = "Expediente generado automáticamente por el módulo de beneficiarias VIFAC en Odoo 17 Community"
        p.setFont("Helvetica-Oblique", 8)
        p.setFillGray(0.5, 0.5)  # color gris tenue
        p.drawCentredString(width / 2, 0.5 * inch, footer_text)
        p.setFillGray(0, 1)  # restaurar color normal



    def _add_indice(self, p, sections, width, height):
        """Genera el índice del expediente."""
        p.setFont("Helvetica-Bold", 16)
        p.drawCentredString(width / 2, height - 80, "ÍNDICE")

        y = height - 120
        p.setFont("Helvetica", 12)
        line_height = 18

        for i, section in enumerate(sections, start=1):
            p.drawString(inch, y, f"{i}. {section}")
            y -= line_height

            if y < inch:  # Si se llena la página, pasar a la siguiente
                p.showPage()
                y = height - inch

        p.showPage()

    def _add_section_informacion_particular(self, p, beneficiaria, width, height):
        """Primera sección: Información Particular Detallada"""
        p.setFont("Helvetica-Bold", 16)
        p.drawCentredString(width / 2, height - 80, "INFORMACIÓN PARTICULAR DETALLADA")

        # Configuración visual
        y = height - 130
        line_height = 20         # Espacio entre líneas normales
        section_spacing = 25     # Espacio entre secciones
        subtitle_spacing = 20    # Espacio después de cada subtítulo
        left_margin = inch

        # Función auxiliar para dibujar campos
        def draw_field(label, value):
            nonlocal y
            if y < inch:
                self._add_footer(p, width, height)
                p.showPage()
                y = height - 100
                p.setFont("Helvetica-Bold", 16)
                p.drawCentredString(width / 2, height - 80, "INFORMACIÓN PARTICULAR DETALLADA (cont.)")
                y -= 40
                p.setFont("Helvetica", 11)
            p.drawString(left_margin, y, f"{label}: {value or '-'}")
            y -= line_height

        # === SECCIÓN: DATOS DE CONTACTO ===
        p.setFont("Helvetica-Bold", 13)
        p.drawString(left_margin, y, "Datos de Contacto")
        y -= subtitle_spacing
        p.setFont("Helvetica", 11)

        draw_field("Correo", beneficiaria.correo)
        draw_field("Teléfono", beneficiaria.telefono)
        draw_field("Teléfono Celular", beneficiaria.telefono_celular)

        if beneficiaria.tiene_red_social:
            y -= 5
            p.setFont("Helvetica-Bold", 12)
            p.drawString(left_margin, y, "Redes Sociales")
            y -= subtitle_spacing
            p.setFont("Helvetica", 11)
            draw_field(getattr(beneficiaria, "tipo_red_social1", "Red social 1"), beneficiaria.red_social1)
            draw_field(getattr(beneficiaria, "tipo_red_social2", "Red social 2"), beneficiaria.red_social2)

        # === SECCIÓN: DATOS DE NACIMIENTO ===
        y -= section_spacing
        p.setFont("Helvetica-Bold", 13)
        p.drawString(left_margin, y, "Datos de Nacimiento")
        y -= subtitle_spacing
        p.setFont("Helvetica", 11)

        draw_field("País de Nacimiento", getattr(beneficiaria.pais_nacimiento, "name", None))
        draw_field("Estado de Nacimiento", getattr(beneficiaria.estado_nacimiento, "name", None))
        draw_field("Ciudad de Nacimiento", beneficiaria.ciudad_nacimiento)

        # === SECCIÓN: NIVEL SOCIOECONÓMICO ===
        y -= section_spacing
        p.setFont("Helvetica-Bold", 13)
        p.drawString(left_margin, y, "Nivel Socioeconómico")
        y -= subtitle_spacing
        p.setFont("Helvetica", 11)

        draw_field("Grado de estudios", beneficiaria.grado_estudios)
        draw_field("Estado civil", beneficiaria.estado_civil)
        draw_field("Ocupación", beneficiaria.ocupacion)
        draw_field("Nivel económico", beneficiaria.nivel_economico)
        draw_field("Tipo de población", beneficiaria.tipo_poblacion)

        # === SECCIÓN: RELIGIÓN ===
        y -= section_spacing
        p.setFont("Helvetica-Bold", 13)
        p.drawString(left_margin, y, "Religión")
        y -= subtitle_spacing
        p.setFont("Helvetica", 11)

        draw_field("Religión", beneficiaria.religion)
        if beneficiaria.religion == "otro":
            draw_field("Especificar religión", beneficiaria.religion_otro)

        # === Footer al final de la página ===
        self._add_footer(p, width, height)
        p.showPage()


