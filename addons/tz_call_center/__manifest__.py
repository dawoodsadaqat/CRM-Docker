{
    "name": "TZ Call Center",
    "version": "1.0.0",
    "summary": "Call logs and call status tracking for CRM leads",
    "category": "Sales/CRM",
    "author": "Techzilla Global",
    "depends": [
        "crm",
        "contacts",
        "tz_crm_base",
        "tz_realestate_leads"
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/sequence.xml",
        "views/call_log_views.xml",
        "views/crm_lead_views.xml",
        "views/menu.xml",
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}