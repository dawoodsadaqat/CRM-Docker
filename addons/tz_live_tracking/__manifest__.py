{
    "name": "TZ Live Tracking",
    "version": "17.0.1.0.0",
    "depends": ["base", "crm", "sales_team", "tz_crm_base"],
    "data": [
        "security/ir.model.access.csv",
        "security/user_location_rules.xml",
        "views/user_location_views.xml",
        "views/res_users_views.xml",
        "views/live_tracking_config_views.xml",
    ],
    "installable": True,
}