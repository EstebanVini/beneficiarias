# beneficiarias/__manifest__.py
{
    'name': 'Beneficiarias',
    'version': '1.0',
    'summary': 'Gestión de Beneficiarias',
    'category': 'Custom',
    'author': 'Esteban Viniegra Pérez Olagaray | Pridecta',
    'website': 'https://pridecta.com',
    'license': 'LGPL-3',
    'depends': ['base' , 'web'],
    'data': [
        'security/beneficiarias_security.xml',
        'security/ir.model.access.csv', 
        'views/beneficiaria_views.xml',
        'views/beneficiaria_form.xml',
        'views/stage_views.xml',
        'views/beneficiaria_kanban.xml',
        'data/stages.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'beneficiarias/static/src/css/beneficiarias_tabs.css',
        ],
    },
    'icon': 'beneficiarias/static/description/icon.svg',
    'installable': True,
    'application': True,  
}
