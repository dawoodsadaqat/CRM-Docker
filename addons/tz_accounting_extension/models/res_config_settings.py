from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    tz_uae_vat_standard_tax_id = fields.Many2one(
        related="company_id.tz_uae_vat_standard_tax_id",
        readonly=False,
    )
    tz_uae_vat_zero_tax_id = fields.Many2one(
        related="company_id.tz_uae_vat_zero_tax_id",
        readonly=False,
    )
    tz_uae_vat_exempt_tax_id = fields.Many2one(
        related="company_id.tz_uae_vat_exempt_tax_id",
        readonly=False,
    )
    tz_uae_vat_out_scope_tax_id = fields.Many2one(
        related="company_id.tz_uae_vat_out_scope_tax_id",
        readonly=False,
    )
