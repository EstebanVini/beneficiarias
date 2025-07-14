# models/beneficiaria_stage.py
from odoo import models, fields

class BeneficiariaStage(models.Model):
    _name = 'beneficiarias.stage'
    _description = 'Etapas del seguimiento de beneficiarias'
    _order = 'sequence, id'

    name = fields.Char(string='Nombre de la etapa', required=True)
    sequence = fields.Integer(default=10)
    fold = fields.Boolean(string="Colapsado por defecto")
