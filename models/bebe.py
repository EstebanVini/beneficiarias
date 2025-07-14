from odoo import models, fields, api  # type: ignore[import-untyped]

class Bebe(models.Model):
    _name = 'beneficiarias.bebe'
    _description = 'Bebé'

    # === FORMULARIO PRINCIPAL ===

    nombre = fields.Char(required=True)
    
    sexo = fields.Selection([
        ('masculino', 'Masculino'),
        ('femenino', 'Femenino'),
    ], string='Sexo', required=True)

    fecha_y_hora_nacimiento = fields.Datetime(string='Fecha y hora de nacimiento', required=True)
    lugar_nacimiento = fields.Char(string='Lugar de nacimiento')
    talla_al_nacer = fields.Float(string='Talla al nacer (cm)')
    peso_al_nacer = fields.Float(string='Peso al nacer (kg)')

    caracteristicas_especiales = fields.Text(string='Características especiales')
    tiene_cun = fields.Boolean(string='Certificado Único de Nacimiento (CUN)')
    tiene_acta_nacimiento = fields.Boolean(string='Acta de nacimiento')

    cuidado_por = fields.Char(string='Cuidado por', help='Nombre de la persona que cuida al bebé')

    bebe_ingreso_cunero = fields.Boolean(string='¿El bebé ingresó al cunero?')
    mama_desistio_entrega = fields.Boolean(string='¿La mamá desistió de la entrega?')

    fecha_egreso_institucion = fields.Date(string='Fecha de egreso de la institución')
    motivo_egreso = fields.Selection([
        ('adopcion', 'Adopción'),
        ('reintegro_familiar', 'Reintegro familiar'),
        ('otra', 'Otra'),
    ], string='Motivo de egreso')
    motivo_egreso_otro = fields.Char(string='Especifique otro motivo de egreso')

    numero_cert_nacimiento = fields.Char(string='Número de certificado de nacimiento')
    municipio_registro = fields.Char(string='Municipio de registro')
    fecha_registro = fields.Date(string='Fecha de registro')
    numero_acta_nacimiento = fields.Char(string='Número de acta de nacimiento')

    
    # si el bebé nació muerto
    nacido_muerto = fields.Boolean(string='Nacido muerto')
    numero_certificado_defuncion = fields.Char(string='Número de certificado de defunción')
    fecha_defuncion = fields.Date(string='Fecha de defunción')

    # certificado_nacimiento clase documento

    # acta de nacimiento

    mama_en_casa_hogar = fields.Boolean(string='¿La mamá está en la casa hogar?')
    fecha_ingreso_cunero = fields.Date(string='Fecha de ingreso al cunero')
    fecha_egreso_cunero = fields.Date(string='Fecha de egreso del cunero')

    curp_bebe = fields.Char(string='CURP del bebé')
    entidad_registro = fields.Char(string='Entidad de registro')
    oficialia_registro = fields.Char(string='Oficialía de registro')

    # === RELACIONES ===

    beneficiaria_id = fields.Many2one('beneficiarias.beneficiaria', string="Beneficiaria", required=False)
    padres_adoptivos_id = fields.Many2one('beneficiarias.papas_adoptivos', string="Padres adoptivos")
    documento_ids = fields.One2many(
        'beneficiarias.documento',
        'bebe_id',
        string='Documentos adjuntos',
        domain=[('tipo_relacion', '=', 'bebe')]
    )