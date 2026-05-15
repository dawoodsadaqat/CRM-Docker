from odoo import api, models
from odoo.exceptions import ValidationError


class CrmLead(models.Model):
    _inherit = "crm.lead"

    @api.constrains("company_id", "partner_id")
    def _check_tz_compliance_context(self):
        for lead in self:
            company = lead.company_id
            if not company or not company.tz_enable_uae_compliance:
                continue
            if lead.partner_id and lead.partner_id.company_id and lead.partner_id.company_id != company:
                raise ValidationError("Lead customer company must match lead company under compliance mode.")
