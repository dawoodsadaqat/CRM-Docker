{
    "name": "Develvo Branding",
    "version": "17.0.1.0.0",
    "summary": "White-label Odoo branding as Develvo",
    "category": "Branding",
    "author": "Develvo",
    "depends": ["base", "web"],
    "data": [
        "views/web_branding_templates.xml",
        
    ],
    "assets": {
        "web.assets_backend": [
            "tz_branding/static/src/css/branding.css",
            "tz_branding/static/src/js/branding.js",
        ],
        "web.assets_frontend": [
            "tz_branding/static/src/css/branding.css",
        ],
    },
    "installable": True,
    "application": False,
}