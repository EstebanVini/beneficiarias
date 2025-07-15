from odoo import models, fields, api # type: ignore

class Traslados(models.Model):
    _name = 'beneficiarias.traslados'
    _description = 'Modelo para los traslados de beneficiarias'

    ubicacion_destino = fields.Char(string='Ubicación de destino', required=True)
    fecha_traslado = fields.Date(string='Fecha de traslado', required=True)
    beneficiaria_id = fields.Many2one('beneficiarias.beneficiaria', string='Beneficiaria', required=True)
    motivo_traslado = fields.Text(string='Motivo del traslado', required=True)
    estado = fields.Selection([
        ('pendiente', 'Pendiente'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado')
    ], string='Estado del traslado', default='pendiente')
    