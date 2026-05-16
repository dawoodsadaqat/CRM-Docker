from odoo import api, fields, models, _
from odoo.exceptions import UserError


class TzPayroll(models.Model):
    _name = "tz.payroll"
    _description = "Monthly Payroll"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_from desc"

    name = fields.Char(
        string="Reference",
        required=True,
        copy=False,
        readonly=True,
        default="New",
    )

    date_from = fields.Date(
        string="Date From",
        required=True,
    )

    date_to = fields.Date(
        string="Date To",
        required=True,
    )

    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company,
        required=True,
    )

    state = fields.Selection([
        ("draft", "Draft"),
        ("generated", "Generated"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
    ], default="draft", tracking=True)

    line_ids = fields.One2many(
        "tz.payroll.line",
        "payroll_id",
        string="Payroll Lines",
    )

    total_basic_salary = fields.Float(
        compute="_compute_totals",
        store=True,
    )

    total_commission = fields.Float(
        compute="_compute_totals",
        store=True,
    )

    total_expenses = fields.Float(
        compute="_compute_totals",
        store=True,
    )

    total_deductions = fields.Float(
        compute="_compute_totals",
        store=True,
    )

    total_clawbacks = fields.Float(
        compute="_compute_totals",
        store=True,
    )

    total_net_payable = fields.Float(
        compute="_compute_totals",
        store=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "tz.payroll"
                ) or "New"

        return super().create(vals_list)

    @api.depends(
        "line_ids.basic_salary",
        "line_ids.commission_amount",
        "line_ids.expense_amount",
        "line_ids.deduction_amount",
        "line_ids.clawback_amount",
        "line_ids.net_payable",
    )
    def _compute_totals(self):
        for rec in self:
            rec.total_basic_salary = sum(rec.line_ids.mapped("basic_salary"))
            rec.total_commission = sum(rec.line_ids.mapped("commission_amount"))
            rec.total_expenses = sum(rec.line_ids.mapped("expense_amount"))
            rec.total_deductions = sum(rec.line_ids.mapped("deduction_amount"))
            rec.total_clawbacks = sum(rec.line_ids.mapped("clawback_amount"))
            rec.total_net_payable = sum(rec.line_ids.mapped("net_payable"))

    def action_generate_lines(self):

        for payroll in self:

            payroll.line_ids.unlink()

            employees = self.env["hr.employee"].search([
                ("active", "=", True)
            ])

            for employee in employees:

                user = employee.user_id

                commission_amount = 0.0
                clawback_amount = 0.0

                if user:

                    commissions = self.env["tz.commission"].search([
                        ("agent_id", "=", user.id),
                        ("create_date", ">=", payroll.date_from),
                        ("create_date", "<=", payroll.date_to),
                    ])

                    for commission in commissions:
                        commission_amount += (
                            commission.final_payable_amount
                            or 0.0
                        )

                        clawback_amount += (
                            commission.clawback_total
                            or 0.0
                        )

                expenses = self.env["hr.expense"].search([
                    ("employee_id", "=", employee.id),
                    ("date", ">=", payroll.date_from),
                    ("date", "<=", payroll.date_to),
                    ("state", "in", ["approved", "done"]),
                ])

                expense_amount = sum(
                    expenses.mapped("total_amount")
                )

                basic_salary = (
                    employee.tz_basic_salary
                    or 0.0
                )

                self.env["tz.payroll.line"].create({
                    "payroll_id": payroll.id,
                    "employee_id": employee.id,
                    "user_id": user.id if user else False,
                    "basic_salary": basic_salary,
                    "commission_amount": commission_amount,
                    "expense_amount": expense_amount,
                    "deduction_amount": 0.0,
                    "clawback_amount": clawback_amount,
                })

            payroll.state = "generated"

    def action_confirm(self):

        for payroll in self:

            if not payroll.line_ids:
                raise UserError(_("Generate payroll lines first."))

            payroll.state = "confirmed"

    def action_cancel(self):

        for payroll in self:
            payroll.state = "cancelled"

    def action_reset_to_draft(self):

        for payroll in self:
            payroll.state = "draft"


class TzPayrollLine(models.Model):
    _name = "tz.payroll.line"
    _description = "Payroll Line"

    payroll_id = fields.Many2one(
        "tz.payroll",
        required=True,
        ondelete="cascade",
    )

    employee_id = fields.Many2one(
        "hr.employee",
        required=True,
    )

    user_id = fields.Many2one(
        "res.users",
        string="CRM User",
    )

    basic_salary = fields.Float()

    commission_amount = fields.Float()

    expense_amount = fields.Float()

    deduction_amount = fields.Float()

    clawback_amount = fields.Float()

    net_payable = fields.Float(
        compute="_compute_net_payable",
        store=True,
    )

    payable_bill_id = fields.Many2one(
        "account.move",
        string="Payable Bill",
        readonly=True,
        copy=False,
    )

    payment_state = fields.Selection(
        related="payable_bill_id.payment_state",
        readonly=True,
    )

    note = fields.Text()

    @api.depends(
        "basic_salary",
        "commission_amount",
        "expense_amount",
        "deduction_amount",
        "clawback_amount",
    )
    def _compute_net_payable(self):

        for rec in self:

            rec.net_payable = (
                rec.basic_salary
                + rec.commission_amount
                + rec.expense_amount
                - rec.deduction_amount
                - rec.clawback_amount
            )

    def action_create_payable_bill(self):

        expense_account = self.env["account.account"].search([
            ("account_type", "=", "expense"),
            ("deprecated", "=", False),
        ], limit=1)

        if not expense_account:
            raise UserError(_("No expense account found."))

        for rec in self:

            if rec.payable_bill_id:
                continue

            partner = (
                rec.employee_id.work_contact_id
                or rec.employee_id.user_id.partner_id
            )

            if not partner:
                raise UserError(
                    _("Employee has no partner configured.")
                )

            bill = self.env["account.move"].create({
                "move_type": "in_invoice",
                "partner_id": partner.id,
                "invoice_date": fields.Date.today(),
                "ref": rec.payroll_id.name,
                "invoice_line_ids": [(0, 0, {
                    "name": f"Payroll - {rec.employee_id.name}",
                    "quantity": 1,
                    "price_unit": rec.net_payable,
                    "account_id": expense_account.id,
                })],
            })

            rec.payable_bill_id = bill.id

    def action_open_payable_bill(self):

        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": "Payable Bill",
            "res_model": "account.move",
            "view_mode": "form",
            "res_id": self.payable_bill_id.id,
            "target": "current",
        }