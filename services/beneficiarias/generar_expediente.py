# -*- coding: utf-8 -*-
from odoo import models, api  # type: ignore
from io import BytesIO
from reportlab.lib.pagesizes import letter  # type: ignore
from reportlab.pdfgen import canvas  # type: ignore
from reportlab.lib.units import inch  # type: ignore
from reportlab.lib.utils import ImageReader  # type: ignore
import base64


class GenerarExpedienteBeneficiariaService(models.AbstractModel):
    _name = "beneficiarias.expediente.service"
    _description = "Servicio para generar el expediente completo de una beneficiaria"
    _table = False  # ⚠️ Evita que Odoo intente crear una tabla

    @api.model
    def generar_expediente_pdf(self, beneficiaria):
        """Genera el PDF completo del expediente y lo guarda como documento adjunto."""
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        # Obtener logo de la compañía (si existe)
        company = self.env.company
        if company.logo:
            try:
                logo_data = base64.b64decode(company.logo)
                logo_image = ImageReader(BytesIO(logo_data))
                p.drawImage(
                    logo_image,
                    inch,
                    height - 2 * inch,
                    width=2 * inch,
                    preserveAspectRatio=True,
                    mask="auto",
                )
            except Exception as e:
                # En caso de error con el logo, continuar sin interrumpir el PDF
                print(f"[WARN] No se pudo agregar el logo de la empresa: {e}")

        # Portada
        p.setFont("Helvetica-Bold", 18)
        p.drawCentredString(width / 2, height - 100, "Expediente de Beneficiaria")

        p.setFont("Helvetica", 14)
        p.drawCentredString(width / 2, height - 140, beneficiaria.nombre_completo or "")

        p.setFont("Helvetica", 12)
        y = height - 200
        line_height = 18

        # Datos básicos de la beneficiaria
        data = [
            ("CURP", beneficiaria.curp or "-"),
            ("RFC", beneficiaria.rfc or "-"),
            ("Fecha de nacimiento", str(beneficiaria.fecha_nacimiento or "-")),
            ("Fecha de ingreso", str(beneficiaria.fecha_ingreso or "-")),
            ("Centro VIFAC", beneficiaria.atention_center or "-"),
        ]

        for label, value in data:
            p.drawString(inch, y, f"{label}: {value}")
            y -= line_height

        # Finalizar PDF
        p.showPage()
        p.save()

        pdf_data = buffer.getvalue()
        buffer.close()

        # Guardar el PDF en el modelo de documentos
        self.env["beneficiarias.documento"].create({
            "name": f"Expediente - {beneficiaria.nombre_completo}",
            "descripcion": "Expediente completo generado automáticamente.",
            "archivo": base64.b64encode(pdf_data),
            "nombre_archivo": f"Expediente - {beneficiaria.nombre_completo}.pdf",
            "tipo_relacion": "beneficiaria",
            "beneficiaria_id": beneficiaria.id,
        })

        return True
