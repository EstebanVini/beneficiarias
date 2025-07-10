from odoo import models, fields, api # type: ignore
from odoo.exceptions import ValidationError # type: ignore

class Taller(models.Model):
    _name = 'beneficiarias.taller'
    _description = 'Taller'

    name_taller = fields.Char(string='Nombre del Taller', required=True)
    instructor = fields.Char(string='Instructor', required=True)
    fecha = fields.Date(string='Fecha', required=True)
    num_horas = fields.Integer(string='Número de Horas', required=True)
    comentarios = fields.Text(string='Comentarios')

    certificado_archivo = fields.Binary(string="Archivo Certificado")
    certificado_nombre_archivo = fields.Char(string="Nombre del Certificado")

    beneficiaria_id = fields.Many2one('beneficiarias.beneficiaria', string="Beneficiaria")

    documentos_ids = fields.One2many(
        'beneficiarias.documento', 'taller_id', string='Documentos',
        domain=[('tipo_relacion', '=', 'taller')]
    )

    @api.model
    def create(self, vals):
        record = super().create(vals)
        record._crear_documento_certificado()
        return record

    def write(self, vals):
        res = super().write(vals)
        self._crear_documento_certificado()
        return res

    def _crear_documento_certificado(self):
        """Crea o actualiza el documento certificado ligado a este taller."""
        for rec in self:
            if rec.certificado_archivo and rec.certificado_nombre_archivo and rec.beneficiaria_id:
                Documento = self.env['beneficiarias.documento']
                doc = Documento.search([
                    ('taller_id', '=', rec.id),
                    ('tipo_relacion', '=', 'taller'),
                ], limit=1)
                vals = {
                    'name': f'Certificado {rec.name_taller or ""}',
                    'descripcion': 'Certificado subido desde taller',
                    'archivo': rec.certificado_archivo,
                    'nombre_archivo': rec.certificado_nombre_archivo,
                    'taller_id': rec.id,
                    'beneficiaria_id': rec.beneficiaria_id.id,
                    'tipo_relacion': 'taller',
                }
                if doc:
                    doc.write(vals)
                else:
                    Documento.create(vals)
            else:
                # Si se elimina el archivo en el taller, también elimina el documento relacionado
                doc = self.env['beneficiarias.documento'].search([
                    ('taller_id', '=', rec.id),
                    ('tipo_relacion', '=', 'taller'),
                ])
                doc.unlink()

    def action_ver_certificado(self):
        self.ensure_one()
        if not self.certificado_archivo or not self.certificado_nombre_archivo:
            raise ValidationError("No hay un certificado subido para este taller.")
        return {
            'type': 'ir.actions.act_url',
            'url': f"/web/content/{self._name}/{self.id}/certificado_archivo/{self.certificado_nombre_archivo}?download=false",
            'target': 'new',
        }

