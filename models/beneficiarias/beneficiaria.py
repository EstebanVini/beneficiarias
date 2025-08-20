from odoo import models, fields, api # type: ignore
from odoo.exceptions import ValidationError # type: ignore
from datetime import date, timedelta
import re

class Beneficiaria(models.Model):
    _name = 'beneficiarias.beneficiaria'
    _description = 'Beneficiaria'

    # === FORMULARIO PRINCIPAL ===
    nombre = fields.Char(string="Nombre(s)", required=True)
    apellido_paterno = fields.Char(string="Apellido Paterno", required=True)
    apellido_materno = fields.Char(string="Apellido Materno", required=True)
    nombre_completo = fields.Char(
        string="Nombre Completo", 
        compute='_compute_nombre_completo', 
        store=True, 
        readonly=True
    )
    curp = fields.Char(string="CURP", required=True)
    rfc = fields.Char(string="RFC")
    fecha_nacimiento = fields.Date(string="Fecha de Nacimiento", required=True)
    fecha_ingreso = fields.Date(string="Fecha de Ingreso", required=True)
    edad_ingreso = fields.Integer(string="Edad al Ingresar", compute="_compute_edad_ingreso", store=True)
    rango = fields.Selection([
        ('m12', 'Menor de 12 años'),
        ('m12a15', 'De 12 a 15 años'),
        ('m16a18','De 16 a 18 años'),
        ('m19a21','De 19 a 21 años'),
        ('m22a25','De 22 a 25 años'),
        ('m26a28','De 26 a 28 años'),
        ('m29a32','De 29 a 32 años'),
        ('m33a40','De 33 a 40 años'),
        ('ma40','Mayor de 40 años'),
    ], string="Rango de Edad", compute="_compute_rango_edad", store=True)


    atention_center = fields.Selection([
        ('aguascalientes', 'Aguascalientes'), ('brownsville', 'Brownsville'),
        ('cancun', 'Cancún'), ('cdmx', 'Ciudad de México'),
        ('chihuaha', 'Chihuaha'), ('ciudadjuarez', 'Ciudad Juárez'),
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

    numero_hijos = fields.Integer(string="Número de hijos que la acompañan", default=0, required=True)

    nacionalidad = fields.Char(string="Nacionalidad")
    estado_civil = fields.Char(string="Estado Civil")

    escolaridad = fields.Char(string="Escolaridad")

    # datos embarazo en formulario principal
    embarazo = fields.Boolean(string="¿Está embarazada?")
    fum_time = fields.Date(string="FUM")
    meses_embarazo = fields.Integer(string="Meses de embarazo", compute='_compute_embarazo_info', store=True)
    semanas_gestacion = fields.Integer(string="Semanas de gestación", compute='_compute_embarazo_info', store=True)
    fecha_probable_de_parto = fields.Date(string="Fecha probable de parto", compute='_compute_embarazo_info', store=True)

    tipo_de_ayuda = fields.Selection([
        ('interna', 'Interna'),
        ('externa', 'Externa'), 
        ('extra', 'Apoyo extra'),
        ('otro', 'Otro')
    ], string="Tipo de ayuda")
    tipo_de_ayuda_otro = fields.Char(string="Especifique tipo de ayuda")


    ref_auto = fields.Char(string="Referida por autoridad")

    # datos de egreso en formulario principal
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



    #proyecto_id = fields.Many2one('project.project', string='Proyecto')
    #asignado_a_id = fields.Many2one('res.users', string='Asignado a')
    #recibida_por_id = fields.Many2one('res.users', string='Recibida por')



    # ======== PESTAÑA DESCRIPCIÓN ==========

    descripcion = fields.Html(string='Descripción')


    # ======= PESTAÑA "INFORMACIÓN PARTICULAR DETALLADA" ========

    correo = fields.Char(string="Correo Electrónico")
    telefono = fields.Char(string="Teléfono")
    telefono_celular = fields.Char(string="Teléfono Celular")
    tiene_red_social = fields.Boolean(string="¿Tiene redes sociales?")
    tipo_red_social1 = fields.Selection([
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('twitter', 'Twitter'),
        ('tiktok', 'TikTok'),
        ('whatsapp', 'WhatsApp'),
        ('linkedin', 'LinkedIn'),
        ('otro', 'Otro')
    ], string="Tipo de Red Social")
    tipo_red_social1_otro = fields.Char(string="Especifique tipo de Red Social", help="Si eligió 'Otro', especifique el tipo de red social")
    red_social1 = fields.Char(string="Red Social 1")

    tipo_red_social2 = fields.Selection([
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('twitter', 'Twitter'),
        ('tiktok', 'TikTok'),
        ('whatsapp', 'WhatsApp'),
        ('linkedin', 'LinkedIn'),
        ('otro', 'Otro')
    ], string="Tipo de Red Social")
    tipo_red_social2_otro = fields.Char(string="Especifique tipo de Red Social", help="Si eligió 'Otro', especifique el tipo de red social")
    red_social2 = fields.Char(string="Red Social 2")

    nacionalidad = fields.Char(string="Nacionalidad")

    pais_nacimiento = fields.Many2one('res.country', string="País de Nacimiento")
    estado_nacimiento = fields.Many2one('res.country.state', string="Estado de Nacimiento",
                                        domain="[('country_id', '=', pais_nacimiento)]")
    ciudad_nacimiento = fields.Char(string="Ciudad de Nacimiento")

    lugar_de_registro = fields.Char(string="Lugar de Registro")

    # DOMICILIO
    pais = fields.Char(string="País")
    calle = fields.Char(string="Calle")
    numero_exterior = fields.Char(string="Número Exterior")
    numero_interior = fields.Char(string="Número Interior")
    colonia = fields.Char(string="Colonia")
    municipio = fields.Char(string="Municipio")
    estado = fields.Char(string="Estado")
    referencia_domicilio = fields.Char(string="Referencia de Domicilio")
    codigo_postal = fields.Char(string="Código Postal")

    grado_estudios = fields.Selection([
        ('ninguno', 'Ninguno'),
        ('primaria', 'Primaria'),
        ('secundaria', 'Secundaria'),
        ('preparatoria', 'Preparatoria'),
        ('tecnico', 'Técnico'),
        ('licenciatura', 'Licenciatura'),
        ('posgrado', 'Posgrado')
    ], string="Grado de Estudios")

    estado_civil = fields.Selection([
        ('soltera', 'Soltera'),
        ('casada', 'Casada'),
        ('divorciada', 'Divorciada'),
        ('viuda', 'Viuda'),
        ('union_libre', 'Unión Libre')
    ], string="Estado Civil")

    ocupacion = fields.Selection([
        ('comerciante', 'Comerciante'), ('desempleada', 'Desempleada'),
        ('estudiante', 'Estudiante'), ('empleada', 'Empleada'),
        ('hogar', 'Hogar'), ('ninguna', 'Ninguna')

    ], string="Ocupación")

    nivel_economico = fields.Selection([
        ('pobreza_extrema', 'Pobreza Extrema'),
        ('pobreza', 'Pobreza'),
        ('medio', 'Medio'),
        ('alto', 'Alto'),
        ('muy_alto', 'Muy Alto')
    ], string="Nivel Económico")

    tipo_poblacion = fields.Selection([
        ('urbana', 'Urbana'),
        ('semi_urbana', 'Semi Urbana'),
        ('rural', 'Rural')
    ], string="Tipo de población")

    # Segunda columna de pestaña "Información Particular Detallada"
    religion = fields.Selection([
        ('catolica', 'Católica'),
        ('protestante', 'Protestante'),
        ('evangelica', 'Evangélica'),
        ('judia', 'Judía'),
        ('musulmana', 'Musulmana'),
        ('otro', 'Otro')
    ], string="Religión")
    religion_otro = fields.Char(string="Especificar religión")

    migrante = fields.Boolean(string="¿Es migrante?")
    pais_de_origen = fields.Many2one('res.country', string="País de Origen")
    motivo_migracion = fields.Char(string="Motivo de Migración")
    deseo_de_migrar = fields.Boolean(string="¿Desea migrar?")
    pertenece_a_una_comunidad = fields.Boolean(string="¿Pertenece a una comunidad indígena?")
    comunidad_indigena = fields.Char(string="Comunidad Indígena")
    dialecto = fields.Char(string="Dialecto")
    especifique_dialecto = fields.Char(string="Especifique Dialecto")
    lengua_materna = fields.Char(string="Lengua Materna")
    discapacidad = fields.Boolean(string="¿Tiene alguna discapacidad?")
    tipo_discapacidad = fields.Selection([
        ('visual', 'Visual'),
        ('auditiva', 'Auditiva'),
        ('motora', 'Motora'),
        ('intelectual', 'Intelectual'),
        ('otro', 'Otro')
    ], string="Tipo de Discapacidad")

    cantidad_embarazos = fields.Integer(string="Cantidad de embarazos contando este", default=1)
    cantidad_hijos_nacidos_vivos = fields.Integer(string="Cantidad de hijos nacidos vivos")
    cantidad_hijos_nacidos_muertos = fields.Integer(string="Cantidad de hijos nacidos muertos")
    cantidad_abortos = fields.Integer(string="Cantidad de abortos")

    # === seccion acompañante pestaña "informacióno" ===
    acompanante = fields.Boolean(string="¿Tiene acompañante?")
    acompanante_nombre = fields.Char(string="Nombre del acompañante")
    acompanante_parentesco = fields.Char(string="Parentesco")

    # ===== sección referencias y familiares pestaña "información" =====

    nombre_referencia1 = fields.Char(string="Contacto de Emergencia 1")
    telefono_referencia1 = fields.Char(string="Teléfono")
    parentesco_referencia1 = fields.Char(string="Parentesco")
    nombre_referencia2 = fields.Char(string="Contacto de Emergencia 2")
    telefono_referencia2 = fields.Char(string="Teléfono")
    parentesco_referencia2 = fields.Char(string="Parentesco")


    # === PESTAÑA "CANALIZACIÓN" ===
    ingreso_por = fields.Char(string="Ingreso por", help="¿Cómo llegó a VIFAC?")
    canalizacion = fields.Selection([
        ('autoridad', 'Autoridad'),
        ('familiar', 'Familiar'),
        ('amigo', 'Amigo'),
        ('otro', 'Otro')
    ], string="Canalización", help="¿Cómo llegó a VIFAC?")
    canalizacion_otro = fields.Char(string="Especifique canalización", help="Si eligió 'Otro', especifique cómo llegó a VIFAC")
    nombre_canalizador = fields.Char(string="Nombre del canalizador", help="Nombre de la persona que canalizó a la beneficiaria")
    cargo_canalizador = fields.Char(string="Cargo del canalizador", help="Cargo de la persona que canalizó a la beneficiaria")
    numero_oficio_canalizacion = fields.Char(string="Número de oficio de canalización", help="Número de oficio de la autoridad que canalizó a la beneficiaria")

    # ==== sección seguimiento legal pestaña "canalización" ====
    tiene_carpeta_investigacion = fields.Boolean(string="¿Tiene carpeta de investigación?")
    NIC = fields.Char(string="NIC", help="Número de la carpeta de investigación criminal si aplica")
    NUC = fields.Char(string="NUC", help="Número único de caso si aplica")
    fecha_investigacion = fields.Date(string="Fecha de Investigación", help="Fecha de la carpeta de investigación si aplica")
    lugar = fields.Char(string="Lugar de Investigación", help="Lugar donde se realizó la investigación si aplica")
    delito = fields.Char(string="Delito", help="Delito relacionado con la investigación si aplica")
    numero_oficio = fields.Char(string="Número de Oficio", help="Número de oficio relacionado con la canalización")
    estatus_situacion_juridica = fields.Selection([
        ('libre', 'Libre'),
        ('detenida', 'Detenida'),
        ('procesada', 'Procesada'),
        ('sentenciada', 'Sentenciada'),
        ('libertad_condicional', 'Libertad Condicional'),
        ('otro', 'Otro')
    ], string="Estatus de la situación jurídica", help="Estado legal actual de la beneficiaria")
    persona_seguimiento_legal = fields.Char(string="Persona de seguimiento legal", help="Nombre de la persona encargada del seguimiento legal")
    telefono_seguimiento_legal = fields.Char(string="Teléfono de seguimiento legal", help="Teléfono de la persona encargada del seguimiento legal")
    telefono2_seguimiento_legal = fields.Char(string="Teléfono 2 de seguimiento legal", help="Segundo teléfono de la persona encargada del seguimiento legal")
    correo_seguimiento_legal = fields.Char(string="Correo de seguimiento legal", help="Correo electrónico de la persona encargada del seguimiento legal")
    notas_seguimiento_legal = fields.Text(string="Notas de seguimiento legal", help="Notas adicionales sobre el seguimiento legal")

    # ==== sección documentos pestaña "canalización" ====
    tiene_documentos = fields.Boolean(string="¿Tiene documentos?")
    # documento_ids = fields.One2many('beneficiarias.documento', 'beneficiaria_id', string="Documentos", help="Documentos relacionados con la beneficiaria")
    # tipo_documento = fields.Selection([
    #     ('identificacion', 'Identificación'),
    #     ('acta_nacimiento', 'Acta de Nacimiento'),
    #     ('comprobante_domicilio', 'Comprobante de Domicilio'),
    #     ('certificado_medico', 'Certificado Médico'),
    #     ('otro', 'Otro')
    # ], string="Tipo de Documento", help="Tipo de documento relacionado con la beneficiaria")

    # ==== PESTAÑA "FOTOS" =====
    foto_perfil_izquierdo = fields.Image(string="Foto Perfil Izquierdo", max_width=400, max_height=400)
    foto_frontal = fields.Image(string="Foto Frontal", max_width=400, max_height=400)
    foto_perfil_derecho = fields.Image(string="Foto Perfil Derecho", max_width=400, max_height=400)
    foto_huellas = fields.Image(string="Huellas Digitales", max_width=400, max_height=400)


    # === PESTAÑA "DETALLE DEL SERVICIO" ===
    atencion_integral_embarazo = fields.Boolean(string="Atención Integral Embarazo")
    atencion_medica = fields.Boolean(string="Atención Médica")
    atencion_psicologica = fields.Boolean(string="Atención Psicológica")
    atencion_nutricional = fields.Boolean(string="Atención Nutricional")
    apoyo_emocional = fields.Boolean(string="Apoyo Emocional")
    apoyo_especie = fields.Boolean(string="Apoyo en especie")
    aistencia_legal_adopcion = fields.Boolean(string="Asistencia Legal para Adopción")
    centro_capacitacion_formacion = fields.Boolean(string="Centro de Capacitación y Formación")
    otro = fields.Boolean(string="Otro")
    otro_detalle_servicio = fields.Char(string="Especifique otro servicio")

    # ==== PESTAÑA "FAMILIARES" ====
    # datos del padre
    padre_nombre = fields.Char(string="Nombre completo del padre")
    tiene_relacion_padre = fields.Boolean(string="¿Tiene relación con su padre?")
    direccion_padre = fields.Char(string="Dirección del padre")
    telefono_padre = fields.Char(string="Teléfono del padre")
    esta_vivo_padre = fields.Boolean(string="¿Está vivo el padre?")


    # datos de la madre
    madre_nombre = fields.Char(string="Nombre completo de la madre")
    tiene_relacion_madre = fields.Boolean(string="¿Tiene relación con su madre")
    direccion_madre = fields.Char(string="Dirección de la madre")
    telefono_madre = fields.Char(string="Teléfono de la madre")
    esta_vivo_madre = fields.Boolean(string="¿Está viva la madre?")

    # datos del tutor
    tutor_nombre = fields.Char(string="Nombre completo del tutor")
    tutor_direccion = fields.Char(string="Dirección del tutor")
    tutor_telefono = fields.Char(string="Teléfono del tutor")
    tutor_parentesco = fields.Char(string="Parentesco con la beneficiaria")
    tutor_esta_vivo = fields.Boolean(string="¿Está vivo el tutor?")

    # datos hermanos
    tiene_hermanos = fields.Boolean(string="¿Tiene hermanos?")
    # PENDIENTE TABLA DE HERMANOS

    # === PESTAÑA "HIJOS"   ===
    # PENDIENTE PESTAÑA HIJOS

    # === PESTAÑA "RELACIÓN CON EL PADRE" ===
    nombre_padre = fields.Char(string="Nombre del padre del bebé que espera")
    edad_padre = fields.Integer(string="Edad del padre")
    relacion_con_padre = fields.Selection([
        ('buena', 'Buena'),
        ('regular', 'Regular'),
        ('mala', 'Mala'),
        ('no_aplica', 'No Aplica'),
        ('otro', 'Otro')
    ], string="Relación con el padre")
    relacion_con_padre_otro = fields.Char(string="Especifique relación con el padre")
    padre_sabe_de_su_embarazo = fields.Boolean(string="¿El padre sabe de su embarazo?")
    padre_sera_notificado = fields.Boolean(string="¿Piensas informarle de tu situación?")
    padre_ha_dado_apoyo = fields.Boolean(string="¿El padre ha dado apoyo o dijo que apoyaría?")
    estado_civil_padre = fields.Selection([
        ('soltero', 'Soltero'),
        ('casado', 'Casado'),
        ('divorciado', 'Divorciado'),
        ('viudo', 'Viudo'),
        ('union_libre', 'Unión Libre')
    ], string="Estado Civil del Padre")
    padre_ocupacion = fields.Char(string="Ocupación del Padre")
    padre_grado_maximo_estudios = fields.Selection([
        ('ninguno', 'Ninguno'),
        ('primaria', 'Primaria'),
        ('secundaria', 'Secundaria'),
        ('preparatoria', 'Preparatoria'),
        ('tecnico', 'Técnico'),
        ('licenciatura', 'Licenciatura'),
        ('posgrado', 'Posgrado')
    ], string="Grado Máximo de Estudios del Padre")
    padre_tiene_adiccion = fields.Boolean(string="¿El padre tiene alguna adicción?")
    padre_tiene_adiccion_detalle = fields.Char(string="Especifique adicción del padre")
    estatura_padre = fields.Float(string="Estatura del Padre (cm)")
    complexion_padre = fields.Selection([
        ('delgada', 'Delgada'),
        ('media', 'Media'),
        ('musculosa', 'Musculosa'),
        ('obesa', 'Obesa')
    ], string="Complexión del Padre")
    numero_hijos_padre = fields.Integer(string="Número de hijos del padre")
    numero_hijos_padre_con_beneficiaria = fields.Integer(string="Número de hijos del padre contigo")
    padre_vive_con_beneficiaria = fields.Boolean(string="¿El padre vive contigo?")
    origen_padre = fields.Char(string="De dónde es originacio el padre")
    antecendentes_medicos_padre = fields.Text(string="Antecedentes médicos de importancia del padre")
    en_caso_de_haber_migrado_padre = fields.Boolean(string="¿El padre ha migrado?")
    padre_pais_migracion = fields.Char(string="País al que migró el padre")
    lugar_residencia_padre = fields.Char(string="Lugar de residencia actual del padre")
 

    # === PESTAÑA "DATOS DE VIOLENCIA" ===
    violacion = fields.Boolean(string="¿Ha sido víctima de violación?")
    violencia_intrafamiliar = fields.Boolean(string="¿Ha sufrido violencia intrafamiliar por parte de algún familiar o pareja?")
    quien_fue_el_agresor = fields.Char(string="¿Quién fue el agresor?")

    # Título "Qué tipo de violencia sufriste"
    # lista para seleccionar 1 o varios tipos de violencia

    tipo_violencia_fisica = fields.Boolean(string="Violencia física")
    tipo_violencia_psicologica = fields.Boolean(string="Violencia psicológica")
    tipo_violencia_sexual = fields.Boolean(string="Violencia sexual")
    tipo_violencia_economica = fields.Boolean(string="Violencia económica")
    tipo_violencia_patrimonial = fields.Boolean(string="Violencia patrimonial")
    tipo_violencia_otro_seleccion = fields.Boolean(string="Otro")
    tipo_violencia_otro = fields.Boolean(string="Especifique otro tipo de violencia")

    # educación sexual
    educacion_sexual = fields.Boolean(string="¿Has recibido educación sexual?")
    educacion_sexual_detalle = fields.Text(string="¿Quién te la brindó y en dónde? (opcional)")
    embarazo_actual_consecuencia_de_violacion = fields.Boolean(string="¿El embarazo actual es consecuencia de una violación?")
    ha_iniciado_carpeta_investigacion = fields.Boolean(string="¿Has iniciado una carpeta de investigación por la violencia sufrida?")
    carpeta_investigacion_numero = fields.Char(string="Número de la carpeta de investigación")
    carpeta_investigacion_fecha = fields.Date(string="Fecha de la carpeta de investigación")
    carpeta_investigacion_lugar = fields.Char(string="Lugar de la carpeta de investigación")

    # === PESTAÑA "ANTECEDENTES MEDICOS" ===
    antecedentes_medicos = fields.Text(string="Antecedentes Médicos", help="Antecedentes médicos relevantes de la beneficiaria")
    enfermedades_cronicas = fields.Text(string="Enfermedades Crónicas", help="Enfermedades crónicas que padece la beneficiaria")
    alergias = fields.Text(string="Alergias", help="Alergias conocidas de la beneficiaria")
    medicamentos_actuales = fields.Text(string="Medicamentos Actuales", help="Medicamentos que está tomando actualmente la beneficiaria")
    cirugias_previas = fields.Text(string="Cirugías Previas", help="Cirugías que ha tenido la beneficiaria en el pasado")
    vacunas = fields.Text(string="Vacunas", help="Vacunas recibidas por la beneficiaria")
    tipo_sangre = fields.Selection([
        ('a+', 'A+'),
        ('a-', 'A-'),
        ('b+', 'B+'),
        ('b-', 'B-'),
        ('ab+', 'AB+'),
        ('ab-', 'AB-'),
        ('o+', 'O+'),
        ('o-', 'O-')
    ], string="Tipo de Sangre")
    enfermedades_familiares = fields.Text(string="Enfermedades Familiares", help="Enfermedades hereditarias o familiares relevantes")
    antecedentes_quirurgicos = fields.Text(string="Antecedentes Quirúrgicos", help="Antecedentes quirúrgicos relevantes de la beneficiaria")
    tiene_donador = fields.Boolean(string="¿Tiene donador de sangre?")
    donador_nombre = fields.Char(string="Nombre del Donador", help="Nombre de la persona que puede donar sangre en caso de emergencia")
    donador_telefono = fields.Char(string="Teléfono del Donador", help="Teléfono de contacto del donador de sangre")
    donador_relacion = fields.Char(string="Relación con el Donador", help="Relación de la beneficiaria con el donador de sangre")
    

    # === PESTAÑA "MEDIOS DE COMUNICACIÓN" ===
    # título "¿Cómo te enteraste de VIFAC?"
    # selector de uno o varios medios de comunicación: Televisión, Radio, Volante, Poster, Periódico, Espectacular, Iglesia, Institución, Internet, Red Social, Recomendación, Ex Beneficiaria, Otro medio
    television = fields.Boolean(string="Televisión")
    television_canal = fields.Char(string="Canal de Televisión", help="Si se enteró por televisión, especifique el canal")
    radio = fields.Boolean(string="Radio")
    radio_estacion = fields.Char(string="Estación de Radio", help="Si se enteró por radio, especifique la estación")
    volante = fields.Boolean(string="Volante")
    volante_detalle = fields.Char(string="Detalle del Volante", help="Si se enteró por volante, especifique el contenido o lugar donde lo vio")
    poster = fields.Boolean(string="Poster")
    poster_detalle = fields.Char(string="Detalle del Poster", help="Si se enteró por poster, especifique en dónde lo vio")
    periodico = fields.Boolean(string="Periódico")
    periodico_detalle = fields.Char(string="Detalle del Periódico", help="Si se enteró por periódico, especifique el nombre o sección")
    espectacular = fields.Boolean(string="Espectacular")
    espectacular_detalle = fields.Char(string="Detalle del Espectacular", help="Si se enteró por espectacular, especifique el lugar o contenido")
    iglesia = fields.Boolean(string="Iglesia")
    iglesia_detalle = fields.Char(string="Detalle de la Iglesia", help="Si se enteró por iglesia, especifique el nombre o ubicación")
    institucion = fields.Boolean(string="Institución")
    institucion_detalle = fields.Char(string="Detalle de la Institución", help="Si se enteró por una institución, especifique cuál")
    internet = fields.Boolean(string="Internet")
    internet_detalle = fields.Char(string="Detalle de Internet", help="Si se enteró por internet, especifique el sitio web o enlace")
    red_social = fields.Boolean(string="Red Social")
    red_social_detalle = fields.Char(string="Detalle de la Red Social", help="Si se enteró por red social, especifique cuál")
    recomendacion = fields.Boolean(string="Recomendación")
    recomendacion_detalle = fields.Char(string="Detalle de la Recomendación", help="Si se enteró por recomendación, especifique quién le recomendó VIFAC")
    ex_beneficiaria = fields.Boolean(string="Ex Beneficiaria")
    ex_beneficiaria_fecha = fields.Date(string="Fecha de contacto con Ex Beneficiaria", help="Fecha en que se enteró por una ex beneficiaria")
    otro_medio = fields.Boolean(string="Otro Medio")
    otro_medio_detalle = fields.Char(string="Detalle de Otro Medio", help="Si se enteró por otro medio, especifique cuál")


    # detalles del contacto con VIFAC
    contacto_vifac = fields.Selection([
        ('telefono', 'Teléfono'),
        ('correo', 'Correo Electrónico'),
        ('visita', 'Visita Personal'),
        ('otro', 'Otro')
    ], string="Contacto con VIFAC", help="¿Cómo fue el contacto inicial con VIFAC?")

    # en caso de habar sido a través de una institución, especifique
    nombre_contacto_institucion = fields.Char(string="Especifique la institución", help="Si el contacto fue a través de una institución, especifique cuál")
    contacto_institucion = fields.Char(string="Nombre del contacto en la institución", help="Nombre de la persona de contacto en la institución")


    # === PESTAÑA "DOCUMENTACIÓN" ===
    # PENDIENTE PESTAÑA DOCUMENTACIÓN



    # === PESTAÑA "TRASLADOS" ===
    # PENDIENTE PESTAÑA TRASLADOS


    # === PESTAÑA "PROYECTO DE VIDA" ===
    reaccion_confirmacion_embarazo = fields.Selection([
        ('Quise abortar', 'Quise abortar'),
        ('Quise tener al bebé', 'Quise tener al bebé'),
        ('No sabía qué hacer', 'No sabía qué hacer'),
        ('Otro', 'Otro')
    ], string="Reacción al confirmar el embarazo", help="¿Cómo reaccionaste al confirmar tu embarazo?")
    intento_aborto = fields.Boolean(string="¿Intentaste abortar?")
    medio_intento_aborto = fields.Char(string="Medio del intento de aborto", help="¿Qué medio utilizaste para intentar abortar?")

    recibe_apoyo = fields.Boolean(string="Obtuviste apoyo de algún familiar, amigo o conocido", help="¿Recibiste apoyo de alguien durante tu embarazo?")
    especifique_apoyo = fields.Text(string="Especifique el apoyo recibido", help="Si recibiste apoyo, especifica quién te apoyó y cómo")

    sabe_que_es_adocion = fields.Boolean(string="¿Sabes qué es la adopción?")
    conoce_adopcion = fields.Boolean(string="¿Conoces el proceso de adopción?")
    te_gustaria_conocer = fields.Boolean(string="¿Te gustaría conocer más sobre el proceso de adopción?")
    desea_dar_a_adopcion = fields.Boolean(string="¿Deseas dar a tu bebé en adopción?")

    # === PESTAÑA "DATOS DEL PARTO" ===
    fecha_egreso_hospital = fields.Date(string="Fecha de egreso del hospital", help="Fecha en que la beneficiaria fue dada de alta del hospital tras el parto")
    hospital_parto = fields.Char(string="Nombre del hospital")
    parto_multiple = fields.Boolean(string="¿Tuviste un parto múltiple?")

    # === PESTAÑA "ALTA" ===

    fecha_alta = fields.Date(string="Fecha de Alta", help="Fecha en que la beneficiaria fue dada de alta de VIFAC")
    persona_recoge = fields.Char(string="Persona que recoge a la beneficiaria", help="Nombre de la persona que recoge a la beneficiaria al momento de su alta")
    # documento_identificacion_persona_recoge = fields.Char(string="Documento de identificación de la persona que recoge", help="Tipo de documento de identificación de la persona que recoge a la beneficiaria")
    identificacion_persona_recoge = fields.Binary(string="Identificación de la persona que recoge", help="Documento de identificación de la persona que recoge a la beneficiaria al momento de su alta")
    relacion_persona_recoge = fields.Char(string="Relación de la persona que recoge con la beneficiaria", help="Relación de la persona que recoge a la beneficiaria al momento de su alta")
    telefono_persona_recoge = fields.Char(string="Teléfono de la persona que recoge", help="Teléfono de la persona que recoge a la beneficiaria al momento de su alta")
    domicilio_persona_recoge = fields.Char(string="Domicilio de la persona que recoge", help="Domicilio de la persona que recoge a la beneficiaria al momento de su alta")

    se_retiro_despues_de_dar_a_luz = fields.Boolean(string="¿Se retiró después de dar a luz?", help="Indica si la beneficiaria se retiró de VIFAC después de dar a luz")
    se_retiro_con_bebe = fields.Boolean(string="¿Se retiró con el bebé?", help="Indica si la beneficiaria se retiró de VIFAC con su bebé")

    # campo para captar la información:  En caso de retirarse en permiso para regresar y concluir trámite de entrega voluntaria para adopción, favor de poner la fecha en la que concluye la entrega voluntaria(fecha de audiencia en el juzgado)
    se_retira_con_permiso_regreso_entrega_voluntaria = fields.Boolean(string="¿Se retira con permiso para regresar y concluir trámite de entrega voluntaria para adopción?", help="Indica si la beneficiaria se retira con permiso para regresar y concluir el trámite de entrega voluntaria para adopción")
    fecha_conclusion_entrega_voluntaria = fields.Date(string="Fecha de conclusión de entrega voluntaria", help="Fecha en la que concluye el trámite de entrega voluntaria para adopción (fecha de audiencia en el juzgado)")
    nombre_testigo1 = fields.Char(string="Nombre del testigo 1", help="Nombre del primer testigo que firma el acta de alta")
    nombre_testigo2 = fields.Char(string="Nombre del testigo 2", help="Nombre del segundo testigo que firma el acta de alta")
    autorizado_por = fields.Many2one('res.users', string='Autorizado por', tracking=True)


    # === RELACIONES ===
    # relación con usuario encargado para ser asignada
    asignado_a_id = fields.Many2one('res.users', string='Asignado a', tracking=True)

    hijos_ids = fields.One2many('beneficiarias.hijo', 'beneficiaria_id')
    bebe_ids = fields.One2many('beneficiarias.bebe', 'beneficiaria_id')
    hermanos_ids = fields.One2many('beneficiarias.hermano', 'beneficiaria_id', string='Hermanos')
    traslado_ids = fields.One2many('beneficiarias.traslados', 'beneficiaria_id', string='Traslados')
    taller_ids = fields.One2many('beneficiarias.taller', 'beneficiaria_id', string='Talleres')
    valoracion_ids = fields.One2many(
    'beneficiarias.valoracion', 'beneficiaria_id', string='Valoraciones'
    )
    documentos_ids = fields.One2many(
        'beneficiarias.documento', 'beneficiaria_id', string='Documentos',
        domain=[('tipo_relacion', '=', 'beneficiaria')]
    )
    stage_id = fields.Many2one(
    'beneficiarias.stage',
    string="Etapa",
    tracking=True,
    default=lambda self: self.env['beneficiarias.stage'].search([], limit=1, order='sequence'),
    group_expand='_read_group_stage_ids'
    )


    # === CÁLCULOS Y VALIDACIONES ===

    def name_get(self):
        result = []
        for rec in self:
            nombre = rec.nombre_completo or rec.nombre or f'ID {rec.id}'
            result.append((rec.id, nombre))
        return result


    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        # Hace que aparezcan todas las etapas en la vista kanban aunque no haya registros
        return stages.search([])

    @api.depends('nombre', 'apellido_paterno', 'apellido_materno')
    def _compute_nombre_completo(self):
        for rec in self:
            partes = filter(None, [rec.nombre, rec.apellido_paterno, rec.apellido_materno])
            rec.nombre_completo = ' '.join(partes)

    @api.depends('fecha_nacimiento', 'fecha_ingreso')
    def _compute_edad_ingreso(self):
        for record in self:
            if record.fecha_nacimiento and record.fecha_ingreso:
                delta = record.fecha_ingreso - record.fecha_nacimiento
                record.edad_ingreso = delta.days // 365
            else:
                record.edad_ingreso = 0

    @api.depends('fum_time')
    def _compute_embarazo_info(self):
        for rec in self:
            if rec.fum_time:
                # Fecha probable de parto
                rec.fecha_probable_de_parto = rec.fum_time + timedelta(days=280)
                # Cálculo de semanas de gestación y meses de embarazo
                today = fields.Date.context_today(rec)
                days_pregnant = (today - rec.fum_time).days
                rec.semanas_gestacion = days_pregnant // 7 if days_pregnant >= 0 else 0
                rec.meses_embarazo = days_pregnant // 30 if days_pregnant >= 0 else 0
            else:
                rec.fecha_probable_de_parto = False
                rec.semanas_gestacion = 0
                rec.meses_embarazo = 0

    @api.depends('edad_ingreso')
    def _compute_rango_edad(self):
        for rec in self:
            edad = rec.edad_ingreso or 0
            if edad < 12:
                rec.rango = 'm12'
            elif 12 <= edad <= 15:
                rec.rango = 'm12a15'
            elif 16 <= edad <= 18:
                rec.rango = 'm16a18'
            elif 19 <= edad <= 21:
                rec.rango = 'm19a21'
            elif 22 <= edad <= 25:
                rec.rango = 'm22a25'
            elif 26 <= edad <= 28:
                rec.rango = 'm26a28'
            elif 29 <= edad <= 32:
                rec.rango = 'm29a32'
            elif 33 <= edad <= 40:
                rec.rango = 'm33a40'
            elif edad > 40:
                rec.rango = 'ma40'
            else:
                rec.rango = False

    @api.constrains('curp')
    def _check_curp(self):
        for rec in self:
            if rec.curp:
                curp = rec.curp.strip().upper()
                curp_regex = r'^([A-Z][AEIOUX][A-Z]{2}\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])[HM](?:AS|B[CS]|C[CLMSH]|D[FG]|G[TR]|HG|JC|M[CNS]|N[ETL]|OC|PL|Q[TR]|S[PLR]|T[CSL]|VZ|YN|ZS)[B-DF-HJ-NP-TV-Z]{3}[A-Z\d])(\d)$'
                if not re.fullmatch(curp_regex, curp):
                    raise ValidationError(
                        "El CURP '%s' no es válido. "
                        "Debe cumplir con el formato oficial." % rec.curp
                    )
                
    @api.constrains('rfc')
    def _check_rfc(self):
        for rec in self:
            if rec.rfc:
                rfc = rec.rfc.strip().upper()
                rfc_regex = r'^([A-ZÑ\x26]{3,4}([0-9]{2})(0[1-9]|1[0-2])(0[1-9]|1[0-9]|2[0-9]|3[0-1])([A-Z]|[0-9]){2}([A]|[0-9]){1})$'
                if not re.fullmatch(rfc_regex, rfc):
                    raise ValidationError(
                        "El RFC '%s' no es válido. Debe cumplir con el formato oficial." % rec.rfc
                    )

    @api.constrains('telefono', 'telefono_celular')
    def _check_telefono_numerico(self):
        for rec in self:
            for field_name in ['telefono', 'telefono_celular']:
                value = getattr(rec, field_name)
                if value:
                    if not value.isdigit():
                        raise ValidationError("El campo %s solo debe contener números." % rec._fields[field_name].string)
                    if len(value) > 10:
                        raise ValidationError("El campo %s debe tener como máximo 10 dígitos." % rec._fields[field_name].string)

    @api.onchange('atencion_integral_embarazo')
    def _onchange_atencion_integral_embarazo(self):
        if self.atencion_integral_embarazo:
            self.atencion_medica = True
            self.atencion_psicologica = True
            self.atencion_nutricional = True
            self.apoyo_emocional = True
            self.apoyo_especie = True
            self.aistencia_legal_adopcion = True
            self.centro_capacitacion_formacion = True

    @api.onchange('atencion_integral_embarazo')
    def _onchange_atencion_integral_embarazo(self):
        if not self.atencion_integral_embarazo:
            self.atencion_medica = False
            self.atencion_psicologica = False
            self.atencion_nutricional = False
            self.apoyo_emocional = False
            self.apoyo_especie = False
            self.asistencia_legal_adopcion = False
            self.centro_capacitacion_formacion = False

    @api.onchange('pais_nacimiento')
    def _onchange_pais_nacimiento(self):
        self.estado_nacimiento = False
