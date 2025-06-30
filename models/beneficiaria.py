from odoo import models, fields, api # type: ignore
from odoo.exceptions import ValidationError # type: ignore
from datetime import date

import re

class Beneficiaria(models.Model):
    _name = 'beneficiarias.beneficiaria'
    _description = 'Beneficiaria'

    # === DATOS PERSONALES ===
    nombre = fields.Char(string="Nombre", required=True)
    apellido_paterno = fields.Char(string="Apellido Paterno", required=True)
    apellido_materno = fields.Char(string="Apellido Materno", required=True)
    curp = fields.Char(string="CURP", required=True)
    rfc = fields.Char(string="RFC", required=True)
    fecha_nacimiento = fields.Date(string="Fecha de Nacimiento", required=True)
    fecha_ingreso = fields.Date(string="Fecha de Ingreso", required=True)
    edad_ingreso = fields.Integer(string="Edad al Ingresar", compute="_compute_edad_ingreso", store=True)
    rango = fields.Selection([
        ('m12', 'Menor de 12 años'),
        ('12a14','De 12 a 14 años'),
        ('15a17','De 15 a 17 años'),
        ('18a22','De 18 a 22 años'),
        ('23a27','De 23 a 27 años'),
        ('28a31','De 28 a 31 años'),
        ('ma32','Mayores de 32')
    ], string="Rango de Edad")

    nacionalidad = fields.Char(string="Nacionalidad")
    estado_civil = fields.Char(string="Estado Civil")
    ocupacion = fields.Char(string="Ocupación")
    escolaridad = fields.Char(string="Escolaridad")
    religion = fields.Char(string="Religión")

    # === EMBARAZO ===
    embarazo = fields.Boolean(string="¿Está embarazada?")
    fum_time = fields.Date(string="FUM")
    meses_embarazo = fields.Integer(string="Meses de embarazo")
    semanas_gestacion = fields.Integer(string="Semanas de gestación")
    fecha_probable_de_parto = fields.Date(string="Fecha probable de parto")

    # === EGRESO ===
    motivo_de_egreso = fields.Selection([
        ('01', 'Arregló su situación personal'),
        ('02', 'No se adaptó a la casa hogar'),
        ('03', 'Tuvo problemas con el personal'),
        ('04', 'Tuvo problemas con otras internas'),
        ('05', 'Egreso no autorizado'),
        ('06', 'Egreso por autoridad'),
        ('07', 'Canalización a otra institución'),
        ('08', 'VIFAC no cubrió mis expectativas'),
        ('09', 'Otro')
    ], string="Motivo de egreso (embarazada)")
    motivo_de_egreso_otro = fields.Char(string="Especifique (embarazada)")

    motivo_de_egreso_parto = fields.Selection([
        ('01', 'Reintegración a su núcleo familiar, madre e hijo(a)'),
        ('02', 'Egreso voluntario madre e hijo(a)'),
        ('03', 'Egreso por autoridad madre e hijo(a)'),
        ('04', 'Egreso no autorizado madre e hijo(a)'),
        ('05', 'Egreso post entrega en adopción (madre)'),
        ('06', 'Canalización a otra institución madre e hijo(a)'),
        ('07', 'Otro')
    ], string="Motivo de egreso (post parto)")
    motivo_de_egreso_otro_post_parto = fields.Char(string="Especifique (post parto)")

    # === REFERENCIAS Y UBICACIÓN ===
    ref_auto = fields.Char(string="Referida por autoridad")
    atention_center = fields.Selection([
        ('aguascalientes', 'Aguascalientes'), ('brownsville', 'Brownsville'),
        ('cancun', 'Cancún'), ('cdmx', 'Ciudad de México'),
        ('chihuaha', 'Chihuaha'), ('ciudadjuarez', 'Ciudad Juárez'),
        ('ciudadsatelite', 'Ciudad Satélite'),
        ('ciudadsateliteeducadores', 'Ciudad Satélite (Educadores)'),
        ('ciudadsatelitecasaazul', 'Ciudad Satélite (Casa Azul)'),
        ('cuernavaca', 'Cuernavaca'), ('culiacan', 'Culiacán'),
        ('delicias', 'Delicias'), ('guadalajara', 'Guadalajara'),
        ('hermosillo', 'Hermosillo'), ('leon', 'León'),
        ('loscabos', 'Los Cabos'), ('merida', 'Mérida'),
        ('mexicali', 'Mexicali'), ('monterrey', 'Monterrey'),
        ('morelia', 'Morelia'), ('oaxaca', 'Oaxaca'),
        ('puebla', 'Puebla'), ('queretaro', 'Querétaro'),
        ('tehuacan', 'Tehuacán'), ('tequisquiapan', 'Tequisquiapan'),
        ('tuxtlagutierrez', 'Tuxtla Gutiérrez'), ('veracruz', 'Veracruz'),
        ('zacatecas', 'Zacatecas')
    ], string="Centro de atención VIFAC")

    #proyecto_id = fields.Many2one('project.project', string='Proyecto')
    #asignado_a_id = fields.Many2one('res.users', string='Asignado a')
    #recibida_por_id = fields.Many2one('res.users', string='Recibida por')

    # tipo_ayuda_id = fields.Many2one('vifac.tipoayuda', string='Tipo de ayuda', required=True)
    # need_extra_ayuda = fields.Boolean(string='Otro campo', related='tipo_ayuda_id.extra_field', readonly=True)
    # especifique_ayuda = fields.Char(string='Especifique')

    # === ACOMPAÑANTE ===
    acompanante = fields.Boolean(string="¿Tiene acompañante?")
    acompanante_nombre = fields.Char(string="Nombre del acompañante")
    acompanante_parentesco = fields.Char(string="Parentesco")

    # === RELACIONES ===
    # hijo_ids = fields.One2many('vifac.hijo', 'beneficiaria_id')
    #bebe_ids = fields.One2many('vifac.bebe', 'beneficiaria_id')
    #documento_ids = fields.One2many('vifac.documento', 'beneficiaria_id')
    #red_social_ids = fields.One2many('vifac.redsocial', 'beneficiaria_id')
    #valoracion_ids = fields.One2many('vifac.valoracion', 'beneficiaria_id')
    #encuesta_ids = fields.One2many('vifac.encuesta', 'beneficiaria_id')
    #tipo_ayuda_ids = fields.Many2many('vifac.tipoayuda', string='Tipos de ayuda')

    # === CÁLCULOS Y VALIDACIONES ===
    @api.depends('fecha_nacimiento', 'fecha_ingreso')
    def _compute_edad_ingreso(self):
        for record in self:
            if record.fecha_nacimiento and record.fecha_ingreso:
                delta = record.fecha_ingreso - record.fecha_nacimiento
                record.edad_ingreso = delta.days // 365
            else:
                record.edad_ingreso = 0

    @api.constrains('curp')
    def _check_curp_format(self):
        for record in self:
            if record.curp and not re.match(r'^[A-Z]{4}\d{6}[HM][A-Z]{5}\d{2}$', record.curp):
                raise ValidationError("CURP no tiene un formato válido.")

    @api.constrains('rfc')
    def _check_rfc_format(self):
        for record in self:
            if record.rfc and not re.match(r'^[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}$', record.rfc):
                raise ValidationError("RFC no tiene un formato válido.")
