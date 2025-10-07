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
        # === SEGUNDA SECCIÓN: Canalización y Legal ===
        self._add_section_canalizacion_legal(p, beneficiaria, width, height)
        # === TERCERA SECCIÓN: Fotos ===
        self._add_section_fotos(p, beneficiaria, width, height)

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
                from odoo.tools import html2plaintext
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


    def _add_section_informacion_particular(self, p, beneficiaria, width, height):
        """Sección combinada: Información Particular Detallada + Residencia"""
        p.setFont("Helvetica-Bold", 16)
        p.drawCentredString(width / 2, height - 80, "INFORMACIÓN PARTICULAR DETALLADA")

        # === Configuración visual ===
        y = height - 130
        line_height = 20
        section_spacing = 25
        subtitle_spacing = 20
        left_margin = inch
        col2_x = width / 2 + 0.5 * inch  # margen para la segunda columna

        # Función auxiliar reutilizable
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
        # COLUMNA IZQUIERDA → Datos personales y contexto
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
        # COLUMNA DERECHA → Residencia (Domicilio)
        # ======================================================

        # Reiniciar Y para la segunda columna (un poco más arriba)
        y_col2 = height - 130

        p.setFont("Helvetica-Bold", 13)
        p.drawString(col2_x, y_col2, "Domicilio")
        y_col2 -= subtitle_spacing
        p.setFont("Helvetica", 11)

        def draw_field_col2(label, value):
            nonlocal y_col2
            if y_col2 < inch:
                self._add_footer(p, width, height)
                p.showPage()
                y_col2 = height - 100
                p.setFont("Helvetica-Bold", 13)
                p.drawString(col2_x, y_col2, "Domicilio (cont.)")
                y_col2 -= subtitle_spacing
                p.setFont("Helvetica", 11)
            p.drawString(col2_x, y_col2, f"{label}: {value or '-'}")
            y_col2 -= line_height

        draw_field_col2("País", getattr(beneficiaria.pais, "name", None))
        draw_field_col2("Estado", getattr(beneficiaria.estado, "name", None))
        draw_field_col2("Municipio", beneficiaria.municipio)
        draw_field_col2("Colonia", beneficiaria.colonia)
        draw_field_col2("Calle", beneficiaria.calle)
        draw_field_col2("Número exterior", beneficiaria.numero_exterior)
        draw_field_col2("Número interior", beneficiaria.numero_interior)
        draw_field_col2("Código postal", beneficiaria.codigo_postal)

        # === Footer al final de la página ===
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
