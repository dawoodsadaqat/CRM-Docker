from odoo import _, api, fields, models


class TzI18nTools(models.TransientModel):
    _name = "tz.i18n.tools"
    _description = "TZ Translation Tools"

    name = fields.Char(string="Name", default="Translation Tools", translate=True)
    language_code = fields.Selection([
        ("ar_001", "Arabic"),
        ("ur_PK", "Urdu"),
        ("fr_FR", "French"),
        ("ru_RU", "Russian"),
        ("hi_IN", "Hindi"),
    ], string="Language", default="ar_001", required=True)
    module_scope = fields.Selection([
        ("all", "All Custom Modules"),
        ("crm", "CRM Modules"),
        ("property", "Property Modules"),
        ("finance", "Finance Modules"),
        ("hr", "HR / Payroll Modules"),
        ("communication", "Communication Modules"),
    ], string="Module Scope", default="all", required=True)
    note = fields.Text(string="Notes", translate=True, default="Use Odoo translation export/import for all custom modules.")
    custom_module_list = fields.Text(string="Custom Modules", compute="_compute_custom_module_list", readonly=True)

    def _get_custom_modules(self):
        mapping = {
            "all": ["tz_crm_base", "tz_realestate_leads", "tz_property_inventory", "tz_site_visit", "tz_call_center", "tz_whatsapp", "tz_api_gateway", "tz_lead_assignment", "tz_commission", "tz_accounting_extension", "tz_dashboard", "tz_hr_extension", "tz_live_tracking", "tz_attendance_geo", "tz_expense_extension", "tz_payroll"],
            "crm": ["tz_crm_base", "tz_realestate_leads", "tz_dashboard", "tz_lead_assignment", "tz_api_gateway"],
            "property": ["tz_property_inventory", "tz_site_visit"],
            "finance": ["tz_commission", "tz_accounting_extension"],
            "hr": ["tz_hr_extension", "tz_live_tracking", "tz_attendance_geo", "tz_expense_extension", "tz_payroll"],
            "communication": ["tz_call_center", "tz_whatsapp"],
        }
        return mapping.get(self.module_scope, mapping["all"])

    @api.depends("module_scope")
    def _compute_custom_module_list(self):
        for record in self:
            record.custom_module_list = "\n".join(record._get_custom_modules())

    def action_open_languages(self):
        return {"type": "ir.actions.act_window", "name": _("Languages"), "res_model": "res.lang", "view_mode": "tree,form", "target": "current"}

    def action_open_translations(self):
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Not Available"),
                "message": _("Direct translated terms view is not available in Odoo 17. Use Settings > Translations > Export/Import instead."),
                "type": "warning",
                "sticky": False,
            },
        }

    def action_show_export_instructions(self):
        modules = ",".join(self._get_custom_modules())
        message = _("Run this command inside Docker to export translations:\n\ndocker exec -it odoo-app odoo -d techzilla_crm_clean --i18n-export=/tmp/tz_custom_modules.pot --modules=%s --stop-after-init") % modules
        return {"type": "ir.actions.client", "tag": "display_notification", "params": {"title": _("Translation Export Command"), "message": message, "type": "info", "sticky": True}}
