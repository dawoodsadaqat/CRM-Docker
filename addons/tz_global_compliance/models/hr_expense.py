from odoo import api, models
from odoo.exceptions import ValidationError


class HrExpense(models.Model):
    _inherit = "hr.expense"

    @api.constrains("company_id", "lead_id")
    def _check_tz_expense_company(self):
        for rec in self:
            company = rec.company_id
            if not company or not company.tz_enable_uae_compliance:
                continue
            if rec.lead_id and rec.lead_id.company_id and company != rec.lead_id.company_id:
                raise ValidationError("Expense company must match linked lead company under compliance mode.")
