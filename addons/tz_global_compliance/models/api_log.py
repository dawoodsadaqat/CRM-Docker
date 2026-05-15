from odoo import fields, models


class TzApiLog(models.Model):
    _inherit = "tz.api.log"

    tz_compliance_failed = fields.Boolean(string="Compliance Failed", default=False)
