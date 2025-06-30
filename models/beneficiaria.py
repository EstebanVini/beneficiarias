from odoo import models, fields

class Beneficiaria(models.Model):
    _name = 'beneficiarias.beneficiaria'
    _description = 'Beneficiaria'

    name = fields.Char(string='Nombre completo', required=True)
    edad = fields.Integer(string='Edad')
    direccion = fields.Char(string='Dirección')
