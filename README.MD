#   <img src="/static/description/favicon.png" alt="Logo Pridecta" width="40" height="40" style="border-radius:50%; vertical-align:middle; margin-left:10px;"/> Odoo 17 – Módulo de Registro de Beneficiarias para VIFAC México
![Logo VIFAC](/static/description/logo-vifac-sin_fondo.png)

## 1. Descripción 📋

Este módulo para **Odoo 17 Community** fue creado especialmente para **VIFAC México**, con el objetivo de **agilizar el registro y seguimiento integral** de mujeres embarazadas en situación vulnerable (“Beneficiarias”).  
Centraliza datos personales, control por etapas, evidencia documental, valoraciones, talleres, traslados y red familiar, ofreciendo una vista 360° del expediente.

---

## 2. Estructura del módulo 📂

```text
beneficiarias/
├── .gitattributes
├── .gitignore
├── README.MD
├── __init__.py
├── __manifest__.py
├── data/
│   └── stages.xml
├── models/
│   ├── __init__.py
│   ├── bebes/
│   │   ├── __init__.py
│   │   └── bebe.py
│   ├── beneficiarias/
│   │   ├── __init__.py
│   │   ├── beneficiaria.py
│   │   ├── geo_city.py
│   │   ├── hermanos.py
│   │   ├── preview_image_wizard.py
│   │   ├── stage.py
│   │   ├── taller.py
│   │   ├── traslados.py
│   │   └── valoracion.py
│   ├── documentos/
│   │   ├── __init__.py
│   │   └── documento.py
│   ├── hijos/
│   │   ├── __init__.py
│   │   └── hijo.py
│   └── padres_adoptivos/
│       ├── __init__.py
│       └── papas_adoptivos.py
├── security/
│   ├── beneficiarias_security.xml
│   └── ir.model.access.csv
├── static/
│   ├── description/
│   │   ├── icon.png
│   │   └── icon2.png
│   └── src/
│       └── css/
│           └── beneficiarias_tabs.css
└── views/
    ├── bebes/
    │   └── bebe_views.xml
    ├── beneficiaria/
    │   ├── beneficiaria_form.xml
    │   ├── beneficiaria_kanban.xml
    │   ├── beneficiaria_search_view.xml
    │   ├── beneficiaria_tree.xml
    │   ├── documento_views.xml
    │   ├── preview_image_wizard_views.xml
    │   └── stage_views.xml
    ├── hijos/
    │   └── hijo_views.xml
    ├── papas_adoptivos/
    │   └── papas_adoptivos_views.xml
    └── beneficiarias_views.xml
```

---

## 3. Compatibilidad y dependencias 🧩

- **Versión de Odoo:** 17.0 (Community)  
- **Dependencias:** `base`, `web`  
- **Licencia:** LGPL-3 (definida en `__manifest__.py`)  
- **Activos web:** CSS para pestañas y grilla de imágenes (`static/src/css/beneficiarias_tabs.css`)

---

## 4. Instalación 🚀

1. Copia la carpeta `beneficiarias/` dentro de tu ruta de **addons**.  
2. Inicia Odoo con la ruta de addons correspondiente.  
3. Activa **Modo Desarrollador**.  
4. Ve a **Apps** → **Actualizar lista de aplicaciones**.  
5. Busca **“Beneficiarias”** e instala.

---

## 5. Configuración inicial ⚙️

El módulo crea el catálogo de **Etapas** (`beneficiarias.stage`) desde `data/stages.xml`:
- Pre-Ingreso → En Atención → Seguimiento Post Atención → Conclusión del servicio.  
Estas etapas alimentan el **statusbar** y la vista **kanban** del expediente.

---

## 6. Modelos y funcionalidad detallada 🏗️

### 6.1. Expediente principal — `beneficiarias.beneficiaria`
- **Identificación y básicos:** nombre completo, **CURP**, **RFC**, fecha de nacimiento e **ingreso**, **edad_ingreso** y **rango** etario.  
- **Contacto y contexto:** teléfonos, correo, escolaridad, ocupación, estado civil, religión, nacionalidad, vivienda, referencias.  
- **Embarazo y atención:** FUM, semanas, controles prenatales, parto, apoyos médicos/psicológicos/nutricionales/legales.  
- **Imágenes:** 4 fotos (perfil izq., frontal, perfil der., huellas) con **vista previa** vía wizard.  
- **Pipeline/Etapas:** relación `stage_id`, vista kanban y barra de estado clicable.  
- **Relaciones:** hijos, bebés, hermanos, traslados, talleres, valoraciones.  
- **Validaciones:** CURP, RFC y teléfonos.  
- **Vistas:** formulario con pestañas y grilla de imágenes, kanban con foto circular, lista, búsqueda avanzada.

### 6.2. Documentación — `beneficiarias.documento`
- Contenedor de archivos adjuntos (PDF/imagen).  
- Asociado a beneficiaria, hijo, bebé, taller o valoración.  
- Automatiza alta desde talleres y valoraciones.  
- Acciones para abrir en modal.

### 6.3. Hijos — `beneficiarias.hijo`
- Datos personales, escolares y acompañamiento.  
- Documentos: acta, CURP, cartilla, docs médicos/escolares.  
- Relación con beneficiaria y documentos.  

