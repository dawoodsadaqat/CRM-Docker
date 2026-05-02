from odoo import models, fields, api


class TzCommission(models.Model):
    _name = "tz.commission"
    _description = "Agent Commission"
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

    property_unit_id = fields.Many2one(
        "tz.property.unit",
        string="Property Unit",
        required=True
    )

    sale_value = fields.Float(
        string="Sale Value",
        required=True
    )

    commission_percent = fields.Float(
        string="Commission %",
        default=2.0,
        required=True
    )

    commission_amount = fields.Float(
        string="Commission Amount",
        compute="_compute_commission_amount",
        store=True
    )

    approval_status = fields.Selection([
        ("draft", "Draft"),
        ("submitted", "Submitted"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ], string="Approval Status", default="draft", required=True)

    payment_status = fields.Selection([
        ("unpaid", "Unpaid"),
        ("partially_paid", "Partially Paid"),
        ("paid", "Paid"),
    ], string="Payment Status", default="unpaid", required=True)

    paid_amount = fields.Float(string="Paid Amount")

    remaining_amount = fields.Float(
        string="Remaining Amount",
        compute="_compute_remaining_amount",
        store=True
    )

    approval_note = fields.Text(string="Approval Note")
    payment_note = fields.Text(string="Payment Note")

    @api.depends("sale_value", "commission_percent")
    def _compute_commission_amount(self):
        for rec in self:
            rec.commission_amount = (rec.sale_value * rec.commission_percent) / 100 if rec.sale_value else 0.0

    @api.depends("commission_amount", "paid_amount")
    def _compute_remaining_amount(self):
        for rec in self:
            rec.remaining_amount = rec.commission_amount - rec.paid_amount

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

        return super().create(vals_list)

    @api.onchange("property_unit_id")
    def _onchange_property_unit_id(self):
        for rec in self:
            if rec.property_unit_id:
                rec.sale_value = rec.property_unit_id.sale_price

    def action_submit(self):
        for rec in self:
            rec.approval_status = "submitted"

    def action_approve(self):
        for rec in self:
            rec.approval_status = "approved"

    def action_reject(self):
        for rec in self:
            rec.approval_status = "rejected"

    def action_reset_to_draft(self):
        for rec in self:
            rec.approval_status = "draft"