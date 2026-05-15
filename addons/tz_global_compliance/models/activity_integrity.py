from odoo import api, models
from odoo.exceptions import ValidationError


class TzSiteVisit(models.Model):
    _inherit = "tz.site.visit"

    @api.constrains("lead_id", "customer_id")
    def _check_tz_site_visit_integrity(self):
        for rec in self:
            if not rec.lead_id and not rec.customer_id:
                raise ValidationError("Site Visit requires lead or customer context.")


class TzCallLog(models.Model):
    _inherit = "tz.call.log"

    @api.constrains("lead_id", "customer_id")
    def _check_tz_call_integrity(self):
        for rec in self:
            if not rec.lead_id and not rec.customer_id:
                raise ValidationError("Call log requires lead or customer context.")


class TzWhatsappMessage(models.Model):
    _inherit = "tz.whatsapp.message"

    @api.constrains("lead_id", "customer_id")
    def _check_tz_whatsapp_integrity(self):
        for rec in self:
            if not rec.lead_id and not rec.customer_id:
                raise ValidationError("WhatsApp message requires lead or customer context.")
