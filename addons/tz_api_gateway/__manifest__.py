{
    "name": "TZ API Gateway",
    "version": "1.0.0",
    "summary": "External API gateway for Techzilla CRM",
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
        "views/api_config_views.xml",
        "views/menu.xml",
	"views/api_log_views.xml",
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}