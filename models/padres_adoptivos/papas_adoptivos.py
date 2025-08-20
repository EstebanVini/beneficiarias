from odoo import models, fields # type: ignore

class PapasAdoptivos(models.Model):
    _name = "beneficiarias.papas_adoptivos"
    _description = "Papas adoptivos para el bebe"
    _rec_name = 'nombre_padre_adoptivo'

    nombre_padre_adoptivo = fields.Char(string="Nombre del Padre")
    edad_padre_adoptivo = fields.Integer(string="Edad del padre adoptivo")
    telefono_padre_adoptivo = fields.Integer(string="Número de teléfono del padre adoptivo")
    ocupacion_padre_adoptivo = fields.Char(string="Ocupacion padre adoptivo")

    nombre_madre_adoptiva = fields.Char(string="Nombre de la Madre adoptiva")