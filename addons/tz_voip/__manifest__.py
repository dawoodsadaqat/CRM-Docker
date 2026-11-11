{
    "name": "TZ VOIP Integration",
    "version": "17.0.1.0.0",
    "summary": "Configurable VOIP integration for CRM calls",
    "category": "CRM",
    "author": "Techzilla",
    "license": "LGPL-3",
    "depends": [
        "base",
        "crm",
        "contacts",
        "mail",
        "tz_call_center",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/tz_voip_provider_views.xml",
        "views/tz_call_log_views.xml",
        "views/crm_lead_views.xml",
        "views/res_users_views.xml",
    ],
    "installable": True,
    "application": False,
}