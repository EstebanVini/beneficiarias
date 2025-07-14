# 📦 Odoo 17 – Módulo de Registro de Beneficiarias para VIFAC México

## 1. Descripción 📋

Este módulo para **Odoo 17 Community** fue creado especialmente para **VIFAC México**, una organización privada sin fines de lucro fundada en enero de 1985 (legalizada el 31 de enero de 1985) por María Guadalupe Mariscal de Vilchis, enfermera comprometida con brindar alternativas a mujeres embarazadas en situación vulnerable :contentReference[oaicite:1]{index=1}.

Con más de **40 años de trayectoria**, VIFAC ofrece servicios gratuitos como:
- Alojamiento temporal,
- Atención médica y psicológica,
- Clases y talleres certificados (estilismo, corte y confección, atención a comensales...),
- Capacitación en valores y pláticas motivacionales :contentReference[oaicite:2]{index=2}.

Actualmente cuenta con una red de **37 centros** en 25 estados de México, y presencia incluso en Brownsville, Texas :contentReference[oaicite:3]{index=3}, habiendo beneficiado a **más de un millón de personas** a través de sus servicios :contentReference[oaicite:4]{index=4}.

✨ **Objetivo del módulo**: agilizar el registro y seguimiento de beneficiarias dentro del proceso integral que realiza VIFAC, alineando tecnología y misión social.

---

## 2. Estructura del módulo 📂

```text
beneficiarias/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── beneficiaria.py
├── views/
│   ├── beneficiaria_form.xml
│   ├── beneficiaria_tree.xml
│   └── stage_views.xml
├── security/
│   ├── ir.model.access.csv
│   └── security.xml
└── data/
    └── stage_data.xml
