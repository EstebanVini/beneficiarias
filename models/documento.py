from odoo import models, fields, api # type: ignore[import-untyped]

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

    url_ver = fields.Char(string='URL Visualización', compute='_compute_urls', store=False)
    url_descargar = fields.Char(string='URL Descarga', compute='_compute_urls', store=False)

    @api.depends('archivo', 'nombre_archivo')
    def _compute_urls(self):
        for record in self:
            if record.id and record.archivo:
                base = f"/web/content/beneficiarias.documento/{record.id}/archivo/{record.nombre_archivo}"
                record.url_ver = base
                record.url_descargar = base + "?download=true"
            else:
                record.url_ver = False
                record.url_descargar = False

    @api.model
    def create(self, vals):
        # Asignar tipo_relacion automáticamente
        if vals.get('beneficiaria_id'):
            vals['tipo_relacion'] = 'beneficiaria'
        elif vals.get('hijo_id'):
            vals['tipo_relacion'] = 'hijo'
        elif vals.get('bebe_id'):
            vals['tipo_relacion'] = 'bebe'
        return super().create(vals)

    def action_ver_documento(self):
        self.ensure_one()
        if self.url_ver:
            return {
                'type': 'ir.actions.act_url',
                'url': self.url_ver,
                'target': 'new',
            }

    def action_descargar_documento(self):
        self.ensure_one()
        if self.url_descargar:
            return {
                'type': 'ir.actions.act_url',
                'url': self.url_descargar,
                'target': 'self',
            }
