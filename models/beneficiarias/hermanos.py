from odoo import models, fields, api # type: ignore
from odoo.exceptions import ValidationError # type: ignore

class Hermano(models.Model):
    _name = 'beneficiarias.hermano'
    _description = 'Hermanos de la beneficiaria'

    nombre = fields.Char(string="Nombre", required=True)
    telefono = fields.Char(string="Teléfono")
    tienen_relacion = fields.Boolean(string="Tiene relación con el/ella", default=False)
    
    beneficiaria_id = fields.Many2one('beneficiarias.beneficiaria', string="Beneficiaria", required=True)