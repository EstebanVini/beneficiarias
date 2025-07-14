from odoo import models, fields, api # type: ignore
from odoo.exceptions import ValidationError # type: ignore

class Valoracion(models.Model):
    _name = 'beneficiarias.valoracion'
    _description = 'Valoraciones de Beneficiarias'

    fecha_realizacion = fields.Date(string='Fecha de Realización', required=True)
    elaborado_por = fields.Char(string='Elaborado por', required=True)
    categoria = fields.Selection([
        ('psicologica_ingreso', 'Evaluación Psicológica de ingreso'),
        ('socioeconomica_ingreso', 'Evaluación Socioeconómica de ingreso'),
        ('medica_ingreso', 'Evaluación Médica de ingreso'),
        ('pedagogica_ingreso', 'Evaluación Pedagógica de Ingreso'),
        ('psicologica_1', 'Evaluación Psicológica (1)'),
        ('socioeconomica_1', 'Evaluación Socioeconómica (1)'),
        ('medica_1', 'Evaluación Médica (1)'),
        ('pedagogica_1', 'Evaluación Pedagógica (1)'),
        ('consultoria', 'Consultoría'),
        ('nutricion', 'Nutrición'),
        ('otros', 'Otros'),
    ], string='Categoría', required=True)

    beneficiaria_id = fields.Many2one(
        'beneficiarias.beneficiaria', string='Beneficiaria', required=True, ondelete='cascade'
    )

    valoracion_archivo = fields.Binary(string="Archivo Valoración")
    valoracion_nombre_archivo = fields.Char(string="Nombre del Archivo de Valoración")

    documentos_ids = fields.One2many(
        'beneficiarias.documento', 'valoracion_id', string='Documentos',
        domain=[('tipo_relacion', '=', 'valoracion')]
    )

    @api.model
    def create(self, vals):
        record = super().create(vals)
        record._crear_documento_valoracion()
        return record

    def write(self, vals):
        res = super().write(vals)
        self._crear_documento_valoracion()
        return res

    def _crear_documento_valoracion(self):
        """Crea o actualiza el documento principal ligado a esta valoración."""
        for rec in self:
            if rec.valoracion_archivo and rec.valoracion_nombre_archivo and rec.beneficiaria_id:
                Documento = self.env['beneficiarias.documento']
                doc = Documento.search([
                    ('valoracion_id', '=', rec.id),
                    ('tipo_relacion', '=', 'valoracion'),
                    ('name', '=', f'Valoración {rec.categoria or ""}')
                ], limit=1)
                vals = {
                    'name': f'Valoración {rec.categoria or ""}',
                    'descripcion': 'Documento principal subido desde valoración',
                    'archivo': rec.valoracion_archivo,
                    'nombre_archivo': rec.valoracion_nombre_archivo,
                    'valoracion_id': rec.id,
                    'beneficiaria_id': rec.beneficiaria_id.id,
                    'tipo_relacion': 'valoracion',
                }
                if doc:
                    doc.write(vals)
                else:
                    Documento.create(vals)
            else:
                # Si se elimina el archivo, elimina también el documento principal relacionado
                doc = self.env['beneficiarias.documento'].search([
                    ('valoracion_id', '=', rec.id),
                    ('tipo_relacion', '=', 'valoracion'),
                    ('name', '=', f'Valoración {rec.categoria or ""}')
                ])
                doc.unlink()

    def action_ver_valoracion(self):
        self.ensure_one()
        if not self.valoracion_archivo or not self.valoracion_nombre_archivo:
            raise ValidationError("No hay un documento subido para esta valoración.")
        return {
            'type': 'ir.actions.act_url',
            'url': f"/web/content/{self._name}/{self.id}/valoracion_archivo/{self.valoracion_nombre_archivo}?download=false",
            'target': 'new',
        }
