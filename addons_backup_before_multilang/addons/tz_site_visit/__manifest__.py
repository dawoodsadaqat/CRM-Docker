{
    "name": "TZ Site Visit",
    "version": "1.0.0",
    "summary": "Manage real estate site visits linked to CRM leads",
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
    "views/site_visit_views.xml",
    "views/crm_lead_views.xml",
    "views/menu.xml",
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}