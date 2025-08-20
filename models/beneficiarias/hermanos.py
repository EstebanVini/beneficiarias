from odoo import models, fields, api # type: ignore
from odoo.exceptions import ValidationError # type: ignore

class Hermano(models.Model):
    _name = 'beneficiarias.hermano'
    _description = 'Hermanos de la beneficiaria'

    nombre = fields.Char(string="Nombre", required=True)
    telefono = fields.Char(string="Teléfono")
    tienen_relacion = fields.Boolean(string="Tiene relación con el/ella", default=False)

    beneficiaria_id = fields.Many2one('beneficiarias.beneficiaria', string="Beneficiaria", required=True)

    @api.constrains('telefono')
    def _check_telefono_numerico(self):
        for rec in self:
            for field_name in ['telefono']:
                value = getattr(rec, field_name)
                if value:
                    if not value.isdigit():
                        raise ValidationError("El campo %s solo debe contener números." % rec._fields[field_name].string)
                    if len(value) > 10:
                        raise ValidationError("El campo %s debe tener como máximo 10 dígitos." % rec._fields[field_name].string)
