from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    tz_commission_id = fields.Many2one(
        "tz.commission",
        string="Commission Record",
        readonly=True,
        copy=False,
    )

    tz_lead_id = fields.Many2one(
        "crm.lead",
        string="CRM Lead",
        readonly=True,
        copy=False,
    )

    tz_property_unit_id = fields.Many2one(
        "tz.property.unit",
        string="Property Unit",
        readonly=True,
        copy=False,
    )

    tz_move_purpose = fields.Selection(
        [
            ("customer_invoice", "Customer Invoice"),
            ("agent_payable", "Agent Payable"),
            ("developer_payable", "Developer Payable"),
        ],
        string="Purpose",
        readonly=True,
        copy=False,
    )