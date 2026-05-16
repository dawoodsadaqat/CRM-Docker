from odoo import models, fields


class CrmLead(models.Model):
    _inherit = "crm.lead"

    commission_ids = fields.One2many(
        "tz.commission",
        "lead_id",
        string="Commissions"
    )

    commission_count = fields.Integer(
        string="Commission Count",
        compute="_compute_commission_count"
    )

    total_commission_amount = fields.Float(
        string="Total Commission",
        compute="_compute_commission_count"
    )

    total_agent_commission_amount = fields.Float(
        string="Total Agent Commission",
        compute="_compute_commission_count"
    )

    def _compute_commission_count(self):
        for lead in self:
            commissions = lead.commission_ids
            lead.commission_count = len(commissions)
            lead.total_commission_amount = sum(commissions.mapped("agency_commission_amount"))
            lead.total_agent_commission_amount = sum(commissions.mapped("agent_commission_amount"))

    def action_view_commissions(self):
        self.ensure_one()

        agent_id = self.user_id.id if self.user_id else self.env.user.id
        manager_id = self.team_id.user_id.id if self.team_id and self.team_id.user_id else False

        return {
            "type": "ir.actions.act_window",
            "name": "Commissions",
            "res_model": "tz.commission",
            "view_mode": "tree,form",
            "domain": [("lead_id", "=", self.id)],
            "context": {
                "default_lead_id": self.id,
                "default_customer_id": self.partner_id.id if self.partner_id else False,
                "default_agent_id": agent_id,
                "default_manager_id": manager_id,
            },
        }