from odoo import models, fields, api # type: ignore[import-untyped]

class Documento(models.Model):
    _name = 'beneficiarias.documento'
    _description = 'Documento adjunto personalizado'

    name = fields.Char(string='Nombre del documento', required=True)
    descripcion = fields.Text(string='Descripción')

    attachment_id = fields.Many2one('ir.attachment', string='Archivo', required=True)
    file_name = fields.Char(related='attachment_id.name', string='Nombre del archivo', store=False)

    tipo_relacion = fields.Selection([
        ('beneficiaria', 'Beneficiaria'),
        ('hijo', 'Hijo'),
        ('bebe', 'Bebé'),
    ], string='Relacionado con', required=True)

    beneficiaria_id = fields.Many2one('beneficiarias.beneficiaria', string='Beneficiaria')
    bebe_id = fields.Many2one('beneficiarias.bebe', string='Bebé')
    hijo_id = fields.Many2one('beneficiarias.hijo', string='Hijo')


    url = fields.Char(string='Descargar', compute='_compute_url', store=False)

    @api.depends('attachment_id')
    def _compute_url(self):
        for record in self:
            if record.attachment_id:
                record.url = f"/web/content/{record.attachment_id.id}?download=true"
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

