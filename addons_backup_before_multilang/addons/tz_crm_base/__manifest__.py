{
    "name": "TZ CRM Base",
    "version": "1.0.0",
    "summary": "Base configuration for Techzilla Real Estate CRM",
    "category": "Sales/CRM",
    "author": "Techzilla Global",
    "depends": ["base", "crm", "contacts"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
	"views/crm_lead_source_views.xml",
	"views/res_users_role_filter_views.xml",
        "views/menu.xml",
    ],
    "installable": True,
    "application": True,
    "license": "LGPL-3",
}