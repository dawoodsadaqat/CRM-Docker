{
    "name": "TZ Commission",
    "version": "17.0.1.0.0",
    "summary": "Advanced commission management for real estate CRM deals",
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