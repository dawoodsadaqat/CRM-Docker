{
    "name": "TZ Dashboard",
    "version": "1.0.0",
    "summary": "Management dashboard for Techzilla CRM",
    "category": "Sales/CRM",
    "author": "Techzilla Global",
    "depends": [
        "crm",
        "tz_crm_base",
        "tz_realestate_leads",
        "tz_site_visit",
        "tz_commission"
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/dashboard_views.xml",
 	"views/crm_lead_conversion_views.xml",
        "views/menu.xml",
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}