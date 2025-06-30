# beneficiarias/__manifest__.py
{
    'name': 'Beneficiarias',
    'version': '1.0',
    'summary': 'Gestión de Beneficiarias',
    'category': 'Custom',
    'author': 'Esteban Viniegra Pérez Olagaray | Pridecta',
    'website': 'https://pridecta.com',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [
        'security/beneficiarias_security.xml',
        'views/beneficiaria_views.xml',
        'security/ir.model.access.csv', 
    ],
    'icon': 'beneficiarias/static/description/icon.svg',
    'installable': True,
    'application': True,  
}
