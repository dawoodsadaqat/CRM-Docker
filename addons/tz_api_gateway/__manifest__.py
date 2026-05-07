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
        "tz_realestate_leads",
        'sales_team'
    ],
    "data": [
        "security/ir.model.access.csv",
        # "views/menu.xml",
        "views/lead_source_config_views.xml",
	    "views/api_log_views.xml",
        "data/master_data.xml",
        "views/lead_routing_rule_views.xml",
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}