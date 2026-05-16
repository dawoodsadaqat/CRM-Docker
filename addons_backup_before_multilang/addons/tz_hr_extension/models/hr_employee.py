from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    tz_is_crm_user = fields.Boolean(
        string="Is CRM User?",
        default=False,
        help="If enabled, an Odoo user will be created/linked for this employee."
    )

    tz_linked_user_id = fields.Many2one(
        "res.users",
        string="Linked CRM User",
        related="user_id",
        readonly=True,
        store=False,
    )

    tz_user_login = fields.Char(
        string="User Login",
        related="user_id.login",
        readonly=True,
        store=False,
    )

    tz_basic_salary = fields.Float(
        string="Basic Salary"
    )

    def _prepare_crm_user_vals(self):
        self.ensure_one()

        if not self.name:
            raise UserError(_("Employee name is required."))

        if not self.work_email:
            raise UserError(_("Work Email is required to create a CRM user."))

        return {
            "name": self.name,
            "login": self.work_email,
            "email": self.work_email,
            "groups_id": [(6, 0, [self.env.ref("base.group_user").id])],
        }

    def action_create_or_sync_crm_user(self):
        Users = self.env["res.users"].sudo()

        for employee in self:
            if not employee.tz_is_crm_user:
                raise UserError(_("Please enable 'Is CRM User?' first."))

            vals = employee._prepare_crm_user_vals()

            user = employee.user_id

            if not user:
                user = Users.search([
                    ("login", "=", employee.work_email)
                ], limit=1)

            if not user:
                user = Users.with_context(
                    from_employee_sync=True,
                    skip_employee_crm_sync=True,
                    no_reset_password=True,
                    mail_create_nosubscribe=True,
                    tracking_disable=True,
                ).create(vals)
            else:
                user.with_context(
                    from_employee_sync=True,
                    skip_employee_crm_sync=True,
                    tracking_disable=True,
                ).write({
                    "name": employee.name,
                    "login": employee.work_email,
                    "email": employee.work_email,
                })

            if employee.user_id != user:
                employee.with_context(
                    skip_employee_crm_sync=True,
                    tracking_disable=True,
                ).write({
                    "user_id": user.id
                })

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "CRM User Synced",
                "message": "CRM user has been created/linked. Use Open User Settings to configure access rights.",
                "type": "success",
                "sticky": False,
            },
        }

    def action_open_user_settings(self):
        self.ensure_one()

        if not self.user_id:
            raise UserError(_("No linked user found. Create/sync CRM user first."))

        form_view = self.env.ref("base.view_users_form", raise_if_not_found=False)

        return {
            "type": "ir.actions.act_window",
            "name": "User Settings",
            "res_model": "res.users",
            "view_mode": "form",
            "views": [(form_view.id, "form")] if form_view else [(False, "form")],
            "res_id": self.user_id.id,
            "target": "current",
            "context": {
                "create": False,
                "delete": False,
            },
        }

    @api.model_create_multi
    def create(self, vals_list):
        employees = super().create(vals_list)

        if self.env.context.get("skip_employee_crm_sync"):
            return employees

        for employee in employees:
            if employee.tz_is_crm_user:
                employee.with_context(skip_employee_crm_sync=True).action_create_or_sync_crm_user()

        return employees

    def write(self, vals):
        result = super().write(vals)

        if self.env.context.get("skip_employee_crm_sync"):
            return result

        sync_fields = {
            "name",
            "work_email",
            "tz_is_crm_user",
        }

        if sync_fields.intersection(vals.keys()):
            for employee in self:
                if employee.tz_is_crm_user:
                    employee.with_context(skip_employee_crm_sync=True).action_create_or_sync_crm_user()

        return result