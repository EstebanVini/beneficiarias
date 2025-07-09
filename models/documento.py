from odoo import models, fields, api # type: ignore

class Documento(models.Model):
    _name = 'beneficiarias.documento'
    _description = 'Documento adjunto personalizado'

    name = fields.Char(string='Nombre del documento', required=True)
    descripcion = fields.Text(string='Descripción')

    archivo = fields.Binary(string='Archivo', required=True)
    nombre_archivo = fields.Char(string='Nombre del archivo')

    tipo_relacion = fields.Selection([
        ('beneficiaria', 'Beneficiaria'),
        ('hijo', 'Hijo'),
        ('bebe', 'Bebé'),
    ], string='Relacionado con', required=True)

    beneficiaria_id = fields.Many2one('beneficiarias.beneficiaria', string='Beneficiaria')
    bebe_id = fields.Many2one('beneficiarias.bebe', string='Bebé')
    hijo_id = fields.Many2one('beneficiarias.hijo', string='Hijo')

    url = fields.Char(string='Descargar', compute='_compute_url', store=False)

    @api.depends('archivo', 'nombre_archivo')
    def _compute_url(self):
        for record in self:
            if record.archivo:
                record.url = f"/web/content/beneficiarias.documento/{record.id}/archivo/{record.nombre_archivo}?download=true"
            else:
                record.url = False

    @api.model
    def create(self, vals):
        if vals.get('beneficiaria_id'):
            vals['tipo_relacion'] = 'beneficiaria'
        elif vals.get('hijo_id'):
            vals['tipo_relacion'] = 'hijo'
        elif vals.get('bebe_id'):
            vals['tipo_relacion'] = 'bebe'
        return super().create(vals)
