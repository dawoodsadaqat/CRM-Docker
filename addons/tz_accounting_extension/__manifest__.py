{
    "name": "TZ Accounting Extension",
    "version": "17.0.1.0.0",
    "summary": "Accounting integration for CRM commissions",
    "category": "Accounting",
    "author": "Techzilla",
    "license": "LGPL-3",
    "depends": [
        "account",
        "crm",
        "tz_crm_base",
        "tz_realestate_leads",
        "tz_property_inventory",
        "tz_commission",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/account_move_views.xml",
        "views/tz_commission_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "installable": True,
    "application": False,
}