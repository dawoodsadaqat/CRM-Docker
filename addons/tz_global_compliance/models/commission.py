from odoo import api, models
from odoo.exceptions import ValidationError


class TzCommission(models.Model):
    _inherit = "tz.commission"

    @api.constrains("company_id", "lead_id", "customer_id", "vat_applicable", "vat_percent")
    def _check_tz_commission_compliance(self):
        for rec in self:
            if rec.lead_id.company_id and rec.company_id != rec.lead_id.company_id:
                raise ValidationError("Commission company must match lead company.")
            if rec.vat_applicable and rec.vat_percent < 0:
                raise ValidationError("Commission VAT percent cannot be negative.")
