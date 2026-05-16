{
    "name": "TZ Multilingual Support",
    "version": "17.0.1.0.0",
    "summary": "Multilingual support and translation readiness for Techzilla custom modules",
    "category": "Tools",
    "author": "Techzilla",
    "license": "LGPL-3",
    "depends": [
        "base", "web", "crm", "contacts", "account", "hr", "hr_attendance", "hr_expense",
        "tz_crm_base", "tz_realestate_leads", "tz_property_inventory", "tz_site_visit",
        "tz_call_center", "tz_whatsapp", "tz_api_gateway", "tz_lead_assignment",
        "tz_commission", "tz_accounting_extension", "tz_dashboard", "tz_hr_extension",
        "tz_live_tracking", "tz_attendance_geo", "tz_expense_extension", "tz_payroll",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/res_config_settings_views.xml",
        "views/i18n_tools_views.xml",
    ],
    "installable": True,
    "application": False,
}
