from odoo import api, fields, models
from odoo.exceptions import ValidationError


class TzPropertyProject(models.Model):
    _inherit = "tz.property.project"

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        required=True,
    )
    country_id = fields.Many2one("res.country", string="Country")

    @api.constrains("company_id", "developer_id")
    def _check_tz_project_company_context(self):
        for rec in self:
            if rec.developer_id.company_id and rec.developer_id.company_id != rec.company_id:
                raise ValidationError("Developer company must match property project company.")


class TzPropertyListing(models.Model):
    _inherit = "tz.property.listing"

    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        related="unit_id.project_id.company_id.currency_id",
        store=True,
        readonly=True,
    )

    @api.constrains("unit_id", "listing_price")
    def _check_tz_listing_basics(self):
        for rec in self:
            if rec.listing_price < 0:
                raise ValidationError("Listing price cannot be negative.")
            if not rec.unit_id:
                raise ValidationError("Listing must be linked to a property unit.")
