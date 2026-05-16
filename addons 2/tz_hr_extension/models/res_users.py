from odoo import api, models, _
from odoo.exceptions import UserError


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.context.get("from_employee_sync"):
            current_user = self.env.user

            if not current_user.has_group("base.group_system"):
                raise UserError(
                    _("Users can only be created from Employees using the Is CRM User checkbox.")
                )

        return super().create(vals_list)