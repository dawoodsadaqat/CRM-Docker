{
    "name": "TZ Live Tracking",
    "version": "17.0.1.0.0",
    "summary": "Live GPS tracking for CRM users",
    "category": "CRM",
    "author": "Techzilla",
    "license": "LGPL-3",

    "depends": [
        "base",
        "crm",
        "sales_team",
        "web",
        "tz_crm_base",
    ],

    "data": [
        "security/ir.model.access.csv",
        "security/user_location_rules.xml",
        "views/res_users_views.xml",
        "views/user_location_views.xml",
        "views/live_tracking_client_action.xml",
    ],

    "assets": {
        "web.assets_backend": [
            "tz_live_tracking/static/src/js/live_tracking.js",
            "tz_live_tracking/static/src/xml/live_tracking.xml",
        ],
    },

    "installable": True,
    "application": False,
}