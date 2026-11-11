{
    "name": "TZ Site Visit",
    "version": "1.1.0",
    "summary": "Manage site visits and CRM lead meetings",
    "category": "Sales/CRM",
    "author": "Techzilla Global",
    "license": "LGPL-3",
    "depends": [
        "crm",
        "contacts",
        "calendar",
        "web",
        "tz_crm_base",
        "tz_realestate_leads",
        "tz_property_inventory",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/sequence.xml",
        "views/site_visit_views.xml",
        "views/crm_lead_views.xml",
        "views/calendar_event_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "tz_site_visit/static/src/js/meeting_location_capture.js",
        ],
    },
    "installable": True,
    "application": False,
}