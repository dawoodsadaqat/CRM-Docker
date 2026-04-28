{
    'name': 'Techzilla Real Estate CRM',
    'version': '17.0.1.0.0',
    'summary': 'Custom CRM extensions for Techzilla real estate workflows',
    'category': 'Sales/CRM',
    'author': 'Techzilla',
    'license': 'LGPL-3',
    'depends': ['crm', 'mail', 'contacts', 'calendar', 'sales_team'],
    'data': [
        'security/ir.model.access.csv',
        'data/crm_stage_data.xml',
        'data/mail_activity_type_data.xml',
        'views/crm_lead_views.xml',
    ],
    'installable': True,
    'application': False,
}
