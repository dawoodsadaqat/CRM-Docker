from odoo import models, fields


class TzAssignmentRule(models.Model):
    _name = "tz.assignment.rule"
    _description = "Lead Assignment Rule"
    _order = "priority asc, id asc"

    name = fields.Char(string="Rule Name", required=True)

    active = fields.Boolean(string="Active", default=True)

    assignment_type = fields.Selection([
        ("round_robin", "Round Robin"),
        ("manual", "Manual"),
    ], string="Assignment Type", default="round_robin", required=True)

    agent_ids = fields.Many2many(
        "res.users",
        string="Agents",
        required=True
    )

    priority = fields.Integer(string="Priority", default=10)

    last_assigned_user_id = fields.Many2one(
        "res.users",
        string="Last Assigned Agent",
        readonly=True
    )

    lead_count = fields.Integer(
        string="Assigned Leads Count",
        compute="_compute_lead_count"
    )

    def _compute_lead_count(self):
        for rule in self:
            rule.lead_count = self.env["crm.lead"].search_count([
                ("assignment_rule_id", "=", rule.id)
            ])

    def get_next_agent(self):
        self.ensure_one()

        agents = self.agent_ids
        if not agents:
            return False

        if not self.last_assigned_user_id:
            return agents[0]

        agent_ids = agents.ids

        if self.last_assigned_user_id.id not in agent_ids:
            return agents[0]

        current_index = agent_ids.index(self.last_assigned_user_id.id)
        next_index = (current_index + 1) % len(agent_ids)

        return self.env["res.users"].browse(agent_ids[next_index])