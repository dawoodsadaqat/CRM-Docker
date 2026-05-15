from odoo import api, models
from odoo.exceptions import ValidationError


class CrmLead(models.Model):
    _inherit = "crm.lead"

    @api.constrains("company_id", "partner_id")
    def _check_tz_compliance_context(self):
        for lead in self:
            if not lead.company_id:
                raise ValidationError("Lead must have a company.")
            if lead.partner_id and lead.partner_id.company_id and lead.partner_id.company_id != lead.company_id:
                raise ValidationError("Lead customer company must match lead company.")
