{
    "name": "TZ Commission",
    "version": "1.0.0",
    "summary": "Agent commission tracking for real estate deals",
    "category": "Sales/CRM",
    "author": "Techzilla Global",
    "depends": [
        "crm",
        "contacts",
        "tz_crm_base",
        "tz_realestate_leads",
        "tz_property_inventory"
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/sequence.xml",
        "views/commission_views.xml",
        "views/crm_lead_views.xml",
        "views/menu.xml",
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}