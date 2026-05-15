from odoo import api, models
from odoo.exceptions import ValidationError


class TzPayroll(models.Model):
    _inherit = "tz.payroll"

    @api.constrains("company_id", "line_ids")
    def _check_tz_payroll_company_scope(self):
        for payroll in self:
            for line in payroll.line_ids:
                if line.employee_id.company_id and line.employee_id.company_id != payroll.company_id:
                    raise ValidationError("Payroll line employee company must match payroll company.")
