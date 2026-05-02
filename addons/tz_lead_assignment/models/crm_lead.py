from odoo import models, fields, api


class CrmLead(models.Model):
    _inherit = "crm.lead"

    assignment_rule_id = fields.Many2one(
        "tz.assignment.rule",
        string="Assignment Rule",
        readonly=True
    )

    auto_assigned = fields.Boolean(
        string="Auto Assigned",
        readonly=True,
        default=False
    )

    @api.model_create_multi
    def create(self, vals_list):
        leads = super().create(vals_list)

        for lead in leads:
            if not lead.user_id:
                lead._assign_lead_round_robin()

        return leads

    def _assign_lead_round_robin(self):
        for lead in self:
            rule = self.env["tz.assignment.rule"].search([
                ("active", "=", True),
                ("assignment_type", "=", "round_robin"),
            ], order="priority asc", limit=1)

            if not rule:
                continue

            next_agent = rule.get_next_agent()

            if not next_agent:
                continue

            lead.write({
                "user_id": next_agent.id,
                "assignment_rule_id": rule.id,
                "auto_assigned": True,
            })

            rule.write({
                "last_assigned_user_id": next_agent.id
            })