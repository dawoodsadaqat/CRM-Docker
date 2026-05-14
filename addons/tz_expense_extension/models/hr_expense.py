from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrExpense(models.Model):
    _inherit = "hr.expense"

    lead_id = fields.Many2one(
        "crm.lead",
        string="CRM Lead",
        tracking=True,
    )

    site_visit_id = fields.Many2one(
        "tz.site.visit",
        string="Site Visit",
        tracking=True,
    )

    property_unit_id = fields.Many2one(
        "tz.property.unit",
        string="Property Unit",
        tracking=True,
    )

    customer_id = fields.Many2one(
        "res.partner",
        string="Customer",
        tracking=True,
    )

    approved_by_supervisor_id = fields.Many2one(
        "res.users",
        string="Approved By Supervisor",
        readonly=True,
        tracking=True,
    )

    supervisor_approval_state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted to Supervisor"),
            ("approved", "Supervisor Approved"),
            ("rejected", "Supervisor Rejected"),
        ],
        string="Supervisor Approval",
        default="draft",
        tracking=True,
    )

    supervisor_rejection_reason = fields.Text(
        string="Supervisor Rejection Reason",
        tracking=True,
    )

    is_crm_expense = fields.Boolean(
        string="CRM Related Expense",
        compute="_compute_is_crm_expense",
        store=True,
    )

    @api.depends("lead_id", "site_visit_id", "property_unit_id", "customer_id")
    def _compute_is_crm_expense(self):
        for expense in self:
            expense.is_crm_expense = bool(
                expense.lead_id
                or expense.site_visit_id
                or expense.property_unit_id
                or expense.customer_id
            )

    @api.onchange("lead_id")
    def _onchange_lead_id(self):
        for expense in self:
            if expense.lead_id:
                expense.customer_id = expense.lead_id.partner_id

    @api.onchange("site_visit_id")
    def _onchange_site_visit_id(self):
        for expense in self:
            if expense.site_visit_id:
                expense.lead_id = expense.site_visit_id.lead_id
                expense.customer_id = expense.site_visit_id.customer_id
                expense.property_unit_id = expense.site_visit_id.property_unit_id

    def action_submit_to_supervisor(self):
        for expense in self:
            if not expense.employee_id:
                raise UserError(_("Employee is required."))

            if not expense.employee_id.user_id:
                raise UserError(_("Employee must be linked with an Odoo user."))

            expense.supervisor_approval_state = "submitted"

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Submitted",
                "message": "Expense submitted to supervisor.",
                "type": "success",
                "sticky": False,
            },
        }

    def action_supervisor_approve(self):
        for expense in self:
            expense.supervisor_approval_state = "approved"
            expense.approved_by_supervisor_id = self.env.user

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Approved",
                "message": "Expense approved by supervisor. Accounting can now reimburse.",
                "type": "success",
                "sticky": False,
            },
        }

    def action_supervisor_reject(self):
        for expense in self:
            expense.supervisor_approval_state = "rejected"

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Rejected",
                "message": "Expense rejected by supervisor.",
                "type": "warning",
                "sticky": False,
            },
        }

    def action_view_linked_lead(self):
        self.ensure_one()

        if not self.lead_id:
            raise UserError(_("No linked CRM Lead."))

        return {
            "type": "ir.actions.act_window",
            "name": "CRM Lead",
            "res_model": "crm.lead",
            "view_mode": "form",
            "res_id": self.lead_id.id,
            "target": "current",
        }

    def action_view_site_visit(self):
        self.ensure_one()

        if not self.site_visit_id:
            raise UserError(_("No linked Site Visit."))

        return {
            "type": "ir.actions.act_window",
            "name": "Site Visit",
            "res_model": "tz.site.visit",
            "view_mode": "form",
            "res_id": self.site_visit_id.id,
            "target": "current",
        }

    def action_view_property_unit(self):
        self.ensure_one()

        if not self.property_unit_id:
            raise UserError(_("No linked Property Unit."))

        return {
            "type": "ir.actions.act_window",
            "name": "Property Unit",
            "res_model": "tz.property.unit",
            "view_mode": "form",
            "res_id": self.property_unit_id.id,
            "target": "current",
        }