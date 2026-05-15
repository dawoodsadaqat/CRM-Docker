from odoo import api, models
from odoo.exceptions import ValidationError


class TzPayroll(models.Model):
    _inherit = "tz.payroll"

    @api.constrains("company_id", "line_ids")
    def _check_tz_payroll_company_scope(self):
        for payroll in self:
            company = payroll.company_id
            if not company or not company.tz_enable_uae_compliance:
                continue
            for line in payroll.line_ids:
                if line.employee_id.company_id and line.employee_id.company_id != company:
                    raise ValidationError("Payroll line employee company must match payroll company under compliance mode.")
