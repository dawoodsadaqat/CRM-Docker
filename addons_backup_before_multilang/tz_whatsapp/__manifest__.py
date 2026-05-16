{
    "name": "TZ WhatsApp",
    "version": "1.0.0",
    "summary": "WhatsApp message tracking for CRM leads",
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
        "views/whatsapp_message_views.xml",
        "views/crm_lead_views.xml",
        "views/menu.xml",
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}