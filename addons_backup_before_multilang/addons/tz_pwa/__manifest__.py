{
    "name": "TZ PWA",
    "version": "17.0.1.0.0",
    "summary": "PWA support for Techzilla CRM",
    "category": "Tools",
    "author": "Techzilla",
    "license": "LGPL-3",
    "depends": ["web","crm"],
    "data": [
        "views/pwa_templates.xml",
	"views/mobile_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "tz_pwa/static/src/js/pwa_register.js",
	    "tz_pwa/static/src/css/mobile.css",
        ],
        "web.assets_frontend": [
            "tz_pwa/static/src/js/pwa_register.js",
        ],
    },
    "installable": True,
    "application": False,
}
