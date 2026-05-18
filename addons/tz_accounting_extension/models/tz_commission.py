from odoo import fields, models, _
from odoo.exceptions import UserError


class TzCommission(models.Model):
    _inherit = "tz.commission"

    def _get_company_tax_mapping(self):
        self.ensure_one()
        company = self.company_id
        return {
            "standard_5": company.tz_uae_vat_standard_tax_id,
            "zero_rated": company.tz_uae_vat_zero_tax_id,
            "exempt": company.tz_uae_vat_exempt_tax_id,
            "out_of_scope": company.tz_uae_vat_out_scope_tax_id,
        }

    def _resolve_vat_treatment(self):
        self.ensure_one()
        if self.property_unit_id and self.property_unit_id.vat_treatment:
            return self.property_unit_id.vat_treatment
        return "standard_5"

    def _get_tax_from_vat_treatment(self):
        self.ensure_one()
        treatment = self._resolve_vat_treatment()
        tax = self._get_company_tax_mapping().get(treatment)

        # standard rate preserves legacy behavior if mapping is absent
        if treatment == "standard_5" and not tax:
            return self._get_uae_output_vat_tax()

        # zero/exempt/out-of-scope should stay untaxed when no mapping is configured
        return tax

    customer_invoice_id = fields.Many2one(
        "account.move",
        string="Customer Invoice",
        readonly=True,
        copy=False,
    )

    agent_payable_bill_id = fields.Many2one(
        "account.move",
        string="Agent Payable",
        readonly=True,
        copy=False,
    )

    developer_payable_bill_id = fields.Many2one(
        "account.move",
        string="Developer Payable",
        readonly=True,
        copy=False,
    )

    customer_payment_status = fields.Selection(
        related="customer_invoice_id.payment_state",
        string="Customer Payment Status",
        readonly=True,
    )

    agent_bill_payment_status = fields.Selection(
        related="agent_payable_bill_id.payment_state",
        string="Agent Payout Status",
        readonly=True,
    )

    developer_bill_payment_status = fields.Selection(
        related="developer_payable_bill_id.payment_state",
        string="Developer Payout Status",
        readonly=True,
    )

    # ---------------------------------------------------------
    # ACCOUNT HELPERS
    # ---------------------------------------------------------

    def _get_income_account(self):
        account = self.env["account.account"].search([
            ("account_type", "=", "income"),
            ("deprecated", "=", False),
            ("company_id", "=", self.env.company.id),
        ], limit=1)

        if not account:
            raise UserError(_("No income account found."))

        return account

    def _get_expense_account(self):
        account = self.env["account.account"].search([
            ("account_type", "=", "expense"),
            ("deprecated", "=", False),
            ("company_id", "=", self.env.company.id),
        ], limit=1)

        if not account:
            raise UserError(_("No expense account found."))

        return account

    def _get_uae_output_vat_tax(self):
        self.ensure_one()

        tax = self.env["account.tax"].search([
            ("type_tax_use", "=", "sale"),
            ("amount", "=", 5),
            ("amount_type", "=", "percent"),
            ("company_id", "=", self.company_id.id),
            ("active", "=", True),
            ("name", "=", "5% DB"),
        ], limit=1)

        if not tax:
            tax = self.env["account.tax"].search([
                ("type_tax_use", "=", "sale"),
                ("amount", "=", 5),
                ("amount_type", "=", "percent"),
                ("company_id", "=", self.company_id.id),
                ("active", "=", True),
                ("name", "not ilike", "R C"),
                ("name", "not ilike", "Reverse"),
            ], limit=1)

        if not tax:
            raise UserError(_(
                "UAE 5% Output VAT tax is not configured for this company. "
                "Expected normal sales VAT such as '5% DB'. "
                "Do not use reverse-charge VAT for customer commission invoices."
            ))

        return tax

    # ---------------------------------------------------------
    # PARTNER HELPERS
    # ---------------------------------------------------------

    def _get_customer_partner(self):
        self.ensure_one()

        if self.customer_id:
            return self.customer_id

        if self.lead_id and self.lead_id.partner_id:
            return self.lead_id.partner_id

        raise UserError(_("Customer is required."))

    def _get_agent_partner(self):
        self.ensure_one()

        if not self.agent_id:
            raise UserError(_("Agent is required."))

        employee = self.env["hr.employee"].search([
            ("user_id", "=", self.agent_id.id)
        ], limit=1)

        if employee and employee.work_contact_id:
            return employee.work_contact_id

        if self.agent_id.partner_id:
            return self.agent_id.partner_id

        raise UserError(_("Agent partner missing."))

    def _get_developer_partner(self):
        self.ensure_one()

        if self.property_unit_id and self.property_unit_id.developer_id:
            return self.property_unit_id.developer_id

        raise UserError(_("Developer missing on property unit."))

    # ---------------------------------------------------------
    # CUSTOMER INVOICE
    # ---------------------------------------------------------

    def action_create_customer_invoice(self):
        income_account = self._get_income_account()

        for rec in self:
            if rec.customer_invoice_id:
                raise UserError(_("Customer invoice already exists."))

            partner = rec._get_customer_partner()

            amount = rec.agency_commission_amount or 0.0

            if amount <= 0:
                raise UserError(_("Agency commission amount must be greater than zero."))

            vat_tax = rec._get_tax_from_vat_treatment() if rec.vat_applicable else False

            move = self.env["account.move"].create({
                "move_type": "out_invoice",
                "partner_id": partner.id,
                "invoice_date": fields.Date.context_today(self),
                "tz_commission_id": rec.id,
                "tz_lead_id": rec.lead_id.id if rec.lead_id else False,
                "tz_property_unit_id": rec.property_unit_id.id if rec.property_unit_id else False,
                "tz_move_purpose": "customer_invoice",
                "invoice_line_ids": [(0, 0, {
                    "name": _("Real Estate Agency Commission"),
                    "quantity": 1,
                    "price_unit": amount,
                    "account_id": income_account.id,
                    "tax_ids": [(6, 0, [vat_tax.id])] if vat_tax else False,
                })],
            })

            rec.customer_invoice_id = move.id
            rec.customer_invoice_ref = move.name or move.ref or ""

        return True

    def action_register_customer_payment(self):
        self.ensure_one()

        if not self.customer_invoice_id:
            raise UserError(_("Customer invoice not found."))

        return {
            "type": "ir.actions.act_window",
            "name": _("Register Payment"),
            "res_model": "account.payment.register",
            "view_mode": "form",
            "target": "new",
            "context": {
                "active_model": "account.move",
                "active_ids": [self.customer_invoice_id.id],
            },
        }

    # ---------------------------------------------------------
    # AGENT PAYABLE
    # ---------------------------------------------------------

    def action_create_agent_payable(self):
        expense_account = self._get_expense_account()

        for rec in self:
            if rec.agent_payable_bill_id:
                raise UserError(_("Agent payable already exists."))

            partner = rec._get_agent_partner()

            amount = rec.agent_commission_amount or 0.0

            if amount <= 0:
                raise UserError(_("Agent commission amount invalid."))

            bill = self.env["account.move"].create({
                "move_type": "in_invoice",
                "partner_id": partner.id,
                "invoice_date": fields.Date.context_today(self),
                "tz_commission_id": rec.id,
                "tz_lead_id": rec.lead_id.id if rec.lead_id else False,
                "tz_property_unit_id": rec.property_unit_id.id if rec.property_unit_id else False,
                "tz_move_purpose": "agent_payable",
                "invoice_line_ids": [(0, 0, {
                    "name": _("Agent Commission Payable"),
                    "quantity": 1,
                    "price_unit": amount,
                    "account_id": expense_account.id,
                })],
            })

            rec.agent_payable_bill_id = bill.id

        return True

    # ---------------------------------------------------------
    # DEVELOPER PAYABLE
    # ---------------------------------------------------------

    def action_create_developer_payable(self):
        expense_account = self._get_expense_account()

        for rec in self:
            if rec.developer_payable_bill_id:
                raise UserError(_("Developer payable already exists."))

            partner = rec._get_developer_partner()

            amount = rec.developer_payout_amount or 0.0

            if amount <= 0:
                raise UserError(_("Developer payout amount invalid."))

            bill = self.env["account.move"].create({
                "move_type": "in_invoice",
                "partner_id": partner.id,
                "invoice_date": fields.Date.context_today(self),
                "tz_commission_id": rec.id,
                "tz_lead_id": rec.lead_id.id if rec.lead_id else False,
                "tz_property_unit_id": rec.property_unit_id.id if rec.property_unit_id else False,
                "tz_move_purpose": "developer_payable",
                "invoice_line_ids": [(0, 0, {
                    "name": _("Developer Payout Payable"),
                    "quantity": 1,
                    "price_unit": amount,
                    "account_id": expense_account.id,
                })],
            })

            rec.developer_payable_bill_id = bill.id

        return True

    # ---------------------------------------------------------
    # OPEN ACTIONS
    # ---------------------------------------------------------

    def action_open_customer_invoice(self):
        self.ensure_one()

        if not self.customer_invoice_id:
            raise UserError(_("Customer invoice not found."))

        return {
            "type": "ir.actions.act_window",
            "name": _("Customer Invoice"),
            "res_model": "account.move",
            "view_mode": "form",
            "res_id": self.customer_invoice_id.id,
            "target": "current",
        }

    def action_open_agent_payable(self):
        self.ensure_one()

        if not self.agent_payable_bill_id:
            raise UserError(_("Agent payable not found."))

        return {
            "type": "ir.actions.act_window",
            "name": _("Agent Payable"),
            "res_model": "account.move",
            "view_mode": "form",
            "res_id": self.agent_payable_bill_id.id,
            "target": "current",
        }

    def action_open_developer_payable(self):
        self.ensure_one()

        if not self.developer_payable_bill_id:
            raise UserError(_("Developer payable not found."))

        return {
            "type": "ir.actions.act_window",
            "name": _("Developer Payable"),
            "res_model": "account.move",
            "view_mode": "form",
            "res_id": self.developer_payable_bill_id.id,
            "target": "current",
        }
