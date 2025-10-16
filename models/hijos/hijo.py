from odoo import models, fields # type: ignore

class Hijo(models.Model):
    _name = 'beneficiarias.hijo'
    _description = 'Hijo'
    _rec_name = 'nombre'

    # === FORMULARIO PRINCIPAL ===
    nombre = fields.Char(required=True)
    edad = fields.Integer()
    nivel_estudios = fields.Char()
    vive_con_ella = fields.Boolean()
    la_acompana = fields.Boolean()
    responsable = fields.Char()
    escuela = fields.Char()

    # === PESTAÑA "INFORMACIÓN NO ACOMPAÑANTE" ===
    nombre_no_acompanante = fields.Char(string='Nombre del no acompañante')
    edad_no_acompanante = fields.Integer(string='Edad del no acompañante')
    fecha_nacimiento_no_acompanante = fields.Date(string='Fecha de nacimiento del no acompañante')
    lugar_nacimiento_no_acompanante = fields.Char(string='Lugar de nacimiento del no acompañante')
    nacionalidad_no_acompanante = fields.Char(string='Nacionalidad del no acompañante')
    fecha_registro_no_acompanante = fields.Date(string='Fecha de registro del no acompañante')
    folio_acta_nacimiento_no_acompanante = fields.Char(string='Folio del acta de nacimiento del no acompañante')
    oficialia_registro_no_acompanante = fields.Char(string='Oficialía de registro del no acompañante')
    libro_registro_no_acompanante = fields.Char(string='Libro de registro del no acompañante')
    CURP_no_acompanante = fields.Char(string='CURP del no acompañante')
    origen_etnico_no_acompanante = fields.Char(string='Origen étnico del no acompañante')
    estado_salud_no_acompanante = fields.Char(string='Estado de salud del no acompañante')
    nombre_padre_no_acompanante = fields.Char(string='Nombre del padre del no acompañante')
    edad_padre_no_acompanante = fields.Integer(string='Edad del padre del no acompañante')
    ocupacion_padre_no_acompanante = fields.Char(string='Ocupación del padre del no acompañante')
    relacion_actual_padre_no_acompanante = fields.Char(string='Relación actual con el padre de la niña o niño')

    # === PESTAÑA "DESCRIPCIÓN DE HIJO ACOMPAÑANTE" ===
    nombre_acompanante = fields.Char(string='Nombre del hijo acompañante')
    apellido_paterno_acompanante = fields.Char(string='Apellido del hijo acompañante')
    apellido_materno_acompanante = fields.Char(string='Apellido materno del hijo acompañante')
    fecha_nacimiento_acompanante = fields.Date(string='Fecha de nacimiento del hijo acompañante')
    CURP_no_acompanante = fields.Char(string='CURP del hijo acompañante')
    fecha_hora_ingreso_CAS = fields.Datetime(string='Fecha y hora de ingreso a la Casa Hogar')
    centro_atencion_de_ingreso_CAS = fields.Char(string='Centro de Atención de Ingreso (CAS)')
    motivo_ingreso_CAS = fields.Selection([
        ('abandono', 'Abandono'),
        ('violencia', 'Violencia'),
        ('maltrato', 'Maltrato'),
        ('otro', 'Otro'),
    ], string='Motivo de ingreso a la Casa Hogar')
    motivo_ingreso_CAS_otro = fields.Char(string='Especifique otro motivo de ingreso a la Casa Hogar')
    nombre_persona_realiza_inregreso = fields.Char(string='Nombre de la persona que realiza el ingreso')
    domicilio_acompanante = fields.Char(string='Domicilio del hijo acompañante')
    telefono_acompanante = fields.Char(string='Teléfono del hijo acompañante')
    estado_salud_acompanante = fields.Char(string='Estado de salud del hijo acompañante')
    identificacion_acompanante = fields.Binary(string='Identificación del hijo acompañante')
    relacion_con_acompanante = fields.Char(string='Relación con el hijo acompañante')
    fecha_registro_no_acompanante = fields.Date(string='Fecha de registro del hijo acompañante')

    # === PESTAÑA "INFORMACIÓN PARTICULAR DETALLADA" ===
    nombre_particular = fields.Char(string='Nombre')
    edad_particular = fields.Integer(string='Edad')
    fecha_nacimiento_particular = fields.Date(string='Fecha de Nacimiento')
    lugar_nacimiento_particular = fields.Char(string='Lugar de Nacimiento')
    nacionalidad_particular = fields.Char(string='Nacionalidad')
    fecha_registro_particular = fields.Date(string='Fecha de registro')
    folio_acta_nacimiento_particular = fields.Char(string='Folio del acta de nacimiento')
    oficialia_particular = fields.Char(string='Oficialía')
    libro_particular = fields.Char(string='Libro')
    curp_particular = fields.Char(string='CURP')
    origen_etnico_particular = fields.Char(string='Origen étnico')
    estado_salud_actual_particular = fields.Char(string='Estado de Salud Actual')
    nombre_padre_particular = fields.Char(string='Nombre del Padre')
    edad_padre_particular = fields.Integer(string='Edad del Padre')
    ocupacion_padre_particular = fields.Char(string='Ocupación del Padre')
    relacion_actual_padre_particular = fields.Char(string='Relación actual con el padre de la niña o niño')
    se_hace_cargo_particular = fields.Boolean(string='¿Se hace cargo de él?')
    sabe_que_esta_aqui_particular = fields.Boolean(string='¿Sabe que está aquí?')
    tiene_relacion_familia_padre_particular = fields.Boolean(string='¿Tiene relación con la familia del padre de su hija o hijo?')
    persona_emergencia_particular = fields.Char(string='En caso de emergencia, ¿Quién podría cuidar de su hijo?')
    parentesco_emergencia_particular = fields.Char(string='Parentesco de emergencia')
    telefono_emergencia_particular = fields.Char(string='Teléfono de emergencia')
    direccion_emergencia_particular = fields.Char(string='Dirección de emergencia')
    sabe_persona_institucion_particular = fields.Boolean(string='¿Sabe la persona que usted y su hijo están en la Institución?')
    observaciones_particular = fields.Text(string='Observaciones')

    # === PESTAÑA "ATENCIÓN" === 
    atencion_integral = fields.Boolean(string='Atención integral')
    medicina = fields.Boolean(string='Medicina')
    psicologia = fields.Boolean(string='Psicología')
    pedagogia = fields.Boolean(string='Pedagogía')
    legal = fields.Boolean(string='Legal')
    nutricion = fields.Boolean(string='Nutrición')
    regularizacion_escolar = fields.Boolean(string='Regularización Escolar')
    capacitacion = fields.Boolean(string='Capacitación')
    otros = fields.Boolean(string='Otros')
    especifique = fields.Char(string='Especifique')

    # === PESTAÑA "EGRESO" ===
    fecha_egreso_hora_egreso = fields.Datetime(string='Fecha y hora de egreso')
    motivo_egreso = fields.Selection([
        ('egreso_con_madre', 'Egreso con su madre por conclusión de servicio'),
        ('egreso_con_familiar', 'Egreso con familiar por autorización de su madre'),
        ('mandato_autoridad', 'Egreso por mandato de autoridad'),
        ('no_autorizado', 'Egreso no autorizado'),
        ('otro', 'Otro (especifique)'),
    ], string='Motivo de egreso')
    motivo_egreso_otro = fields.Char(string='Especifique otro motivo de egreso')
    nombre_persona_entrega = fields.Char(string='Nombre de la persona que entrega al hijo')
    direccion_persona_entrega = fields.Char(string='Dirección de la persona que entrega al hijo')
    telefono_persona_entrega = fields.Char(string='Teléfono de la persona que entrega al hijo')
    parentesco_persona_entrega = fields.Char(string='Parentesco de la persona que entrega al hijo')
    identificacion_acompanante = fields.Binary(string='Identificación de la persona que entrega al hijo')

    # === PESTAÑA "DOCUMENTOS" ===
    tipo_documentos_adjuntos = fields.Selection([
        ('acta_nacimiento', 'Acta de Nacimiento'),
        ('curp', 'CURP'),
        ('cartilla_vacunacion', 'Cartilla de Vacunación'),
        ('documentos_escolares', 'Documentos Escolares'),
        ('identificacion', 'Identificación'),
        ('certificado_nacimiento', 'Certificado de Nacimiento'),
        ('documentos_medicos', 'Documentos Médicos'),
        ('identificacion_persona_egresa', 'Identificación de persona distinta que egresa a la niña o niño'),
        ('carta_responsiva_cuidado', 'Carta responsiva de cuidado'),
        ('carta_autorizacion_madre_egreso', 'Carta de autorización de la madre para el egreso de su hijo o hija'),
        ('carta_salida_madre_hijo', 'Carta de Salida de la Madre con su hijo'),
    ], string='Documento adjunto')


    # === PESTAÑA "VALORACIONES" ===
    tipo_valoracion = fields.Selection([
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
    ], string='Tipo de valoración')
    tipo_valoracion_otro = fields.Char(string='Especifique otro tipo de valoración')
    fecha_valoracion = fields.Date(string='Fecha de valoración')
    elaborado_por_valoracion = fields.Char(string='Elaborado por')

    # === RELACIONES ===
    beneficiaria_id = fields.Many2one('beneficiarias.beneficiaria', string="Beneficiaria", required=False)
    documentos_ids = fields.One2many(
        'beneficiarias.documento',
        'hijo_id',
        string='Documentos adjuntos',
        domain=[('tipo_relacion', '=', 'hijo')]
    )