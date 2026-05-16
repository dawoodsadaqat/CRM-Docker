from odoo import models, fields, api
from odoo.exceptions import UserError


class TzCommission(models.Model):
    _name = "tz.commission"
    _description = "Real Estate Commission"
    _order = "create_date desc, id desc"

    name = fields.Char(
        string="Commission Reference",
        required=True,
        copy=False,
        default="New"
    )

    lead_id = fields.Many2one(
        "crm.lead",
        string="Lead / Deal",
        required=True,
        ondelete="cascade"
    )

    customer_id = fields.Many2one(
        "res.partner",
        string="Customer"
    )

    agent_id = fields.Many2one(
        "res.users",
        string="Agent",
        required=True
    )

    manager_id = fields.Many2one(
        "res.users",
        string="Manager / Supervisor"
    )

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        required=True
    )

    property_unit_id = fields.Many2one(
        "tz.property.unit",
        string="Property Unit",
        required=True
    )

    sale_value = fields.Float(
        string="Sale / Deal Value",
        required=True
    )

    currency_id = fields.Many2one(
        "res.currency",
        related="company_id.currency_id",
        store=True,
        readonly=True
    )

    # =====================================================
    # AGENCY COMMISSION
    # =====================================================

    agency_commission_percent = fields.Float(
        string="Agency Commission %",
        default=2.0
    )

    agency_commission_amount = fields.Monetary(
        string="Agency Commission Amount",
        compute="_compute_commission_amounts",
        store=True,
        currency_field="currency_id"
    )

    vat_applicable = fields.Boolean(
        string="VAT Applicable",
        default=True
    )

    vat_percent = fields.Float(
        string="VAT %",
        default=5.0
    )

    vat_amount = fields.Monetary(
        string="VAT Amount",
        compute="_compute_commission_amounts",
        store=True,
        currency_field="currency_id"
    )

    total_receivable_amount = fields.Monetary(
        string="Total Receivable from Customer",
        compute="_compute_commission_amounts",
        store=True,
        currency_field="currency_id"
    )

    # =====================================================
    # BROKERAGE SPLITS / PAYOUTS
    # =====================================================

    agency_share_percent = fields.Float(
        string="Agency Share %",
        default=100.0
    )

    agency_share_amount = fields.Monetary(
        string="Agency Share Amount",
        compute="_compute_commission_amounts",
        store=True,
        currency_field="currency_id"
    )

    external_broker_percent = fields.Float(
        string="External Broker %",
        default=0.0
    )

    external_broker_amount = fields.Monetary(
        string="External Broker Amount",
        compute="_compute_commission_amounts",
        store=True,
        currency_field="currency_id"
    )

    agent_commission_percent = fields.Float(
        string="Agent Commission %",
        default=30.0
    )

    agent_commission_amount = fields.Monetary(
        string="Agent Commission Amount",
        compute="_compute_commission_amounts",
        store=True,
        currency_field="currency_id"
    )

    manager_override_percent = fields.Float(
        string="Manager Override %",
        default=0.0
    )

    manager_override_amount = fields.Monetary(
        string="Manager Override Amount",
        compute="_compute_commission_amounts",
        store=True,
        currency_field="currency_id"
    )

    developer_payout_percent = fields.Float(
        string="Developer Payout %",
        default=0.0
    )

    developer_payout_amount = fields.Monetary(
        string="Developer Payout Amount",
        compute="_compute_commission_amounts",
        store=True,
        currency_field="currency_id"
    )

    total_payout_amount = fields.Monetary(
        string="Total Payout",
        compute="_compute_commission_amounts",
        store=True,
        currency_field="currency_id"
    )

    net_company_commission = fields.Monetary(
        string="Net Company Commission",
        compute="_compute_commission_amounts",
        store=True,
        currency_field="currency_id"
    )

    # =====================================================
    # PAYMENT / MILESTONES
    # =====================================================

    milestone_ids = fields.One2many(
        "tz.commission.milestone",
        "commission_id",
        string="Payment Milestones"
    )

    paid_amount = fields.Monetary(
        string="Paid Amount",
        compute="_compute_payment_status",
        store=True,
        currency_field="currency_id"
    )

    remaining_amount = fields.Monetary(
        string="Remaining Amount",
        compute="_compute_payment_status",
        store=True,
        currency_field="currency_id"
    )

    payment_status = fields.Selection([
        ("unpaid", "Unpaid"),
        ("partially_paid", "Partially Paid"),
        ("paid", "Paid"),
    ], string="Payment Status", compute="_compute_payment_status", store=True)

    # =====================================================
    # APPROVAL / ACCOUNTING
    # =====================================================

    approval_status = fields.Selection([
        ("draft", "Draft"),
        ("submitted", "Submitted"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("closed", "Closed"),
    ], string="Approval Status", default="draft", required=True)

    customer_invoice_ref = fields.Char(
        string="Customer Invoice Reference"
    )

    accounting_entry_ref = fields.Char(
        string="Accounting Entry Reference"
    )

    agency_payment_received = fields.Boolean(
        string="Agency Payment Received",
        default=False
    )

    approval_note = fields.Text(string="Approval Note")
    payment_note = fields.Text(string="Payment Note")
    accounting_note = fields.Text(string="Accounting Note")

    clawback_ids = fields.One2many(
        "tz.commission.clawback",
        "commission_id",
        string="Clawbacks"
    )

    clawback_total = fields.Monetary(
        string="Clawback Total",
        compute="_compute_clawback_total",
        store=True,
        currency_field="currency_id"
    )

    final_payable_amount = fields.Monetary(
        string="Final Payable After Clawback",
        compute="_compute_final_payable_amount",
        store=True,
        currency_field="currency_id"
    )

    # =====================================================
    # COMPUTES
    # =====================================================

    @api.depends(
        "sale_value",
        "agency_commission_percent",
        "vat_applicable",
        "vat_percent",
        "agency_share_percent",
        "external_broker_percent",
        "agent_commission_percent",
        "manager_override_percent",
        "developer_payout_percent",
    )
    def _compute_commission_amounts(self):
        for rec in self:
            base = (rec.sale_value * rec.agency_commission_percent) / 100 if rec.sale_value else 0.0

            rec.agency_commission_amount = base
            rec.vat_amount = (base * rec.vat_percent) / 100 if rec.vat_applicable else 0.0
            rec.total_receivable_amount = base + rec.vat_amount

            rec.agency_share_amount = (base * rec.agency_share_percent) / 100
            rec.external_broker_amount = (base * rec.external_broker_percent) / 100
            rec.agent_commission_amount = (base * rec.agent_commission_percent) / 100
            rec.manager_override_amount = (base * rec.manager_override_percent) / 100
            rec.developer_payout_amount = (base * rec.developer_payout_percent) / 100

            rec.total_payout_amount = (
                rec.external_broker_amount
                + rec.agent_commission_amount
                + rec.manager_override_amount
                + rec.developer_payout_amount
            )

            rec.net_company_commission = base - rec.total_payout_amount

    @api.depends("milestone_ids.amount", "milestone_ids.status", "total_receivable_amount")
    def _compute_payment_status(self):
        for rec in self:
            paid = sum(
                rec.milestone_ids.filtered(lambda m: m.status == "paid").mapped("amount")
            )

            rec.paid_amount = paid
            rec.remaining_amount = rec.total_receivable_amount - paid

            if paid <= 0:
                rec.payment_status = "unpaid"
            elif paid < rec.total_receivable_amount:
                rec.payment_status = "partially_paid"
            else:
                rec.payment_status = "paid"

    @api.depends("clawback_ids.amount", "clawback_ids.status")
    def _compute_clawback_total(self):
        for rec in self:
            rec.clawback_total = sum(
                rec.clawback_ids.filtered(lambda c: c.status == "approved").mapped("amount")
            )

    @api.depends("agent_commission_amount", "clawback_total")
    def _compute_final_payable_amount(self):
        for rec in self:
            rec.final_payable_amount = rec.agent_commission_amount - rec.clawback_total

    # =====================================================
    # CREATE / ONCHANGE
    # =====================================================

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("tz.commission") or "New"

            if vals.get("lead_id"):
                lead = self.env["crm.lead"].browse(vals["lead_id"])

                if not vals.get("customer_id") and lead.partner_id:
                    vals["customer_id"] = lead.partner_id.id

                if not vals.get("agent_id") and lead.user_id:
                    vals["agent_id"] = lead.user_id.id

                if not vals.get("manager_id") and lead.team_id and lead.team_id.user_id:
                    vals["manager_id"] = lead.team_id.user_id.id

        return super().create(vals_list)

    @api.onchange("property_unit_id")
    def _onchange_property_unit_id(self):
        for rec in self:
            if rec.property_unit_id and hasattr(rec.property_unit_id, "sale_price"):
                rec.sale_value = rec.property_unit_id.sale_price

    # =====================================================
    # SECURITY HELPERS
    # =====================================================

    def _check_manager_or_admin(self):
        if not (
            self.env.user.has_group("tz_crm_base.group_tz_crm_manager")
            or self.env.user.has_group("tz_crm_base.group_tz_crm_admin")
            or self.env.user.has_group("base.group_system")
        ):
            raise UserError("Only Manager/Admin can perform this action.")

    # =====================================================
    # ACTIONS
    # =====================================================

    def action_submit(self):
        for rec in self:
            if rec.approval_status != "draft":
                continue
            rec.approval_status = "submitted"

    def action_approve(self):
        self._check_manager_or_admin()
        for rec in self:
            if rec.approval_status != "submitted":
                raise UserError("Only submitted commissions can be approved.")
            rec.approval_status = "approved"

    def action_reject(self):
        self._check_manager_or_admin()
        for rec in self:
            if rec.approval_status != "submitted":
                raise UserError("Only submitted commissions can be rejected.")
            rec.approval_status = "rejected"

    def action_reset_to_draft(self):
        self._check_manager_or_admin()
        for rec in self:
            rec.approval_status = "draft"

    def action_mark_agency_payment_received(self):
        self._check_manager_or_admin()
        for rec in self:
            rec.agency_payment_received = True

    def action_close_commission(self):
        self._check_manager_or_admin()
        for rec in self:
            if rec.approval_status != "approved":
                raise UserError("Only approved commissions can be closed.")
            rec.approval_status = "closed"


class TzCommissionMilestone(models.Model):
    _name = "tz.commission.milestone"
    _description = "Commission Payment Milestone"
    _order = "due_date asc, id asc"

    commission_id = fields.Many2one(
        "tz.commission",
        string="Commission",
        required=True,
        ondelete="cascade"
    )

    name = fields.Char(
        string="Milestone",
        required=True,
        default="Payment Milestone"
    )

    due_date = fields.Date(
        string="Due Date",
        default=fields.Date.today
    )

    amount = fields.Monetary(
        string="Amount",
        required=True,
        currency_field="currency_id"
    )

    currency_id = fields.Many2one(
        "res.currency",
        related="commission_id.currency_id",
        store=True,
        readonly=True
    )

    status = fields.Selection([
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("cancelled", "Cancelled"),
    ], string="Status", default="pending", required=True)

    paid_date = fields.Date(string="Paid Date")
    note = fields.Text(string="Note")

    def action_mark_paid(self):
        for rec in self:
            rec.status = "paid"
            rec.paid_date = fields.Date.today()

    def action_reset_pending(self):
        for rec in self:
            rec.status = "pending"
            rec.paid_date = False


class TzCommissionClawback(models.Model):
    _name = "tz.commission.clawback"
    _description = "Commission Clawback"
    _order = "date desc, id desc"

    commission_id = fields.Many2one(
        "tz.commission",
        string="Commission",
        required=True,
        ondelete="cascade"
    )

    date = fields.Date(
        string="Date",
        default=fields.Date.today
    )

    reason = fields.Char(
        string="Reason",
        required=True
    )

    amount = fields.Monetary(
        string="Amount",
        required=True,
        currency_field="currency_id"
    )

    currency_id = fields.Many2one(
        "res.currency",
        related="commission_id.currency_id",
        store=True,
        readonly=True
    )

    status = fields.Selection([
        ("draft", "Draft"),
        ("approved", "Approved"),
        ("cancelled", "Cancelled"),
    ], string="Status", default="draft", required=True)

    note = fields.Text(string="Note")

    def action_approve(self):
        for rec in self:
            rec.status = "approved"

    def action_cancel(self):
        for rec in self:
            rec.status = "cancelled"