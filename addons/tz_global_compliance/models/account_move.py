from odoo import _, models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    def _tz_validate_uae_invoice(self):
        for move in self:
            if move.move_type not in ("out_invoice", "out_refund", "in_invoice", "in_refund"):
                continue
            company = move.company_id
            if not company.tz_enable_uae_compliance or company.tz_compliance_country_mode != "uae":
                continue

            if company.country_id.code != "AE":
                raise ValidationError(_("Company country must be UAE when UAE compliance mode is enabled."))
            if not company.vat:
                raise ValidationError(_("Company TRN (VAT field) is required for UAE invoice posting."))
            if not move.currency_id or not company.currency_id:
                raise ValidationError(_("Invoice and company currencies must be configured."))
            if not move.partner_id:
                raise ValidationError(_("Customer/Vendor is required before posting."))

            partner = move.partner_id.commercial_partner_id
            if partner.country_id.code == "AE" and not partner.vat:
                raise ValidationError(_("UAE customer/vendor must have TRN in VAT field before posting."))

            taxable_lines = move.invoice_line_ids.filtered(lambda l: not l.display_type and l.price_subtotal)
            if taxable_lines and not any(line.tax_ids for line in taxable_lines):
                raise ValidationError(_("Tax is required on taxable invoice lines under UAE compliance."))

    def action_post(self):
        self._tz_validate_uae_invoice()
        return super().action_post()
