# beneficiarias/__manifest__.py
{
    'name': 'Beneficiarias',
    'version': '1.0',
    'summary': 'Gestión de Beneficiarias',
    'category': 'Custom',
    'author': 'Esteban Viniegra Pérez Olagaray | Pridecta',
    #'website': 'https://pridecta.com',
    'license': 'LGPL-3',
    'depends': ['base' , 'web'],
    'data': [
        'security/beneficiarias_security.xml',
        'security/ir.model.access.csv', 
        'views/beneficiarias_views.xml',
        'views/beneficiaria/beneficiaria_form.xml',
        'views/beneficiaria/beneficiaria_tree.xml',
        'views/beneficiaria/beneficiaria_search_view.xml',
        'views/beneficiaria/stage_views.xml',
        'views/beneficiaria/beneficiaria_kanban.xml',
        'views/beneficiaria/documento_views.xml',
        'views/hijos/hijo_views.xml',
        'views/bebes/bebe_views.xml',
        'views/papas_adoptivos/papas_adoptivos_views.xml',
        'data/stages.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'beneficiarias/static/src/css/beneficiarias_tabs.css',
        ],
    },
    'icon': 'beneficiarias/static/description/icon.png',
    'installable': True,
    'application': True,  
}
