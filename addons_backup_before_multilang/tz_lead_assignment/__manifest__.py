{
    "name": "TZ Lead Assignment",
    "version": "1.0.0",
    "summary": "Automatic round-robin lead assignment",
    "category": "Sales/CRM",
    "author": "Techzilla Global",
    "depends": [
        "crm",
        "tz_crm_base",
        "tz_realestate_leads"
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/assignment_rule_views.xml",
        "views/crm_lead_views.xml",
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}