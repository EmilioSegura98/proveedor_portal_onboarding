{
    'name': 'Proveedor Portal Onboarding',
    'version': '1.0',
    'author': 'Morphology Consulting',
    'summary': 'Automatiza el onboarding de proveedores en Odoo',
    'depends': [
        'base',
        'contacts',
        'mail',
        'portal',
        'sign',
        'documents',
    ],
    'data': [
        'data/email_template.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
