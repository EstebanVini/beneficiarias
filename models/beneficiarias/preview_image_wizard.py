# models/preview_image_wizard.py
from odoo import fields, models # type: ignore

class PreviewImageWizard(models.TransientModel):
    _name = "preview.image.wizard"
    _description = "Vista previa de imagen"

    name = fields.Char(string="Título", readonly=True)
    # Guardamos/mostramos en alta para que se vea nítida
    image = fields.Image(string="Imagen", max_width=1920, max_height=1920, readonly=True)
