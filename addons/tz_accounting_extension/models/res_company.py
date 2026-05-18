from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    tz_uae_vat_standard_tax_id = fields.Many2one(
        "account.tax",
        string="UAE VAT Standard Tax",
        domain="[('type_tax_use', '=', 'sale'), ('company_id', '=', id)]",
    )
    tz_uae_vat_zero_tax_id = fields.Many2one(
        "account.tax",
        string="UAE VAT Zero-Rated Tax",
        domain="[('type_tax_use', '=', 'sale'), ('company_id', '=', id)]",
    )
    tz_uae_vat_exempt_tax_id = fields.Many2one(
        "account.tax",
        string="UAE VAT Exempt Tax",
        domain="[('type_tax_use', '=', 'sale'), ('company_id', '=', id)]",
    )
    tz_uae_vat_out_scope_tax_id = fields.Many2one(
        "account.tax",
        string="UAE VAT Out-of-Scope Tax",
        domain="[('type_tax_use', '=', 'sale'), ('company_id', '=', id)]",
    )
