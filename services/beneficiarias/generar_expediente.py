# -*- coding: utf-8 -*-
from odoo import models, api #type: ignore[import]
from io import BytesIO
from reportlab.lib.pagesizes import letter #type: ignore[import]
from reportlab.pdfgen import canvas #type: ignore[import]
from reportlab.lib.units import inch #type: ignore[import]
from reportlab.lib.utils import ImageReader #type: ignore[import]
import base64
import re
from odoo.tools import html2plaintext #type: ignore[import]
from reportlab.pdfbase.pdfmetrics import stringWidth #type: ignore[import]
from reportlab.lib.colors import blue #type: ignore[import]
from reportlab.pdfbase.pdfmetrics import stringWidth #type: ignore[import]
        


class GenerarExpedienteBeneficiariaService(models.AbstractModel):
    _name = "beneficiarias.expediente.service"
    _description = "Servicio para generar el expediente completo de una beneficiaria"
    _table = False

    # ==========================================================
    # 1️⃣ MÉTODO PRINCIPAL (doble pasada)
    # ==========================================================
    @api.model
    def generar_expediente_pdf(self, beneficiaria):
        """Genera el PDF completo con índice dinámico y vínculos internos."""
        # Primera pasada: solo para obtener páginas y secciones
        sections_info = self._scan_sections(beneficiaria)

        # Segunda pasada: generar PDF final con índice
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        # === PORTADA ===
        self._add_portada(p, beneficiaria, width, height)

        # === ÍNDICE DINÁMICO ===
        self._add_indice(p, sections_info, width, height)

        # === SECCIONES ===
        for sec in sections_info:
            if not sec["generated"]:
                continue
            p.bookmarkPage(sec["bookmark"])
            p.addOutlineEntry(sec["title"], sec["bookmark"], level=0)
            sec["method"](p, beneficiaria, width, height)

        # === FINALIZAR PDF ===
        p.save()
        pdf_data = buffer.getvalue()
        buffer.close()

        # === GUARDAR EN ODOO ===
        self.env["beneficiarias.documento"].create({
            "name": f"Expediente - {beneficiaria.nombre_completo}",
            "descripcion": "Expediente completo generado automáticamente.",
            "archivo": base64.b64encode(pdf_data),
            "nombre_archivo": f"Expediente - {beneficiaria.nombre_completo}.pdf",
            "tipo_relacion": "beneficiaria",
            "beneficiaria_id": beneficiaria.id,
        })
        return True


    # ==========================================================
    # 2️⃣ PRIMERA PASADA (solo para detectar qué secciones hay)
    # ==========================================================
    def _scan_sections(self, beneficiaria):
        """Escanea qué secciones se generarán realmente."""
        width, height = letter
        dummy = canvas.Canvas(BytesIO(), pagesize=letter)

        # Definir las secciones con sus métodos y títulos
        sections = [
            ("DATOS GENERALES DE LA BENEFICIARIA", self._add_section_datos_generales),
            ("INFORMACIÓN PARTICULAR DETALLADA", self._add_section_informacion_particular),
            ("CANALIZACIÓN Y SEGUIMIENTO LEGAL", self._add_section_canalizacion_legal),
            ("FOTOGRAFÍAS DE LA BENEFICIARIA", self._add_section_fotos),
            ("ACOMPAÑANTE Y REFERENCIAS", self._add_section_acompanante_y_referencias),
            ("FAMILIARES", self._add_section_familiares),
            ("HIJOS", self._add_section_hijos),
            ("RELACIÓN CON EL PADRE DEL BEBÉ", self._add_section_relacion_padre),
            ("DATOS DE VIOLENCIA", self._add_section_datos_violencia),
            ("ANTECEDENTES MÉDICOS", self._add_section_antecedentes_medicos),
            ("VALORACIONES", self._add_section_valoraciones),
            ("TRASLADOS", self._add_section_traslados),
            ("TALLERES", self._add_section_talleres),
            ("PROYECTO DE VIDA", self._add_section_proyecto_de_vida),
            ("DATOS DEL PARTO Y DEL BEBÉ", self._add_section_parto_y_bebe),
            ("DATOS DE ALTA", self._add_section_alta),
        ]

        sections_info = []
        for title, method in sections:
            before = dummy.getPageNumber()
            method(dummy, beneficiaria, width, height)
            after = dummy.getPageNumber()
            generated = after > before
            bookmark = re.sub(r"\W+", "_", title.lower())
            sections_info.append({
                "title": title,
                "method": method,
                "bookmark": bookmark,
                "generated": generated,
            })
        return [s for s in sections_info if s["generated"]]


    # ==========================================================
    # 3️⃣ ÍNDICE DINÁMICO CON HIPERVÍNCULOS
    # ==========================================================
    def _add_indice(self, p, sections_info, width, height):
        """Genera el índice dinámico con vínculos internos."""
        p.setFont("Helvetica-Bold", 16)
        p.drawCentredString(width / 2, height - 80, "ÍNDICE")

        y = height - 130
        line_height = 20
        left_margin = inch

        for i, sec in enumerate(sections_info, start=1):
            text = f"{i}. {sec['title']}"
            p.setFillColor(blue)
            p.drawString(left_margin, y, text)

            link_width = stringWidth(text, "Helvetica", 12)
            p.linkRect(
                "", sec["bookmark"],
                (left_margin, y - 2, left_margin + link_width, y + 10),
                relative=1, thickness=0,
            )

            p.setFillColorRGB(0, 0, 0)
            y -= line_height

            if y < inch + 40:
                p.showPage()
                y = height - 100
                p.setFont("Helvetica-Bold", 16)
                p.drawCentredString(width / 2, height - 80, "ÍNDICE (cont.)")
                y -= 40
                p.setFont("Helvetica", 12)

        self._add_footer(p, width, height)
        p.showPage()
    
    #----------------------------------------------------------
    # Función para valores diferentes
    #----------------------------------------------------------

    def _safe_value(self, value):
        """Devuelve un valor limpio para texto o campos Many2one"""
        if not value:
            return "-"
        if hasattr(value, "name"):
            return value.name
        return str(value)

    # ----------------------------------------------------------
    # 🔹 MÉTODOS DE SECCIONES
    # ----------------------------------------------------------
    def _add_portada(self, p, beneficiaria, width, height):
        """Genera la portada del expediente de beneficiaria"""

        company = self.env.company
        y = height - inch  # margen superior inicial

        # === LOGO EMPRESA CENTRADO ===
        if company.logo:
            try:
                logo_data = base64.b64decode(company.logo)
                logo_image = ImageReader(BytesIO(logo_data))

                logo_width = 2.5 * inch
                logo_height = 2.5 * inch
                logo_x = (width - logo_width) / 2
                logo_y = height - 2.5 * inch

                p.drawImage(
                    logo_image,
                    logo_x,
                    logo_y,
                    width=logo_width,
                    height=logo_height,
                    preserveAspectRatio=True,
                    mask="auto",
                )
                y = logo_y - 0.8 * inch  # dejar espacio debajo del logo
            except Exception as e:
                print(f"[WARN] No se pudo agregar el logo: {e}")
                y = height - 2 * inch
        else:
            y = height - 2 * inch

        # === TÍTULO Y NOMBRE ===
        p.setFont("Helvetica-Bold", 18)
        p.drawCentredString(width / 2, y, "Expediente de Beneficiaria")
        y -= 40

        p.setFont("Helvetica", 14)
        p.drawCentredString(width / 2, y, beneficiaria.nombre_completo or "")
        y -= 60

        # === DESCRIPCIÓN (HTML → texto plano, centrada) ===
        descripcion_texto = ""
        if beneficiaria.descripcion:
            try:
                from odoo.tools import html2plaintext #type: ignore[import]
                descripcion_texto = html2plaintext(beneficiaria.descripcion).strip()
            except Exception:
                descripcion_texto = str(beneficiaria.descripcion or "").strip()

        if descripcion_texto:
            p.setFont("Helvetica", 11)

            # Convertir saltos de línea y limitar longitud para evitar desbordes
            lineas = descripcion_texto.split("\n")
            max_lineas = 8  # evita textos demasiado largos en portada

            for i, linea in enumerate(lineas[:max_lineas]):
                p.drawCentredString(width / 2, y, linea.strip())
                y -= 15  # espacio entre líneas

            y -= 30  # espacio después de la descripción
        else:
            y -= 40  # deja aire si no hay descripción


        # === FOTO FRONTAL ===
        if beneficiaria.foto_frontal:
            try:
                image_data = base64.b64decode(beneficiaria.foto_frontal)
                image = ImageReader(BytesIO(image_data))

                image_width = 2.8 * inch
                image_height = 2.8 * inch
                image_x = (width - image_width) / 2
                image_y = y - image_height - 20

                p.drawImage(
                    image,
                    image_x,
                    image_y,
                    width=image_width,
                    height=image_height,
                    preserveAspectRatio=True,
                    mask="auto",
                )

                # Marco gris suave
                p.setStrokeColorRGB(0.75, 0.75, 0.75)
                p.rect(image_x, image_y, image_width, image_height)

                # Leyenda bajo la foto
                p.setFont("Helvetica", 11)

                y = image_y - 60
            except Exception as e:
                print(f"[WARN] No se pudo agregar la foto frontal: {e}")
                y -= 80
        else:
            y -= 80  # deja espacio si no hay foto

        # === FOOTER INSTITUCIONAL ===
        self._add_footer(p, width, height)
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

    # ----------------------------------------------------------
    # Secciones de Datos
    # ----------------------------------------------------------
    def _add_section_datos_generales(self, p, beneficiaria, width, height):
        """Primera sección después de la portada: Datos Generales + Embarazo + Motivo de Egreso + Servicios"""

        p.setFont("Helvetica-Bold", 16)
        p.drawCentredString(width / 2, height - 80, "DATOS GENERALES DE LA BENEFICIARIA")

        # === Configuración visual ===
        y = height - 130
        line_height = 20
        section_spacing = 25
        subtitle_spacing = 20
        left_margin = inch
        col2_x = width / 2 + 0.5 * inch
        usable_width = (width / 2) - (1.5 * inch)  # ancho utilizable en cada columna

        # ---------------------------------------------------------------------
        # Funciones auxiliares
        # ---------------------------------------------------------------------
        def draw_field(x, label, value):
            nonlocal y
            if y < inch:
                self._add_footer(p, width, height)
                p.showPage()
                y = height - 100
                p.setFont("Helvetica-Bold", 16)
                p.drawCentredString(width / 2, height - 80, "DATOS GENERALES DE LA BENEFICIARIA (cont.)")
                y -= 40
                p.setFont("Helvetica", 11)
            p.drawString(x, y, f"{label}: {value or '-'}")
            y -= line_height

        def draw_field_col2(label, value):
            nonlocal y_col2
            if y_col2 < inch:
                self._add_footer(p, width, height)
                p.showPage()
                y_col2 = height - 100
                p.setFont("Helvetica-Bold", 16)
                p.drawCentredString(width / 2, height - 80, "DATOS GENERALES DE LA BENEFICIARIA (cont.)")
                y_col2 -= 40
                p.setFont("Helvetica", 11)
            p.drawString(col2_x, y_col2, f"{label}: {value or '-'}")
            y_col2 -= line_height

        # Función auxiliar para texto largo con salto automático
        def draw_wrapped_text(x, y_start, text, max_width):
            """Dibuja texto multilínea (ajuste automático al ancho disponible)."""

            p.setFont("Helvetica", 11)
            lines = []
            current_line = ""
            for word in text.split():
                if stringWidth(current_line + " " + word, "Helvetica", 11) <= max_width:
                    current_line += (" " if current_line else "") + word
                else:
                    lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)

            for line in lines:
                p.drawString(x, y_start, line.strip())
                y_start -= 15
            return y_start

        # ======================================================
        # COLUMNA IZQUIERDA → Datos Generales + Servicios
        # ======================================================
        p.setFont("Helvetica-Bold", 13)
        p.drawString(left_margin, y, "Datos Generales")
        y -= subtitle_spacing
        p.setFont("Helvetica", 11)

        draw_field(left_margin, "Nombre", beneficiaria.nombre)
        draw_field(left_margin, "Apellido paterno", beneficiaria.apellido_paterno)
        draw_field(left_margin, "Apellido materno", beneficiaria.apellido_materno)
        draw_field(left_margin, "CURP", beneficiaria.curp)
        draw_field(left_margin, "RFC", beneficiaria.rfc)
        draw_field(left_margin, "Fecha de nacimiento", str(beneficiaria.fecha_nacimiento or "-"))
        draw_field(left_margin, "Fecha de ingreso", str(beneficiaria.fecha_ingreso or "-"))
        draw_field(left_margin, "Edad al ingreso", beneficiaria.edad_ingreso)
        draw_field(left_margin, "Rango", beneficiaria.rango)
        draw_field(left_margin, "Centro de atención", getattr(beneficiaria.atention_center, "name", None))
        draw_field(left_margin, "Número de hijos", beneficiaria.numero_hijos)
        draw_field(left_margin, "Asignado a", getattr(beneficiaria.asignado_a_id, "name", None))
        draw_field(left_margin, "Referencia automática", beneficiaria.ref_auto)
        draw_field(left_margin, "Tipo de ayuda", beneficiaria.tipo_de_ayuda)
        if beneficiaria.tipo_de_ayuda == "otro":
            draw_field(left_margin, "Especificar otro", beneficiaria.tipo_de_ayuda_otro)

        # === SERVICIOS RECIBIDOS ===
        y -= section_spacing
        p.setFont("Helvetica-Bold", 13)
        p.drawString(left_margin, y, "Servicios Recibidos")
        y -= subtitle_spacing
        p.setFont("Helvetica", 11)

        servicios = []
        if beneficiaria.atencion_integral_embarazo:
            servicios.append("Atención integral embarazo")
        if beneficiaria.atencion_medica:
            servicios.append("Atención médica")
        if beneficiaria.atencion_psicologica:
            servicios.append("Atención psicológica")
        if beneficiaria.atencion_nutricional:
            servicios.append("Atención nutricional")
        if beneficiaria.apoyo_emocional:
            servicios.append("Apoyo emocional")
        if beneficiaria.apoyo_especie:
            servicios.append("Apoyo en especie")
        if beneficiaria.aistencia_legal_adopcion:
            servicios.append("Asistencia legal/adopción")
        if beneficiaria.centro_capacitacion_formacion:
            servicios.append("Centro de capacitación/formación")
        if beneficiaria.otro:
            detalle_otro = (
                f"Otro ({beneficiaria.otro_detalle_servicio})"
                if beneficiaria.otro_detalle_servicio
                else "Otro"
            )
            servicios.append(detalle_otro)

        if servicios:
            texto_servicios = ", ".join(servicios)
            y = draw_wrapped_text(left_margin, y, texto_servicios, usable_width)
            y -= 10
        else:
            p.setFont("Helvetica-Oblique", 10)
            p.drawString(left_margin, y, "No se registraron servicios recibidos.")
            y -= line_height

        # ======================================================
        # COLUMNA DERECHA → Datos de Embarazo, Egreso
        # ======================================================
        y_col2 = height - 130

        # === DATOS DE EMBARAZO ===
        p.setFont("Helvetica-Bold", 13)
        p.drawString(col2_x, y_col2, "Datos de Embarazo")
        y_col2 -= subtitle_spacing
        p.setFont("Helvetica", 11)

        draw_field_col2("FUM", str(beneficiaria.fum_time or "-"))
        draw_field_col2("Meses de embarazo", beneficiaria.meses_embarazo)
        draw_field_col2("Semanas de gestación", beneficiaria.semanas_gestacion)
        draw_field_col2("Fecha probable de parto", str(beneficiaria.fecha_probable_de_parto or "-"))

        # === HISTORIAL DE EMBARAZOS ===
        y_col2 -= section_spacing
        p.setFont("Helvetica-Bold", 12)
        p.drawString(col2_x, y_col2, "Historial de Embarazos")
        y_col2 -= subtitle_spacing
        p.setFont("Helvetica", 11)

        draw_field_col2("Cantidad de embarazos", beneficiaria.cantidad_embarazos)
        draw_field_col2("Hijos nacidos vivos", beneficiaria.cantidad_hijos_nacidos_vivos)
        draw_field_col2("Hijos nacidos muertos", beneficiaria.cantidad_hijos_nacidos_muertos)
        draw_field_col2("Abortos", beneficiaria.cantidad_abortos)

        # === MOTIVO DE EGRESO ===
        y_col2 -= section_spacing
        p.setFont("Helvetica-Bold", 13)
        p.drawString(col2_x, y_col2, "Motivo de Egreso")
        y_col2 -= subtitle_spacing
        p.setFont("Helvetica", 11)
        draw_field_col2("Motivo de egreso", getattr(beneficiaria, "motivo_de_egreso", None))
        if beneficiaria.motivo_de_egreso == "09":
            draw_field_col2("Otro motivo", beneficiaria.motivo_de_egreso_otro)
        draw_field_col2("Motivo de egreso post-parto", getattr(beneficiaria, "motivo_de_egreso_parto", None))
        if beneficiaria.motivo_de_egreso_parto == "07":
            draw_field_col2("Otro post-parto", beneficiaria.motivo_de_egreso_otro_post_parto)

        # === Footer ===
        self._add_footer(p, width, height)
        p.showPage()





    def _add_section_informacion_particular(self, p, beneficiaria, width, height):
        """Sección combinada: Información Particular Detallada + Residencia + Datos de Embarazo + Migración + Discapacidad + Servicios Recibidos"""

        p.setFont("Helvetica-Bold", 16)
        p.drawCentredString(width / 2, height - 80, "INFORMACIÓN PARTICULAR DETALLADA")

        # === Configuración visual ===
        y = height - 130
        line_height = 20
        section_spacing = 25
        subtitle_spacing = 20
        left_margin = inch
        col2_x = width / 2 + 0.5 * inch  # margen para segunda columna

        # ---------------------------------------------------------------------
        # Función auxiliar genérica para ambas columnas
        # ---------------------------------------------------------------------
        def draw_field(x, label, value):
            nonlocal y
            if y < inch:
                self._add_footer(p, width, height)
                p.showPage()
                y = height - 100
                p.setFont("Helvetica-Bold", 16)
                p.drawCentredString(width / 2, height - 80, "INFORMACIÓN PARTICULAR DETALLADA (cont.)")
                y -= 40
                p.setFont("Helvetica", 11)
            p.drawString(x, y, f"{label}: {value or '-'}")
            y -= line_height

        # ======================================================
        # COLUMNA IZQUIERDA → Datos personales y básicos
        # ======================================================

        # === DATOS DE CONTACTO ===
        p.setFont("Helvetica-Bold", 13)
        p.drawString(left_margin, y, "Datos de Contacto")
        y -= subtitle_spacing
        p.setFont("Helvetica", 11)
        draw_field(left_margin, "Correo", beneficiaria.correo)
        draw_field(left_margin, "Teléfono", beneficiaria.telefono)
        draw_field(left_margin, "Teléfono Celular", beneficiaria.telefono_celular)
        draw_field(left_margin, "¿Tiene red social?", "Sí" if beneficiaria.tiene_red_social else "No")

        if beneficiaria.tiene_red_social:
            y -= 5
            p.setFont("Helvetica-Bold", 12)
            p.drawString(left_margin, y, "Redes Sociales")
            y -= subtitle_spacing
            p.setFont("Helvetica", 11)
            draw_field(left_margin, getattr(beneficiaria, "tipo_red_social1", "Red social 1"), beneficiaria.red_social1)
            draw_field(left_margin, getattr(beneficiaria, "tipo_red_social2", "Red social 2"), beneficiaria.red_social2)

        # === DATOS DE NACIMIENTO ===
        y -= section_spacing
        p.setFont("Helvetica-Bold", 13)
        p.drawString(left_margin, y, "Datos de Nacimiento")
        y -= subtitle_spacing
        p.setFont("Helvetica", 11)
        draw_field(left_margin, "País de Nacimiento", getattr(beneficiaria.pais_nacimiento, "name", None))
        draw_field(left_margin, "Estado de Nacimiento", getattr(beneficiaria.estado_nacimiento, "name", None))
        draw_field(left_margin, "Ciudad de Nacimiento", beneficiaria.ciudad_nacimiento)

        # === NIVEL SOCIOECONÓMICO ===
        y -= section_spacing
        p.setFont("Helvetica-Bold", 13)
        p.drawString(left_margin, y, "Nivel Socioeconómico")
        y -= subtitle_spacing
        p.setFont("Helvetica", 11)
        draw_field(left_margin, "Grado de estudios", beneficiaria.grado_estudios)
        draw_field(left_margin, "Estado civil", beneficiaria.estado_civil)
        draw_field(left_margin, "Ocupación", beneficiaria.ocupacion)
        draw_field(left_margin, "Nivel económico", beneficiaria.nivel_economico)
        draw_field(left_margin, "Tipo de población", beneficiaria.tipo_poblacion)

        # === RELIGIÓN ===
        y -= section_spacing
        p.setFont("Helvetica-Bold", 13)
        p.drawString(left_margin, y, "Religión")
        y -= subtitle_spacing
        p.setFont("Helvetica", 11)
        draw_field(left_margin, "Religión", beneficiaria.religion)
        if beneficiaria.religion == "otro":
            draw_field(left_margin, "Especificar religión", beneficiaria.religion_otro)

        # ======================================================
        # COLUMNA DERECHA → Domicilio + Embarazo + Migración + Discapacidad + Servicios
        # ======================================================

        y_col2 = height - 130

        def draw_field_col2(label, value):
            nonlocal y_col2
            if y_col2 < inch:
                self._add_footer(p, width, height)
                p.showPage()
                y_col2 = height - 100
                p.setFont("Helvetica-Bold", 16)
                p.drawCentredString(width / 2, height - 80, "INFORMACIÓN PARTICULAR DETALLADA (cont.)")
                y_col2 -= 40
                p.setFont("Helvetica", 11)
            p.drawString(col2_x, y_col2, f"{label}: {value or '-'}")
            y_col2 -= line_height

        # === DOMICILIO ===
        p.setFont("Helvetica-Bold", 13)
        p.drawString(col2_x, y_col2, "Domicilio")
        y_col2 -= subtitle_spacing
        p.setFont("Helvetica", 11)

        draw_field_col2("País", getattr(beneficiaria.pais, "name", None))
        draw_field_col2("Estado", getattr(beneficiaria.estado, "name", None))
        draw_field_col2("Municipio", beneficiaria.municipio)
        draw_field_col2("Colonia", beneficiaria.colonia)
        draw_field_col2("Calle", beneficiaria.calle)
        draw_field_col2("Número exterior", beneficiaria.numero_exterior)
        draw_field_col2("Número interior", beneficiaria.numero_interior)
        draw_field_col2("Código postal", beneficiaria.codigo_postal)
        draw_field_col2("Referencia", beneficiaria.referencia_domicilio)

        # === MIGRACIÓN ===
        y_col2 -= section_spacing
        p.setFont("Helvetica-Bold", 13)
        p.drawString(col2_x, y_col2, "Migración")
        y_col2 -= subtitle_spacing
        p.setFont("Helvetica", 11)
        draw_field_col2("¿Migrante?", "Sí" if beneficiaria.migrante else "No")
        if beneficiaria.migrante:
            draw_field_col2("País de origen", beneficiaria.pais_de_origen)
            draw_field_col2("Motivo de migración", beneficiaria.motivo_migracion)
            draw_field_col2("Deseo de migrar nuevamente", beneficiaria.deseo_de_migrar)
        draw_field_col2("¿Pertenece a comunidad indígena?", "Sí" if beneficiaria.pertenece_a_una_comunidad else "No")
        if beneficiaria.pertenece_a_una_comunidad:
            draw_field_col2("Comunidad", beneficiaria.comunidad_indigena)
            draw_field_col2("Dialecto", beneficiaria.dialecto)
            draw_field_col2("Lengua materna", beneficiaria.lengua_materna)

        # === DISCAPACIDAD ===
        y_col2 -= section_spacing
        p.setFont("Helvetica-Bold", 13)
        p.drawString(col2_x, y_col2, "Discapacidad")
        y_col2 -= subtitle_spacing
        p.setFont("Helvetica", 11)
        draw_field_col2("¿Tiene discapacidad?", "Sí" if beneficiaria.discapacidad else "No")
        if beneficiaria.discapacidad:
            draw_field_col2("Tipo de discapacidad", beneficiaria.tipo_discapacidad)


        # === Footer ===
        self._add_footer(p, width, height)
        p.showPage()
        
    # ----------------------------------------------------------
    # Sección Canalización y Legal
    # ----------------------------------------------------------
    def _add_section_canalizacion_legal(self, p, beneficiaria, width, height):
        """Tercera sección: Canalización y Seguimiento Legal"""

        # === Verificar si hay datos ===
        campos_canalizacion = [
            beneficiaria.ingreso_por,
            beneficiaria.canalizacion,
            beneficiaria.canalizacion_otro,
            beneficiaria.nombre_canalizador,
            beneficiaria.cargo_canalizador,
            beneficiaria.numero_oficio_canalizacion,
        ]

        campos_legal = [
            beneficiaria.tiene_carpeta_investigacion,
            beneficiaria.NIC,
            beneficiaria.NUC,
            beneficiaria.fecha_investigacion,
            beneficiaria.lugar,
            beneficiaria.delito,
            beneficiaria.numero_oficio,
            beneficiaria.estatus_situacion_juridica,
            beneficiaria.persona_seguimiento_legal,
            beneficiaria.telefono_seguimiento_legal,
            beneficiaria.telefono2_seguimiento_legal,
            beneficiaria.correo_seguimiento_legal,
            beneficiaria.notas_seguimiento_legal,
        ]

        # Si no hay ningún dato en ninguna de las dos secciones, no generar página
        if not any(campos_canalizacion) and not any(campos_legal):
            return  # 🚫 Salimos sin generar la página

        # === Configuración visual ===
        p.setFont("Helvetica-Bold", 16)
        p.drawCentredString(width / 2, height - 80, "CANALIZACIÓN Y SEGUIMIENTO LEGAL")

        y_left = height - 130
        y_right = height - 130
        line_height = 20
        subtitle_spacing = 20
        left_margin = inch
        right_col_x = width / 2 + 0.5 * inch

        # Función auxiliar genérica
        def draw_field(x, y, label, value):
            if y < inch:
                self._add_footer(p, width, height)
                p.showPage()
                p.setFont("Helvetica-Bold", 16)
                p.drawCentredString(width / 2, height - 80, "CANALIZACIÓN Y SEGUIMIENTO LEGAL (cont.)")
                y = height - 100
                p.setFont("Helvetica", 11)
            p.drawString(x, y, f"{label}: {value or '-'}")
            return y - line_height

        # ======================================================
        # COLUMNA IZQUIERDA — CANALIZACIÓN
        # ======================================================
        p.setFont("Helvetica-Bold", 13)
        p.drawString(left_margin, y_left, "Canalización")
        y_left -= subtitle_spacing
        p.setFont("Helvetica", 11)

        y_left = draw_field(left_margin, y_left, "Ingreso por", beneficiaria.ingreso_por)
        y_left = draw_field(left_margin, y_left, "Canalización", beneficiaria.canalizacion)
        if beneficiaria.canalizacion == "otro":
            y_left = draw_field(left_margin, y_left, "Especificar canalización", beneficiaria.canalizacion_otro)
        y_left = draw_field(left_margin, y_left, "Nombre del canalizador", beneficiaria.nombre_canalizador)
        y_left = draw_field(left_margin, y_left, "Cargo del canalizador", beneficiaria.cargo_canalizador)
        y_left = draw_field(left_margin, y_left, "Número de oficio", beneficiaria.numero_oficio_canalizacion)

        # ======================================================
        # COLUMNA DERECHA — SEGUIMIENTO LEGAL
        # ======================================================
        p.setFont("Helvetica-Bold", 13)
        p.drawString(right_col_x, y_right, "Seguimiento Legal")
        y_right -= subtitle_spacing
        p.setFont("Helvetica", 11)

        y_right = draw_field(right_col_x, y_right, "¿Tiene carpeta de investigación?",
                            "Sí" if beneficiaria.tiene_carpeta_investigacion else "No")

        if beneficiaria.tiene_carpeta_investigacion:
            y_right = draw_field(right_col_x, y_right, "NIC", beneficiaria.NIC)
            y_right = draw_field(right_col_x, y_right, "NUC", beneficiaria.NUC)
            y_right = draw_field(right_col_x, y_right, "Fecha de investigación", beneficiaria.fecha_investigacion)
            y_right = draw_field(right_col_x, y_right, "Lugar", beneficiaria.lugar)
            y_right = draw_field(right_col_x, y_right, "Delito", beneficiaria.delito)
            y_right = draw_field(right_col_x, y_right, "Número de oficio", beneficiaria.numero_oficio)
            y_right = draw_field(right_col_x, y_right, "Persona seguimiento legal", beneficiaria.persona_seguimiento_legal)
            y_right = draw_field(right_col_x, y_right, "Teléfono 1", beneficiaria.telefono_seguimiento_legal)
            y_right = draw_field(right_col_x, y_right, "Teléfono 2", beneficiaria.telefono2_seguimiento_legal)
            y_right = draw_field(right_col_x, y_right, "Correo", beneficiaria.correo_seguimiento_legal)
            y_right = draw_field(right_col_x, y_right, "Notas", beneficiaria.notas_seguimiento_legal)

        y_right = draw_field(right_col_x, y_right, "Estatus / Situación jurídica", beneficiaria.estatus_situacion_juridica)

        # Footer
        self._add_footer(p, width, height)
        p.showPage()


    # ======================================================
    # Fotos
    # ======================================================

    def _add_section_fotos(self, p, beneficiaria, width, height):
        """Cuarta sección: Fotos de la beneficiaria"""

        # === Verificar si hay al menos una foto ===
        fotos = {
            "Foto Frontal": beneficiaria.foto_frontal,
            "Perfil Izquierdo": beneficiaria.foto_perfil_izquierdo,
            "Perfil Derecho": beneficiaria.foto_perfil_derecho,
            "Huellas Digitales": beneficiaria.foto_huellas,
        }

        if not any(fotos.values()):
            return  # 🚫 No hay ninguna imagen → no generamos la página

        # === Configuración general ===
        p.setFont("Helvetica-Bold", 16)
        p.drawCentredString(width / 2, height - 80, "FOTOGRAFÍAS DE LA BENEFICIARIA")

        y_start = height - 160
        image_width = 2.5 * inch
        image_height = 2.5 * inch
        x_margin = inch
        x_spacing = (width - 2 * x_margin - 2 * image_width) / 1  # espacio entre las 2 columnas
        y_spacing = 1.2 * inch  # espacio vertical entre filas

        # === Dibujar imágenes ===
        positions = [
            (x_margin, y_start),  # 1. Foto Frontal
            (x_margin + image_width + x_spacing, y_start),  # 2. Perfil Izquierdo
            (x_margin, y_start - image_height - y_spacing),  # 3. Perfil Derecho
            (x_margin + image_width + x_spacing, y_start - image_height - y_spacing),  # 4. Huellas
        ]

        p.setFont("Helvetica", 11)

        for (label, img_data), (x, y) in zip(fotos.items(), positions):
            if not img_data:
                continue  # si no hay imagen, saltar

            try:
                image_data = base64.b64decode(img_data)
                image_reader = ImageReader(BytesIO(image_data))
                p.drawImage(
                    image_reader,
                    x,
                    y - image_height,
                    width=image_width,
                    height=image_height,
                    preserveAspectRatio=True,
                    mask="auto",
                )
            except Exception as e:
                print(f"[WARN] No se pudo procesar {label}: {e}")
                continue

            # Título centrado debajo de cada imagen
            label_x_center = x + image_width / 2
            p.drawCentredString(label_x_center, y - image_height - 15, label)

        # Footer institucional
        self._add_footer(p, width, height)
        p.showPage()


    def _add_section_acompanante_y_referencias(self, p, beneficiaria, width, height):
        """Sección: Acompañante y Referencias (todo en una sola columna)"""

        # Verificar si hay información relevante
        tiene_acompanante = bool(
            beneficiaria.acompanante or beneficiaria.acompanante_nombre or beneficiaria.acompanante_parentesco
        )
        tiene_referencias = bool(
            beneficiaria.nombre_referencia1
            or beneficiaria.telefono_referencia1
            or beneficiaria.parentesco_referencia1
            or beneficiaria.nombre_referencia2
            or beneficiaria.telefono_referencia2
            or beneficiaria.parentesco_referencia2
        )

        # Si no hay nada que mostrar, omitir la página
        if not (tiene_acompanante or tiene_referencias):
            return

        # === Configuración visual ===
        p.setFont("Helvetica-Bold", 16)
        p.drawCentredString(width / 2, height - 80, "ACOMPAÑANTE Y REFERENCIAS")

        y = height - 130
        line_height = 20
        section_spacing = 30
        subtitle_spacing = 20
        left_margin = inch

        # === Función auxiliar ===
        def draw_field(label, value):
            """Dibuja un campo simple con salto de línea automático si es necesario"""
            nonlocal y
            if y < inch:
                self._add_footer(p, width, height)
                p.showPage()
                y = height - 100
                p.setFont("Helvetica-Bold", 16)
                p.drawCentredString(width / 2, height - 80, "ACOMPAÑANTE Y REFERENCIAS (cont.)")
                y -= 40
                p.setFont("Helvetica", 11)

            text = f"{label}: {value or '-'}"
            max_width = width - (2 * inch)
            words = text.split()
            line = ""

            for word in words:
                if stringWidth(line + " " + word, "Helvetica", 11) <= max_width:
                    line += (" " if line else "") + word
                else:
                    p.drawString(left_margin, y, line.strip())
                    y -= line_height
                    line = word
            if line:
                p.drawString(left_margin, y, line.strip())
                y -= line_height

        # ======================================================
        # SECCIÓN: ACOMPAÑANTE
        # ======================================================
        if tiene_acompanante:
            p.setFont("Helvetica-Bold", 13)
            p.drawString(left_margin, y, "Acompañante")
            y -= subtitle_spacing
            p.setFont("Helvetica", 11)

            draw_field("¿Tiene acompañante?", "Sí" if beneficiaria.acompanante else "No")
            if beneficiaria.acompanante:
                draw_field("Nombre", beneficiaria.acompanante_nombre)
                draw_field("Parentesco", beneficiaria.acompanante_parentesco)

            y -= section_spacing

        # ======================================================
        # SECCIÓN: CONTACTOS DE EMERGENCIA
        # ======================================================
        if tiene_referencias:
            p.setFont("Helvetica-Bold", 13)
            p.drawString(left_margin, y, "Contactos de Emergencia")
            y -= subtitle_spacing
            p.setFont("Helvetica", 11)

            # Primer contacto
            draw_field("Nombre (Referencia 1)", beneficiaria.nombre_referencia1)
            draw_field("Teléfono", beneficiaria.telefono_referencia1)
            draw_field("Parentesco", beneficiaria.parentesco_referencia1)

            y -= section_spacing

            # Segundo contacto
            draw_field("Nombre (Referencia 2)", beneficiaria.nombre_referencia2)
            draw_field("Teléfono", beneficiaria.telefono_referencia2)
            draw_field("Parentesco", beneficiaria.parentesco_referencia2)

        # === Footer ===
        self._add_footer(p, width, height)
        p.showPage()


    def _add_section_familiares(self, p, beneficiaria, width, height):
        """Sección: Familiares (Padre, Madre, Tutor, Hermanos)"""

        # === Verificar si hay datos relevantes ===
        tiene_padre = bool(
            beneficiaria.padre_nombre
            or beneficiaria.telefono_padre
            or beneficiaria.direccion_padre
        )
        tiene_madre = bool(
            beneficiaria.madre_nombre
            or beneficiaria.telefono_madre
            or beneficiaria.direccion_madre
        )
        tiene_tutor = bool(
            beneficiaria.tutor_nombre
            or beneficiaria.tutor_telefono
            or beneficiaria.tutor_direccion
        )
        tiene_hermanos = bool(beneficiaria.hermanos_ids)

        if not (tiene_padre or tiene_madre or tiene_tutor or tiene_hermanos):
            return  # No generar la página

        # === Configuración visual ===
        p.setFont("Helvetica-Bold", 16)
        p.drawCentredString(width / 2, height - 80, "FAMILIARES")

        y_left = height - 130
        y_right = height - 130
        line_height = 20
        section_spacing = 30
        subtitle_spacing = 20
        left_margin = inch
        col2_x = width / 2 + 0.5 * inch

        # === Funciones auxiliares ===
        def draw_field_left(label, value):
            nonlocal y_left
            if y_left < inch:
                self._add_footer(p, width, height)
                p.showPage()
                y_left = height - 100
                y_right = height - 100
                p.setFont("Helvetica-Bold", 16)
                p.drawCentredString(width / 2, height - 80, "FAMILIARES (cont.)")
                y_left -= 40
                y_right -= 40
                p.setFont("Helvetica", 11)

            text = f"{label}: {value or '-'}"
            max_width = (width / 2) - (1.5 * inch)
            words = text.split()
            line = ""

            for word in words:
                if stringWidth(line + " " + word, "Helvetica", 11) <= max_width:
                    line += (" " if line else "") + word
                else:
                    p.drawString(left_margin, y_left, line.strip())
                    y_left -= line_height
                    line = word
            if line:
                p.drawString(left_margin, y_left, line.strip())
                y_left -= line_height

        def draw_field_right(label, value):
            nonlocal y_right

            if y_right < inch:
                self._add_footer(p, width, height)
                p.showPage()
                y_left = height - 100
                y_right = height - 100
                p.setFont("Helvetica-Bold", 16)
                p.drawCentredString(width / 2, height - 80, "FAMILIARES (cont.)")
                y_left -= 40
                y_right -= 40
                p.setFont("Helvetica", 11)

            text = f"{label}: {value or '-'}"
            max_width = (width / 2) - (1.5 * inch)
            words = text.split()
            line = ""

            for word in words:
                if stringWidth(line + " " + word, "Helvetica", 11) <= max_width:
                    line += (" " if line else "") + word
                else:
                    p.drawString(col2_x, y_right, line.strip())
                    y_right -= line_height
                    line = word
            if line:
                p.drawString(col2_x, y_right, line.strip())
                y_right -= line_height

        # ======================================================
        # COLUMNA IZQUIERDA → PADRE, TUTOR, HERMANOS
        # ======================================================
        if tiene_padre:
            p.setFont("Helvetica-Bold", 13)
            p.drawString(left_margin, y_left, "Padre")
            y_left -= subtitle_spacing
            p.setFont("Helvetica", 11)

            draw_field_left("Nombre", beneficiaria.padre_nombre)
            draw_field_left("Tiene relación", "Sí" if beneficiaria.tiene_relacion_padre else "No")
            draw_field_left("Dirección", beneficiaria.direccion_padre)
            draw_field_left("Teléfono", beneficiaria.telefono_padre)
            draw_field_left("Está vivo", "Sí" if beneficiaria.esta_vivo_padre else "No")

            y_left -= section_spacing

        if tiene_tutor:
            p.setFont("Helvetica-Bold", 13)
            p.drawString(left_margin, y_left, "Tutor")
            y_left -= subtitle_spacing
            p.setFont("Helvetica", 11)

            draw_field_left("Nombre", beneficiaria.tutor_nombre)
            draw_field_left("Dirección", beneficiaria.tutor_direccion)
            draw_field_left("Teléfono", beneficiaria.tutor_telefono)
            draw_field_left("Parentesco", beneficiaria.tutor_parentesco)
            draw_field_left("Está vivo", "Sí" if beneficiaria.tutor_esta_vivo else "No")

            y_left -= section_spacing

        # ======================================================
        # COLUMNA DERECHA → MADRE
        # ======================================================
        if tiene_madre:
            p.setFont("Helvetica-Bold", 13)
            p.drawString(col2_x, y_right, "Madre")
            y_right -= subtitle_spacing
            p.setFont("Helvetica", 11)

            draw_field_right("Nombre", beneficiaria.madre_nombre)
            draw_field_right("Tiene relación", "Sí" if beneficiaria.tiene_relacion_madre else "No")
            draw_field_right("Dirección", beneficiaria.direccion_madre)
            draw_field_right("Teléfono", beneficiaria.telefono_madre)
            draw_field_right("Está viva", "Sí" if beneficiaria.esta_vivo_madre else "No")

            y_right -= section_spacing

        # ======================================================
        # HERMANOS → lista debajo (columna izquierda)
        # ======================================================
        if tiene_hermanos:
            y_left = min(y_left, y_right) - 20  # para bajar debajo de ambas columnas
            p.setFont("Helvetica-Bold", 13)
            p.drawString(left_margin, y_left, "Hermanos")
            y_left -= subtitle_spacing
            p.setFont("Helvetica", 11)

            draw_field_left("¿Tiene hermanos?", "Sí" if beneficiaria.tiene_hermanos else "No")
            y_left -= 5

            for idx, hermano in enumerate(beneficiaria.hermanos_ids, start=1):
                if y_left < inch + 40:
                    self._add_footer(p, width, height)
                    p.showPage()
                    y_left = height - 100
                    p.setFont("Helvetica-Bold", 16)
                    p.drawCentredString(width / 2, height - 80, "FAMILIARES (cont.)")
                    y_left -= 40
                    p.setFont("Helvetica", 11)

                p.setFont("Helvetica-Bold", 11)
                p.drawString(left_margin, y_left, f"Hermano {idx}:")
                y_left -= 15
                p.setFont("Helvetica", 11)
                draw_field_left("Nombre", hermano.nombre)
                draw_field_left("Teléfono", hermano.telefono)
                draw_field_left("Tienen relación", "Sí" if hermano.tienen_relacion else "No")
                y_left -= 10

        # === Footer ===
        self._add_footer(p, width, height)
        p.showPage()


    def _add_section_hijos(self, p, beneficiaria, width, height):
        """Sección: Hijos (lista enumerada + documentos asociados)"""

        # === Verificar si hay datos ===
        if not beneficiaria.hijos_ids:
            return  # No generar la página si no hay hijos

        # === Configuración visual ===
        p.setFont("Helvetica-Bold", 16)
        p.drawCentredString(width / 2, height - 80, "HIJOS")

        y = height - 130
        line_height = 20
        section_spacing = 30
        subtitle_spacing = 20
        left_margin = inch

        # === Función auxiliar para escribir texto largo ===
        def draw_field(label, value):
            nonlocal y
            if y < inch:
                # salto de página
                self._add_footer(p, width, height)
                p.showPage()
                y = height - 100
                p.setFont("Helvetica-Bold", 16)
                p.drawCentredString(width / 2, height - 80, "HIJOS (cont.)")
                y -= 40
                p.setFont("Helvetica", 11)

            text = f"{label}: {value or '-'}"
            max_width = width - (2 * inch)
            words = text.split()
            line = ""

            for word in words:
                if stringWidth(line + " " + word, "Helvetica", 11) <= max_width:
                    line += (" " if line else "") + word
                else:
                    p.drawString(left_margin, y, line.strip())
                    y -= line_height
                    line = word
            if line:
                p.drawString(left_margin, y, line.strip())
                y -= line_height

        # ======================================================
        # SECCIÓN DE HIJOS
        # ======================================================
        p.setFont("Helvetica-Bold", 13)
        p.drawString(left_margin, y, "Hijos")
        y -= subtitle_spacing
        p.setFont("Helvetica", 11)

        for idx, hijo in enumerate(beneficiaria.hijos_ids, start=1):
            if y < inch + 40:
                self._add_footer(p, width, height)
                p.showPage()
                y = height - 100
                p.setFont("Helvetica-Bold", 16)
                p.drawCentredString(width / 2, height - 80, "HIJOS (cont.)")
                y -= 40
                p.setFont("Helvetica", 11)

            # === Datos del hijo ===
            p.setFont("Helvetica-Bold", 11)
            p.drawString(left_margin, y, f"Hijo {idx}:")
            y -= 15
            p.setFont("Helvetica", 11)

            draw_field("Nombre", hijo.nombre)
            draw_field("Edad", hijo.edad)
            draw_field("Nivel de estudios", hijo.nivel_estudios)
            draw_field("Vive con ella", "Sí" if hijo.vive_con_ella else "No")
            draw_field("La acompaña", "Sí" if hijo.la_acompana else "No")
            draw_field("Responsable", hijo.responsable)
            draw_field("Escuela", hijo.escuela)

            # === Documentos asociados ===
            documentos = self.env["beneficiarias.documento"].search([
                ("hijo_id", "=", hijo.id),
                ("tipo_relacion", "=", "hijo")
            ])

            if documentos:
                p.setFont("Helvetica-Bold", 11)
                p.drawString(left_margin + 10, y, "Documentos asociados:")
                y -= line_height

                p.setFont("Helvetica", 11)
                for doc in documentos:
                    doc_name = doc.name or doc.nombre_archivo or "(Sin nombre)"
                    draw_field("-", doc_name)
            else:
                p.setFont("Helvetica-Oblique", 11)
                p.drawString(left_margin + 10, y, "No hay documentos asociados.")
                y -= line_height

            y -= section_spacing  # espacio entre hijos

        # === Footer final ===
        self._add_footer(p, width, height)
        p.showPage()

    def _add_section_relacion_padre(self, p, beneficiaria, width, height):
        """Sección: Relación con el Padre del Bebé"""

        # === Verificar si hay información relevante ===
        campos = [
            beneficiaria.nombre_padre,
            beneficiaria.edad_padre,
            beneficiaria.relacion_con_padre,
            beneficiaria.padre_sabe_de_su_embarazo,
            beneficiaria.padre_sera_notificado,
            beneficiaria.padre_ha_dado_apoyo,
            beneficiaria.estado_civil_padre,
            beneficiaria.padre_ocupacion,
            beneficiaria.padre_grado_maximo_estudios,
            beneficiaria.padre_tiene_adiccion,
            beneficiaria.estatura_padre,
            beneficiaria.complexion_padre,
            beneficiaria.numero_hijos_padre,
            beneficiaria.numero_hijos_padre_con_beneficiaria,
            beneficiaria.padre_vive_con_beneficiaria,
            beneficiaria.origen_padre,
            beneficiaria.antecendentes_medicos_padre,
            beneficiaria.en_caso_de_haber_migrado_padre,
            beneficiaria.padre_pais_migracion,
            beneficiaria.lugar_residencia_padre,
        ]
        if not any(campos):
            return  # No generar página si no hay datos

        # === Configuración visual ===
        p.setFont("Helvetica-Bold", 16)
        p.drawCentredString(width / 2, height - 80, "RELACIÓN CON EL PADRE DEL BEBÉ")

        y = height - 130
        line_height = 20
        subtitle_spacing = 20
        left_margin = inch

        # === Función auxiliar ===
        def draw_field(label, value):
            nonlocal y
            if y < inch:
                self._add_footer(p, width, height)
                p.showPage()
                y = height - 100
                p.setFont("Helvetica-Bold", 16)
                p.drawCentredString(width / 2, height - 80, "RELACIÓN CON EL PADRE DEL BEBÉ (cont.)")
                y -= 40
                p.setFont("Helvetica", 11)
            p.drawString(left_margin, y, f"{label}: {value or '-'}")
            y -= line_height

        # ======================================================
        # SECCIÓN PRINCIPAL
        # ======================================================
        p.setFont("Helvetica-Bold", 13)
        p.drawString(left_margin, y, "Datos del Padre")
        y -= subtitle_spacing
        p.setFont("Helvetica", 11)

        draw_field("Nombre", self._safe_value(beneficiaria.nombre_padre))
        draw_field("Edad", self._safe_value(beneficiaria.edad_padre))
        draw_field("Relación con el padre", self._safe_value(beneficiaria.relacion_con_padre))
        if beneficiaria.relacion_con_padre == "otro":
            draw_field("Especificar relación", self._safe_value(beneficiaria.relacion_con_padre_otro))

        draw_field("¿El padre sabe del embarazo?", "Sí" if beneficiaria.padre_sabe_de_su_embarazo else "No")
        draw_field("¿Será notificado?", "Sí" if beneficiaria.padre_sera_notificado else "No")
        draw_field("¿Ha dado apoyo?", "Sí" if beneficiaria.padre_ha_dado_apoyo else "No")
        draw_field("Estado civil", self._safe_value(beneficiaria.estado_civil_padre))
        draw_field("Ocupación", self._safe_value(beneficiaria.padre_ocupacion))
        draw_field("Grado máximo de estudios", self._safe_value(beneficiaria.padre_grado_maximo_estudios))

        draw_field("¿Tiene alguna adicción?", "Sí" if beneficiaria.padre_tiene_adiccion else "No")
        if beneficiaria.padre_tiene_adiccion:
            draw_field("Detalles de la adicción", self._safe_value(beneficiaria.padre_tiene_adiccion_detalle))

        draw_field("Estatura", self._safe_value(beneficiaria.estatura_padre))
        draw_field("Complexión", self._safe_value(beneficiaria.complexion_padre))
        draw_field("Número de hijos (totales)", self._safe_value(beneficiaria.numero_hijos_padre))
        draw_field("Hijos con la beneficiaria", self._safe_value(beneficiaria.numero_hijos_padre_con_beneficiaria))
        draw_field("¿Vive con la beneficiaria?", "Sí" if beneficiaria.padre_vive_con_beneficiaria else "No")
        draw_field("Origen del padre", self._safe_value(beneficiaria.origen_padre))
        draw_field("Antecedentes médicos", self._safe_value(beneficiaria.antecendentes_medicos_padre))
        draw_field("¿Ha migrado?", "Sí" if beneficiaria.en_caso_de_haber_migrado_padre else "No")
        if beneficiaria.en_caso_de_haber_migrado_padre:
            draw_field("País de migración", self._safe_value(beneficiaria.padre_pais_migracion))
        draw_field("Lugar de residencia", self._safe_value(beneficiaria.lugar_residencia_padre))

        # === Footer ===
        self._add_footer(p, width, height)
        p.showPage()


    def _add_section_datos_violencia(self, p, beneficiaria, width, height):
        """Sección: Datos de Violencia"""

        # === Verificar si hay datos relevantes ===
        campos = [
            beneficiaria.violacion,
            beneficiaria.violencia_intrafamiliar,
            beneficiaria.quien_fue_el_agresor,
            beneficiaria.tipo_violencia_fisica,
            beneficiaria.tipo_violencia_psicologica,
            beneficiaria.tipo_violencia_sexual,
            beneficiaria.tipo_violencia_economica,
            beneficiaria.tipo_violencia_patrimonial,
            beneficiaria.tipo_violencia_otro_seleccion,
            beneficiaria.tipo_violencia_otro,
            beneficiaria.educacion_sexual,
            beneficiaria.educacion_sexual_detalle,
            beneficiaria.embarazo_actual_consecuencia_de_violacion,
            beneficiaria.ha_iniciado_carpeta_investigacion,
            beneficiaria.carpeta_investigacion_numero,
            beneficiaria.carpeta_investigacion_fecha,
            beneficiaria.carpeta_investigacion_lugar,
        ]
        if not any(campos):
            return  # No generar sección si no hay datos

        # === Configuración visual ===
        p.setFont("Helvetica-Bold", 16)
        p.drawCentredString(width / 2, height - 80, "DATOS DE VIOLENCIA")

        y = height - 130
        line_height = 20
        section_spacing = 30
        left_margin = inch

        def draw_field(label, value):
            nonlocal y
            if y < inch:
                self._add_footer(p, width, height)
                p.showPage()
                y = height - 100
                p.setFont("Helvetica-Bold", 16)
                p.drawCentredString(width / 2, height - 80, "DATOS DE VIOLENCIA (cont.)")
                y -= 40
                p.setFont("Helvetica", 11)
            p.drawString(left_margin, y, f"{label}: {self._safe_value(value)}")
            y -= line_height

        # ======================================================
        # SECCIÓN 1: Tipos de violencia
        # ======================================================
        p.setFont("Helvetica-Bold", 13)
        p.drawString(left_margin, y, "Tipo de Violencia Sufrida")
        y -= 25
        p.setFont("Helvetica", 11)

        draw_field("¿Ha sido víctima de violación?", "Sí" if beneficiaria.violacion else "No")
        draw_field("¿Ha sufrido violencia intrafamiliar?", "Sí" if beneficiaria.violencia_intrafamiliar else "No")

        if beneficiaria.quien_fue_el_agresor:
            draw_field("¿Quién fue el agresor?", beneficiaria.quien_fue_el_agresor)

        tipos = []
        if beneficiaria.tipo_violencia_fisica:
            tipos.append("Física")
        if beneficiaria.tipo_violencia_psicologica:
            tipos.append("Psicológica")
        if beneficiaria.tipo_violencia_sexual:
            tipos.append("Sexual")
        if beneficiaria.tipo_violencia_economica:
            tipos.append("Económica")
        if beneficiaria.tipo_violencia_patrimonial:
            tipos.append("Patrimonial")
        if beneficiaria.tipo_violencia_otro_seleccion:
            tipos.append("Otro")

        draw_field("Tipos de violencia", ", ".join(tipos) if tipos else "Ninguno especificado")
        if beneficiaria.tipo_violencia_otro:
            draw_field("Otro tipo de violencia", beneficiaria.tipo_violencia_otro)
        draw_field("¿El embarazo actual es consecuencia de una violación?", 
            "Sí" if beneficiaria.embarazo_actual_consecuencia_de_violacion else "No")

        y -= section_spacing

        # ======================================================
        # SECCIÓN 2: Educación sexual y consecuencias
        # ======================================================
        p.setFont("Helvetica-Bold", 13)
        p.drawString(left_margin, y, "Educación Sexual y Consecuencias")
        y -= 25
        p.setFont("Helvetica", 11)

        draw_field("¿Ha recibido educación sexual?", "Sí" if beneficiaria.educacion_sexual else "No")
        if beneficiaria.educacion_sexual_detalle:
            draw_field("¿Quién la brindó y dónde?", beneficiaria.educacion_sexual_detalle)

        y -= section_spacing

        # ======================================================
        # SECCIÓN 3: Carpeta de investigación
        # ======================================================
        p.setFont("Helvetica-Bold", 13)
        p.drawString(left_margin, y, "Carpeta de Investigación")
        y -= 25
        p.setFont("Helvetica", 11)

        draw_field("¿Ha iniciado carpeta de investigación?", "Sí" if beneficiaria.ha_iniciado_carpeta_investigacion else "No")

        if beneficiaria.ha_iniciado_carpeta_investigacion:
            draw_field("Número de carpeta", beneficiaria.carpeta_investigacion_numero)
            draw_field("Fecha", str(beneficiaria.carpeta_investigacion_fecha or "-"))
            draw_field("Lugar", beneficiaria.carpeta_investigacion_lugar)

        # === Footer ===
        self._add_footer(p, width, height)
        p.showPage()

    def _add_section_antecedentes_medicos(self, p, beneficiaria, width, height):
        """Sección: Antecedentes Médicos"""

        campos = [
            beneficiaria.antecedentes_medicos,
            beneficiaria.enfermedades_cronicas,
            beneficiaria.alergias,
            beneficiaria.medicamentos_actuales,
            beneficiaria.cirugias_previas,
            beneficiaria.vacunas,
            beneficiaria.tipo_sangre,
            beneficiaria.enfermedades_familiares,
            beneficiaria.antecedentes_quirurgicos,
            beneficiaria.tiene_donador,
            beneficiaria.donador_nombre,
            beneficiaria.donador_telefono,
            beneficiaria.donador_relacion,
        ]

        if not any(campos):
            return  # no hay nada que mostrar

        # === Encabezado principal ===
        p.setFont("Helvetica-Bold", 16)
        p.drawCentredString(width / 2, height - 80, "ANTECEDENTES MÉDICOS")

        y = height - 130
        line_height = 20
        section_spacing = 30
        left_margin = inch

        def draw_field(label, value):
            nonlocal y
            if y < inch:
                self._add_footer(p, width, height)
                p.showPage()
                y = height - 100
                p.setFont("Helvetica-Bold", 16)
                p.drawCentredString(width / 2, height - 80, "ANTECEDENTES MÉDICOS (cont.)")
                y -= 40
                p.setFont("Helvetica", 11)
            p.drawString(left_margin, y, f"{label}: {self._safe_value(value)}")
            y -= line_height

        # ======================================================
        # SECCIÓN 1: Historial médico general
        # ======================================================
        p.setFont("Helvetica-Bold", 13)
        p.drawString(left_margin, y, "Historial Médico General")
        y -= 25
        p.setFont("Helvetica", 11)

        draw_field("Antecedentes médicos", beneficiaria.antecedentes_medicos)
        draw_field("Enfermedades crónicas", beneficiaria.enfermedades_cronicas)
        draw_field("Alergias", beneficiaria.alergias)
        draw_field("Medicamentos actuales", beneficiaria.medicamentos_actuales)
        draw_field("Cirugías previas", beneficiaria.cirugias_previas)
        draw_field("Vacunas", beneficiaria.vacunas)
        draw_field("Tipo de sangre", dict(beneficiaria._fields["tipo_sangre"].selection).get(beneficiaria.tipo_sangre, "-"))

        y -= section_spacing

        # ======================================================
        # SECCIÓN 2: Antecedentes familiares y quirúrgicos
        # ======================================================
        p.setFont("Helvetica-Bold", 13)
        p.drawString(left_margin, y, "Antecedentes Familiares y Quirúrgicos")
        y -= 25
        p.setFont("Helvetica", 11)

        draw_field("Enfermedades familiares", beneficiaria.enfermedades_familiares)
        draw_field("Antecedentes quirúrgicos", beneficiaria.antecedentes_quirurgicos)

        y -= section_spacing

        # ======================================================
        # SECCIÓN 3: Donador de sangre
        # ======================================================
        p.setFont("Helvetica-Bold", 13)
        p.drawString(left_margin, y, "Donador de Sangre")
        y -= 25
        p.setFont("Helvetica", 11)

        draw_field("¿Tiene donador?", "Sí" if beneficiaria.tiene_donador else "No")

        if beneficiaria.tiene_donador:
            draw_field("Nombre del donador", beneficiaria.donador_nombre)
            draw_field("Teléfono del donador", beneficiaria.donador_telefono)
            draw_field("Relación con el donador", beneficiaria.donador_relacion)

        # === Footer ===
        self._add_footer(p, width, height)
        p.showPage()

    def _add_section_traslados(self, p, beneficiaria, width, height):
        """Sección: Traslados de la Beneficiaria"""
        if not beneficiaria.traslado_ids:
            return

        p.setFont("Helvetica-Bold", 16)
        p.drawCentredString(width / 2, height - 80, "TRASLADOS")

        y = height - 130
        line_height = 20
        left_margin = inch

        def draw_field(label, value):
            nonlocal y
            if y < inch:
                self._add_footer(p, width, height)
                p.showPage()
                y = height - 100
                p.setFont("Helvetica-Bold", 16)
                p.drawCentredString(width / 2, height - 80, "TRASLADOS (cont.)")
                y -= 40
                p.setFont("Helvetica", 11)
            p.drawString(left_margin, y, f"{label}: {self._safe_value(value)}")
            y -= line_height

        for idx, traslado in enumerate(beneficiaria.traslado_ids, start=1):
            if y < inch + 40:
                self._add_footer(p, width, height)
                p.showPage()
                y = height - 100
                p.setFont("Helvetica-Bold", 16)
                p.drawCentredString(width / 2, height - 80, "TRASLADOS (cont.)")
                y -= 40
                p.setFont("Helvetica", 11)

            p.setFont("Helvetica-Bold", 12)
            p.drawString(left_margin, y, f"Traslado {idx}:")
            y -= 15
            p.setFont("Helvetica", 11)

            draw_field("Fecha", traslado.fecha_traslado)
            draw_field("Destino", traslado.ubicacion_destino)
            draw_field("Motivo", traslado.motivo_traslado)
            draw_field("Estado", traslado.estado)
            y -= 10

        self._add_footer(p, width, height)
        p.showPage()


    def _add_section_talleres(self, p, beneficiaria, width, height):
        """Sección: Talleres a los que asistió la beneficiaria"""
        if not beneficiaria.taller_ids:
            return

        p.setFont("Helvetica-Bold", 16)
        p.drawCentredString(width / 2, height - 80, "TALLERES")

        y = height - 130
        line_height = 20
        left_margin = inch

        def draw_field(label, value):
            nonlocal y
            if y < inch:
                self._add_footer(p, width, height)
                p.showPage()
                y = height - 100
                p.setFont("Helvetica-Bold", 16)
                p.drawCentredString(width / 2, height - 80, "TALLERES (cont.)")
                y -= 40
                p.setFont("Helvetica", 11)
            p.drawString(left_margin, y, f"{label}: {self._safe_value(value)}")
            y -= line_height

        for idx, taller in enumerate(beneficiaria.taller_ids, start=1):
            if y < inch + 40:
                self._add_footer(p, width, height)
                p.showPage()
                y = height - 100
                p.setFont("Helvetica-Bold", 16)
                p.drawCentredString(width / 2, height - 80, "TALLERES (cont.)")
                y -= 40
                p.setFont("Helvetica", 11)

            p.setFont("Helvetica-Bold", 12)
            p.drawString(left_margin, y, f"Taller {idx}:")
            y -= 15
            p.setFont("Helvetica", 11)

            draw_field("Nombre del taller", taller.name_taller)
            draw_field("Instructor", taller.instructor)
            draw_field("Fecha", taller.fecha)
            draw_field("Duración (horas)", taller.num_horas)
            draw_field("Comentarios", taller.comentarios)
            y -= 10

        self._add_footer(p, width, height)
        p.showPage()


    def _add_section_valoraciones(self, p, beneficiaria, width, height):
        """Sección: Valoraciones realizadas a la beneficiaria"""
        if not beneficiaria.valoracion_ids:
            return

        p.setFont("Helvetica-Bold", 16)
        p.drawCentredString(width / 2, height - 80, "VALORACIONES")

        y = height - 130
        line_height = 20
        left_margin = inch

        def draw_field(label, value):
            nonlocal y
            if y < inch:
                self._add_footer(p, width, height)
                p.showPage()
                y = height - 100
                p.setFont("Helvetica-Bold", 16)
                p.drawCentredString(width / 2, height - 80, "VALORACIONES (cont.)")
                y -= 40
                p.setFont("Helvetica", 11)
            p.drawString(left_margin, y, f"{label}: {self._safe_value(value)}")
            y -= line_height

        for idx, valoracion in enumerate(beneficiaria.valoracion_ids, start=1):
            if y < inch + 60:
                self._add_footer(p, width, height)
                p.showPage()
                y = height - 100
                p.setFont("Helvetica-Bold", 16)
                p.drawCentredString(width / 2, height - 80, "VALORACIONES (cont.)")
                y -= 40
                p.setFont("Helvetica", 11)

            p.setFont("Helvetica-Bold", 12)
            p.drawString(left_margin, y, f"Valoración {idx}:")
            y -= 15
            p.setFont("Helvetica", 11)

            # Campos principales
            draw_field("Categoría", dict(valoracion._fields["categoria"].selection).get(valoracion.categoria, "-"))
            draw_field("Fecha de realización", valoracion.fecha_realizacion)
            draw_field("Elaborado por", valoracion.elaborado_por)

            # Archivo principal
            archivo = "Sí (adjunto)" if valoracion.valoracion_archivo else "No"
            draw_field("Archivo de valoración", archivo)

            # Documentos adicionales asociados
            if valoracion.documentos_ids:
                y -= 5
                p.setFont("Helvetica-Bold", 11)
                p.drawString(left_margin, y, "Documentos vinculados:")
                y -= 15
                p.setFont("Helvetica", 10)
                for doc in valoracion.documentos_ids:
                    if y < inch + 40:
                        self._add_footer(p, width, height)
                        p.showPage()
                        y = height - 100
                        p.setFont("Helvetica-Bold", 16)
                        p.drawCentredString(width / 2, height - 80, "VALORACIONES (cont.)")
                        y -= 40
                        p.setFont("Helvetica", 10)
                    p.drawString(left_margin + 15, y, f"- {self._safe_value(doc.name)}")
                    y -= line_height
                y -= 10

            y -= 10

        # Al final, imprime total de valoraciones
        p.setFont("Helvetica-Bold", 11)
        p.drawString(left_margin, y - 10, f"Total de valoraciones: {len(beneficiaria.valoracion_ids)}")

        self._add_footer(p, width, height)
        p.showPage()

    def _add_section_parto_y_bebe(self, p, beneficiaria, width, height):
        """Sección combinada: Datos del parto (de la beneficiaria) + Datos del bebé (en 2 columnas)."""
        tiene_parto = any([
            beneficiaria.fecha_egreso_hospital,
            beneficiaria.hospital_parto,
            beneficiaria.parto_multiple,
        ])
        tiene_bebes = bool(beneficiaria.bebe_ids)
        if not tiene_parto and not tiene_bebes:
            return  # Nada que mostrar

        p.setFont("Helvetica-Bold", 16)
        p.drawCentredString(width / 2, height - 80, "DATOS DEL PARTO Y DEL BEBÉ")

        y = height - 130
        line_height = 18
        left_margin = inch

        # === Función auxiliar simple ===
        def draw_field(label, value):
            nonlocal y
            if y < inch + 40:
                self._add_footer(p, width, height)
                p.showPage()
                p.setFont("Helvetica-Bold", 16)
                p.drawCentredString(width / 2, height - 80, "DATOS DEL PARTO Y DEL BEBÉ (cont.)")
                y = height - 130
                p.setFont("Helvetica", 11)
            p.drawString(left_margin, y, f"{label}: {self._safe_value(value)}")
            y -= line_height

        # ======================================================
        # SECCIÓN DE DATOS DEL PARTO
        # ======================================================
        if tiene_parto:
            p.setFont("Helvetica-Bold", 13)
            p.drawString(left_margin, y, "Datos del Parto")
            y -= 25
            p.setFont("Helvetica", 11)

            draw_field("Fecha de egreso del hospital", beneficiaria.fecha_egreso_hospital)
            draw_field("Nombre del hospital", beneficiaria.hospital_parto)
            draw_field("¿Parto múltiple?", "Sí" if beneficiaria.parto_multiple else "No")

            # Línea separadora
            y -= 10
            p.line(left_margin, y, width - inch, y)
            y -= 30

        # ======================================================
        # SECCIÓN DE DATOS DEL BEBÉ
        # ======================================================
        if tiene_bebes:
            p.setFont("Helvetica-Bold", 13)
            p.drawString(left_margin, y, "Datos del Bebé")
            y -= 25
            p.setFont("Helvetica", 10)

            y_start = y
            line_height = 18
            col_gap = 1.5 * inch
            col_width = (width - 2 * inch - col_gap) / 2
            left_margin = inch
            right_col_x = left_margin + col_width + col_gap

            def draw_field_col(label, value, x_pos, y_pos):
                text = f"{label}: {self._safe_value(value)}"
                p.drawString(x_pos, y_pos, text)

            for idx, bebe in enumerate(beneficiaria.bebe_ids, start=1):
                # Encabezado
                p.setFont("Helvetica-Bold", 11)
                p.drawString(left_margin, y, f"Bebé {idx}: {bebe.nombre or '-'}")
                y -= 20
                p.setFont("Helvetica", 10)

                # Columna izquierda
                x = left_margin
                col_y = y

                draw_field_col("Sexo", dict(bebe._fields["sexo"].selection).get(bebe.sexo, "-"), x, col_y)
                col_y -= line_height
                draw_field_col("Fecha y hora de nacimiento", bebe.fecha_y_hora_nacimiento, x, col_y)
                col_y -= line_height
                draw_field_col("Lugar de nacimiento", bebe.lugar_nacimiento, x, col_y)
                col_y -= line_height
                draw_field_col("Talla (cm)", bebe.talla_al_nacer, x, col_y)
                col_y -= line_height
                draw_field_col("Peso (kg)", bebe.peso_al_nacer, x, col_y)
                col_y -= line_height
                draw_field_col("Cuidado por", bebe.cuidado_por, x, col_y)
                col_y -= line_height
                draw_field_col("¿Tiene CUN?", "Sí" if bebe.tiene_cun else "No", x, col_y)
                col_y -= line_height
                draw_field_col("¿Tiene acta de nacimiento?", "Sí" if bebe.tiene_acta_nacimiento else "No", x, col_y)
                col_y -= line_height
                draw_field_col("¿Ingresó al cunero?", "Sí" if bebe.bebe_ingreso_cunero else "No", x, col_y)
                col_y -= line_height
                draw_field_col("¿Mamá desistió de entrega?", "Sí" if bebe.mama_desistio_entrega else "No", x, col_y)
                col_y -= line_height

                # Columna derecha
                x = right_col_x
                col_y = y

                draw_field_col("Fecha egreso institución", bebe.fecha_egreso_institucion, x, col_y)
                col_y -= line_height
                draw_field_col("Motivo egreso", dict(bebe._fields["motivo_egreso"].selection).get(bebe.motivo_egreso, "-"), x, col_y)
                col_y -= line_height
                draw_field_col("Otro motivo egreso", bebe.motivo_egreso_otro, x, col_y)
                col_y -= line_height
                draw_field_col("Núm. certificado nacimiento", bebe.numero_cert_nacimiento, x, col_y)
                col_y -= line_height
                draw_field_col("Municipio registro", bebe.municipio_registro, x, col_y)
                col_y -= line_height
                draw_field_col("Fecha registro", bebe.fecha_registro, x, col_y)
                col_y -= line_height
                draw_field_col("CURP bebé", bebe.curp_bebe, x, col_y)
                col_y -= line_height
                draw_field_col("Entidad registro", bebe.entidad_registro, x, col_y)
                col_y -= line_height
                draw_field_col("Oficialía registro", bebe.oficialia_registro, x, col_y)
                col_y -= line_height

                # === Nacido muerto (si aplica) ===
                if bebe.nacido_muerto:
                    col_y -= 10
                    p.setFont("Helvetica-Bold", 10)
                    p.drawString(x, col_y, "Defunción:")
                    col_y -= line_height
                    p.setFont("Helvetica", 10)
                    draw_field_col("Certificado defunción", bebe.numero_certificado_defuncion, x, col_y)
                    col_y -= line_height
                    draw_field_col("Fecha defunción", bebe.fecha_defuncion, x, col_y)

                # === Documentos relacionados ===
                y_docs = min(y, col_y) - 25
                p.setFont("Helvetica-Bold", 10)
                p.drawString(left_margin, y_docs, "Documentos adjuntos:")
                y_docs -= line_height
                p.setFont("Helvetica", 10)
                if bebe.documento_ids:
                    for doc in bebe.documento_ids:
                        if y_docs < inch + 40:
                            self._add_footer(p, width, height)
                            p.showPage()
                            p.setFont("Helvetica-Bold", 16)
                            p.drawCentredString(width / 2, height - 80, "DATOS DEL PARTO Y DEL BEBÉ (cont.)")
                            y_docs = height - 120
                            p.setFont("Helvetica", 10)
                        p.drawString(left_margin + 20, y_docs, f"- {self._safe_value(doc.name)}")
                        y_docs -= line_height
                else:
                    p.drawString(left_margin + 20, y_docs, "No hay documentos adjuntos.")
                    y_docs -= line_height

                # === Separador entre bebés ===
                y = y_docs - 25
                p.line(left_margin, y, width - inch, y)
                y -= 30

                if y < inch + 100:
                    self._add_footer(p, width, height)
                    p.showPage()
                    p.setFont("Helvetica-Bold", 16)
                    p.drawCentredString(width / 2, height - 80, "DATOS DEL PARTO Y DEL BEBÉ (cont.)")
                    y = height - 130

            # Total bebés
            p.setFont("Helvetica-Bold", 10)
            p.drawString(left_margin, y, f"Total de bebés registrados: {len(beneficiaria.bebe_ids)}")

        self._add_footer(p, width, height)
        p.showPage()

    def _add_section_proyecto_de_vida(self, p, beneficiaria, width, height):
        """Sección: Proyecto de Vida de la beneficiaria (solo si hay datos relevantes)."""

        # === Validar si hay información que mostrar ===
        if not any([
            beneficiaria.reaccion_confirmacion_embarazo,
            beneficiaria.intento_aborto,
            beneficiaria.medio_intento_aborto,
            beneficiaria.recibe_apoyo,
            beneficiaria.especifique_apoyo,
            beneficiaria.sabe_que_es_adocion,
            beneficiaria.conoce_adopcion,
            beneficiaria.te_gustaria_conocer,
            beneficiaria.desea_dar_a_adopcion,
        ]):
            return  # No generar página si está vacío

        # === Encabezado ===
        p.setFont("Helvetica-Bold", 16)
        p.drawCentredString(width / 2, height - 80, "PROYECTO DE VIDA")

        y = height - 130
        line_height = 18
        left_margin = inch

        def draw_field(label, value):
            nonlocal y
            if y < inch + 40:
                self._add_footer(p, width, height)
                p.showPage()
                p.setFont("Helvetica-Bold", 16)
                p.drawCentredString(width / 2, height - 80, "PROYECTO DE VIDA (cont.)")
                y = height - 130
                p.setFont("Helvetica", 11)
            p.drawString(left_margin, y, f"{label}: {self._safe_value(value)}")
            y -= line_height

        # === Reacción al embarazo ===
        p.setFont("Helvetica-Bold", 12)
        p.drawString(left_margin, y, "Reacción ante el embarazo")
        y -= 25
        p.setFont("Helvetica", 11)

        draw_field("Reacción al confirmar el embarazo",
                   dict(beneficiaria._fields["reaccion_confirmacion_embarazo"].selection).get(beneficiaria.reaccion_confirmacion_embarazo, "-"))
        draw_field("¿Intentó abortar?", "Sí" if beneficiaria.intento_aborto else "No")
        draw_field("Medio del intento de aborto", beneficiaria.medio_intento_aborto)

        # === Apoyo recibido ===
        if beneficiaria.recibe_apoyo or beneficiaria.especifique_apoyo:
            y -= 10
            p.line(left_margin, y, width - inch, y)
            y -= 30
            p.setFont("Helvetica-Bold", 12)
            p.drawString(left_margin, y, "Apoyo recibido")
            y -= 25
            p.setFont("Helvetica", 11)

            draw_field("¿Recibió apoyo de algún familiar, amigo o conocido?",
                       "Sí" if beneficiaria.recibe_apoyo else "No")
            draw_field("Especifique el apoyo recibido", beneficiaria.especifique_apoyo)

        # === Adopción ===
        if any([
            beneficiaria.sabe_que_es_adocion,
            beneficiaria.conoce_adopcion,
            beneficiaria.te_gustaria_conocer,
            beneficiaria.desea_dar_a_adopcion
        ]):
            y -= 10
            p.line(left_margin, y, width - inch, y)
            y -= 30
            p.setFont("Helvetica-Bold", 12)
            p.drawString(left_margin, y, "Conocimiento sobre adopción")
            y -= 25
            p.setFont("Helvetica", 11)

            draw_field("¿Sabe qué es la adopción?", "Sí" if beneficiaria.sabe_que_es_adocion else "No")
            draw_field("¿Conoce el proceso de adopción?", "Sí" if beneficiaria.conoce_adopcion else "No")
            draw_field("¿Le gustaría conocer más sobre la adopción?", "Sí" if beneficiaria.te_gustaria_conocer else "No")
            draw_field("¿Desea dar a su bebé en adopción?", "Sí" if beneficiaria.desea_dar_a_adopcion else "No")

        self._add_footer(p, width, height)
        p.showPage()

    def _add_section_alta(self, p, beneficiaria, width, height):
        """Sección final: Datos de Alta de la beneficiaria, incluyendo la fotografía de la identificación."""

        # === Validar si hay información de alta ===
        if not any([
            beneficiaria.fecha_alta,
            beneficiaria.se_retiro_despues_de_dar_a_luz,
            beneficiaria.se_retiro_con_bebe,
            beneficiaria.se_retira_con_permiso_regreso_entrega_voluntaria,
            beneficiaria.fecha_conclusion_entrega_voluntaria,
            beneficiaria.persona_recoge,
            beneficiaria.relacion_persona_recoge,
            beneficiaria.telefono_persona_recoge,
            beneficiaria.domicilio_persona_recoge,
            beneficiaria.identificacion_persona_recoge,
            beneficiaria.nombre_testigo1,
            beneficiaria.nombre_testigo2,
            beneficiaria.autorizado_por,
        ]):
            return  # No generar página si está vacío

        # === Encabezado ===
        p.setFont("Helvetica-Bold", 16)
        p.drawCentredString(width / 2, height - 80, "DATOS DE ALTA")

        y = height - 130
        line_height = 18
        left_margin = inch

        def draw_field(label, value):
            nonlocal y
            if y < inch + 60:
                self._add_footer(p, width, height)
                p.showPage()
                p.setFont("Helvetica-Bold", 16)
                p.drawCentredString(width / 2, height - 80, "DATOS DE ALTA (cont.)")
                y = height - 130
                p.setFont("Helvetica", 11)
            p.drawString(left_margin, y, f"{label}: {self._safe_value(value)}")
            y -= line_height

        # === Datos generales ===
        if any([
            beneficiaria.fecha_alta,
            beneficiaria.se_retiro_despues_de_dar_a_luz,
            beneficiaria.se_retiro_con_bebe,
            beneficiaria.se_retira_con_permiso_regreso_entrega_voluntaria,
            beneficiaria.fecha_conclusion_entrega_voluntaria
        ]):
            p.setFont("Helvetica-Bold", 13)
            p.drawString(left_margin, y, "Información general de alta")
            y -= 25
            p.setFont("Helvetica", 11)

            draw_field("Fecha de alta", beneficiaria.fecha_alta)
            draw_field("¿Se retiró después de dar a luz?", "Sí" if beneficiaria.se_retiro_despues_de_dar_a_luz else "No")
            draw_field("¿Se retiró con el bebé?", "Sí" if beneficiaria.se_retiro_con_bebe else "No")
            draw_field("¿Se retira con permiso para regresar y concluir entrega voluntaria?",
                       "Sí" if beneficiaria.se_retira_con_permiso_regreso_entrega_voluntaria else "No")
            draw_field("Fecha de conclusión de entrega voluntaria", beneficiaria.fecha_conclusion_entrega_voluntaria)

            y -= 10
            p.line(left_margin, y, width - inch, y)
            y -= 30

        # === Persona que recoge ===
        if any([
            beneficiaria.persona_recoge,
            beneficiaria.relacion_persona_recoge,
            beneficiaria.telefono_persona_recoge,
            beneficiaria.domicilio_persona_recoge,
            beneficiaria.identificacion_persona_recoge
        ]):
            p.setFont("Helvetica-Bold", 13)
            p.drawString(left_margin, y, "Persona que recoge a la beneficiaria")
            y -= 25
            p.setFont("Helvetica", 11)

            draw_field("Nombre de la persona", beneficiaria.persona_recoge)
            draw_field("Relación con la beneficiaria", beneficiaria.relacion_persona_recoge)
            draw_field("Teléfono", beneficiaria.telefono_persona_recoge)
            draw_field("Domicilio", beneficiaria.domicilio_persona_recoge)

            # Imagen (identificación)
            if beneficiaria.identificacion_persona_recoge:
                try:
                    img_data = base64.b64decode(beneficiaria.identificacion_persona_recoge)
                    img = ImageReader(BytesIO(img_data))

                    img_width = 2.5 * inch
                    img_height = 2 * inch
                    x_img = width - inch - img_width
                    y_img = y - img_height + 20

                    p.setFont("Helvetica-Bold", 11)
                    p.drawString(x_img, y_img + img_height + 10, "Identificación:")
                    p.drawImage(img, x_img, y_img, width=img_width, height=img_height, preserveAspectRatio=True)
                    y = y_img - 40

                except Exception as e:
                    p.setFont("Helvetica", 10)
                    p.drawString(width - 3.5 * inch, y, f"[Error al cargar la imagen: {str(e)}]")
                    y -= 20

            y -= 10
            p.line(left_margin, y, width - inch, y)
            y -= 30

        # === Testigos ===
        if any([beneficiaria.nombre_testigo1, beneficiaria.nombre_testigo2, beneficiaria.autorizado_por]):
            p.setFont("Helvetica-Bold", 13)
            p.drawString(left_margin, y, "Testigos y autorización")
            y -= 25
            p.setFont("Helvetica", 11)

            draw_field("Testigo 1", beneficiaria.nombre_testigo1)
            draw_field("Testigo 2", beneficiaria.nombre_testigo2)
            draw_field("Autorizado por", beneficiaria.autorizado_por.name if beneficiaria.autorizado_por else "-")

            y -= 40
            p.line(left_margin + 50, y, left_margin + 200, y)
            p.drawString(left_margin + 80, y - 15, "Firma de la beneficiaria")

        self._add_footer(p, width, height)
        p.showPage()