### 6.4. Bebés — `beneficiarias.bebe`
- Datos de nacimiento, salud, lactancia, egreso y registros.  
- Relación con beneficiaria, papás adoptivos y documentos.

### 6.5. Padres adoptivos — `beneficiarias.papas_adoptivos`
- Datos de padre/madre adoptivos.  
- Relación con `beneficiarias.bebe`.

### 6.6. Valoraciones — `beneficiarias.valoracion`
- Valoraciones psicológicas, socioeconómicas, médicas y pedagógicas.  
- Archivos adjuntos que generan documentos automáticamente.  

### 6.7. Talleres — `beneficiarias.taller`
- Cursos y capacitaciones.  
- Genera automáticamente documento de certificado.

### 6.8. Traslados — `beneficiarias.traslados`
- Registro de movimientos de beneficiaria entre sedes.  

### 6.9. Hermanos — `beneficiarias.hermano`
- Datos de hermanos y validación de teléfonos.  

### 6.10. Etapas — `beneficiarias.stage`
- Define pipeline (Pre-Ingreso, Atención, Seguimiento, Conclusión).  

### 6.11. Catálogo ciudades — `geo.city`
- Relación ciudad → estado → país.  
- Preparado para domicilios, aún no usado en vistas.  

### 6.12. Wizard de imágenes — `preview.image.wizard`
- Popup transitorio para previsualizar imágenes en alta resolución.

---

## 7. Vistas y navegación 🧭

- **Menú principal:** Beneficiarias.  
- **Submenús:** Registro, Hijos, Bebés, Padres adoptivos, Etapas.  
- **Vistas:** Formulario, Kanban, Lista, Búsqueda avanzada, Modal de documentos.

---

## 8. Seguridad 🔒

- Accesos CRUD abiertos a `base.group_user` en todos los modelos.  
- `beneficiarias_security.xml` preparado para extensiones.

---

## 9. Diagrama ASCII — Modelo de datos 🧩

```text
                                     ┌───────────────────────┐
                                     │   beneficiarias.stage │
                                     └───────────┬───────────┘
                                                 │  *..1  (statusbar/kanban)
                           ┌─────────────────────▼─────────────────────┐
                           │         beneficiarias.beneficiaria        │
                           │  (expediente: datos, CURP/RFC, fotos,     │
                           │   embarazo, ingreso/egreso, seguimiento)  │
                           └───┬──────────┬──────────┬──────────┬──────┬─────────┐
                               │1..*      │1..*      │1..*      │1..*  │1..*     │1..*
                               │          │          │          │      │         │
                     ┌─────────▼───┐  ┌───▼─────────┐  ┌───────▼──────┐ ┌───────▼───────┐ ┌────────▼────────┐
                     │ benefic.    │  │ benefic.     │  │ benefic.     │ │ benefic.      │ │ benefic.        │
                     │   hijo      │  │    bebe      │  │   hermano     │ │  traslados     │ │   taller         │
                     └──────┬──────┘  └────┬─────────┘  └──────────────┘ └───────────────┘ └────────┬────────┘
                            │1..*          │1..*                               │                     │1..*
                            │              │                                   │                     │
                        ┌───▼────────┐  ┌──▼──────────────┐                   │                 ┌───▼────────┐
                        │ documento  │  │ papas_adoptivos │                   │                 │ documento  │
                        │ (hijo)     │  └─────────────────┘                   │                 │ (taller)   │
                        └────────────┘         ▲                               │                 └────────────┘
                                               │                               │
                        ┌──────────────────────┴──────────────────────┐        │
                        │           documento (bebe)                  │        │
                        └─────────────────────────────────────────────┘        │
                                                                               │
                                 ┌──────────────────────────────────────────────┘
                                 │
                           ┌─────▼─────────┐       1..*        ┌──────────────┐
                           │ beneficiarias │◄──────────────────│ documento    │
                           │  .valoracion  │                   │ (valoración) │
                           └───────────────┘                   └──────────────┘

Extras/auxiliares:
- preview.image.wizard (Transient) ← se abre desde beneficiaria para ver fotos
- geo.city → catálogo de ciudades (no referenciado aún en formularios)
- Relaciones externas típicas: res.country/state, res.users (asignados), etc.
```

---

## 10. Créditos ✍️

- **Autor:** Esteban Viniegra Pérez Olagaray  
  <img src="/static/description/Esteban_Viniegra.jpeg" alt="Foto Esteban" width="40" height="40" style="border-radius:50%; vertical-align:middle; margin-left:10px;"/>

- **Compañía:** Pridecta  
  <img src="/static/description/favicon.png" alt="Logo Pridecta" width="40" height="40" style="border-radius:50%; vertical-align:middle; margin-left:10px;"/>

- **Sitio:** https://pridecta.es  
- **Licencia:** LGPL-3

--- 

> **Tip de uso:** desde **Beneficiarias → Registro de Beneficiarias**, crea un expediente, adjunta fotos, registra hijos/bebés, añade **Valoraciones** y **Talleres**; los **Documentos** se generan y pueden **previsualizarse** en modal.