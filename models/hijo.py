from odoo import models, fields # type: ignore

class Hijo(models.Model):
    _name = 'beneficiarias.hijo'
    _description = 'Hijo'

    # === FORMULARIO PRINCIPAL ===
    nombre = fields.Char(required=True)
    edad = fields.Integer()
    nivel_estudios = fields.Char()
    vive_con_ella = fields.Boolean()
    la_acompaña = fields.Boolean()
    responsable = fields.Char()
    escuela = fields.Char()


    # === RELACIONES ===
    beneficiaria_id = fields.Many2one('beneficiarias.beneficiaria', string="Beneficiaria", required=False)
    documento_ids = fields.One2many(
        'documento',
        'hijo_id',
        string='Documentos adjuntos',
        domain=[('tipo_relacion', '=', 'hijo')]
    )