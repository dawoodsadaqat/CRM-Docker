{
    "name": "TZ Property Inventory",
    "version": "1.0.0",
    "summary": "Property projects, buildings, units, and listings",
    "category": "Sales/CRM",
    "author": "Techzilla Global",
    "depends": [
        "base",
        "contacts",
	"crm",
        "tz_crm_base",
        "tz_realestate_leads"
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/property_project_views.xml",
        "views/property_building_views.xml",
        "views/property_unit_views.xml",
        "views/property_listing_views.xml",
	"views/crm_lead_matching_views.xml",
        "views/menu.xml",
	
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}