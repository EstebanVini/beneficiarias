from odoo import models, fields # type: ignore

class PapasAdoptivos(models.Model):
    _name = "papas_adoptivos"
    _description = "Papas adoptivos para el bebe"

    nombre_padre_adoptivo = fields.Char(string="Nombre del Padre")
    edad_padre_adoptivo = fields.Integer(string="Edad del padre adoptivo")
    telefono_padre_adoptivo = fields.Integer(string="Número de teléfono del padre adoptivo")
    ocupacion_padre_adoptivo = fields.Char(string="Ocupacion padre adoptivo")

    nombre_madre_adoptiva = fields.Char(string="Nombre de la Madre adoptiva")
    edad_madre_adoptiva = fields.Integer(string="Edad de la madre adoptiva")
    telefono_madre_adoptiva = fields.Integer(string="Número de teléfono de la madre adoptiva")
    ocupacion_madre_adoptiva = fields.Char(string="Ocupacion madre adoptiva")

    direccion = fields.Char(string="Dirección de los padres adoptivos")
    fecha_adopcion = fields.Date(string="Fecha de adopción")

    estado = fields.Selection(
        selection=[
            ('activo', 'Activo'),
            ('inactivo', 'Inactivo')
        ],
        string="Estado",
        default='activo',
        help="Estado de los padres adoptivos"
    )

    # == RELACIONES ==
    bebe_ids = fields.One2many(
        comodel_name="bebe",
        inverse_name="papas_adoptivos_id",
        string="Bebés adoptados",
        help="Lista de bebés adoptados por los padres adoptivos"
    )

    documentos = fields.One2many(
        comodel_name="documento",
        inverse_name="papas_adoptivos_id",
        string="Documentos",
        help="Lista de documentos relacionados con los padres adoptivos"
    )