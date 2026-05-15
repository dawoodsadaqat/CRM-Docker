from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    tz_enable_uae_compliance = fields.Boolean(
        related="company_id.tz_enable_uae_compliance",
        readonly=False,
    )
    tz_compliance_country_mode = fields.Selection(
        related="company_id.tz_compliance_country_mode",
        readonly=False,
    )
    tz_zatca_readiness_note = fields.Text(
        related="company_id.tz_zatca_readiness_note",
        readonly=False,
    )
