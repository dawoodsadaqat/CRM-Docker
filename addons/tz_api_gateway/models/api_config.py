from odoo import models, fields


class TzApiConfig(models.Model):
    _name = "tz.api.config"
    _description = "TZ API Configuration"

    name = fields.Char(string="Name", required=True)
    active = fields.Boolean(default=True)

    api_key = fields.Char(
        string="API Key",
        required=True,
        help="External systems must send this key in X-API-Key header."
    )

    source_name = fields.Char(
        string="Default Source Name",
        default="External API"
    )