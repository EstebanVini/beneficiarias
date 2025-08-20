from odoo import models, fields # type: ignore[import]

class GeoCity(models.Model):
    _name = 'geo.city'
    _description = 'Ciudad'

    name = fields.Char(string='Nombre de la Ciudad', required=True)
    state_id = fields.Many2one('res.country.state', string="Estado", required=True)
    country_id = fields.Many2one(related='state_id.country_id', store=True, string="País", readonly=True)
