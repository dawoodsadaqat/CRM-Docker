from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    tz_default_language_code = fields.Selection([
        ("en_US", "English"),
        ("ar_001", "Arabic"),
        ("ur_PK", "Urdu"),
        ("fr_FR", "French"),
        ("ru_RU", "Russian"),
        ("hi_IN", "Hindi"),
    ], string="Default CRM Language", config_parameter="tz_i18n_support.default_language_code", default="en_US")

    tz_enable_multilingual_crm = fields.Boolean(string="Enable Multilingual CRM", config_parameter="tz_i18n_support.enable_multilingual_crm", default=True)
