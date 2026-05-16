import random

from odoo import api, fields, models


class CrmLead(models.Model):
    _inherit = "crm.lead"

    agent_owner_id = fields.Many2one(
        "res.users",
        string="Assigned Agent",
        tracking=True
    )

    @api.model
    def create(self, vals):
        lead = super().create(vals)
        lead._auto_assign_agent()
        return lead

    def write(self, vals):
        res = super().write(vals)

        if "user_id" in vals:
            self._auto_assign_agent()

        return res

    def _auto_assign_agent(self):
        for lead in self:
            if not lead.user_id:
                continue

            if lead.agent_owner_id:
                continue

            team = lead._get_supervisor_team()

            if not team:
                continue

            rule = self.env["tz.lead.assignment.rule"].sudo().search([
                ("team_id", "=", team.id),
                ("active", "=", True),
            ], limit=1)

            if not rule:
                continue

            agent = lead._get_agent_by_assignment_rule(rule)

            if agent:
                lead.sudo().write({
                    "agent_owner_id": agent.id
                })

    def _get_supervisor_team(self):
        self.ensure_one()

        if self.team_id:
            return self.team_id

        if not self.user_id:
            return False

        return self.env["crm.team"].sudo().search([
            "|",
            ("user_id", "=", self.user_id.id),
            ("member_ids", "in", [self.user_id.id])
        ], limit=1)

    def _get_agent_by_assignment_rule(self, rule):
        self.ensure_one()

        agents = rule.agent_ids.filtered(
            lambda user: user.active and user.has_group("tz_crm_base.group_tz_crm_agent")
        )

        if not agents:
            agents = rule.team_id.member_ids.filtered(
                lambda user: user.active and user.has_group("tz_crm_base.group_tz_crm_agent")
            )

        if not agents:
            return False

        if rule.assignment_type == "manual":
            return False

        if rule.assignment_type == "round_robin":
            return self._get_round_robin_agent(rule, agents)

        if rule.assignment_type == "least_busy":
            return self._get_least_busy_agent(agents)

        if rule.assignment_type == "location_based":
            return self._get_location_based_agent(rule, agents)

        if rule.assignment_type == "performance_based":
            return self._get_performance_based_agent(agents)

        return False

    def _get_round_robin_agent(self, rule, agents):
        index = rule.assignment_sequence % len(agents)
        agent = agents[index]

        rule.sudo().write({
            "assignment_sequence": rule.assignment_sequence + 1
        })

        return agent

    def _get_least_busy_agent(self, agents):
        agent_load = []

        for agent in agents:
            count = self.env["crm.lead"].sudo().search_count([
                ("agent_owner_id", "=", agent.id),
                ("active", "=", True),
                ("type", "=", "lead"),
            ])

            agent_load.append((agent, count))

        agent_load.sort(key=lambda item: item[1])

        return agent_load[0][0] if agent_load else False

    def _get_location_based_agent(self, rule, agents):
        if not self.preferred_location:
            return self._get_least_busy_agent(agents)

        lead_location = self.preferred_location.strip().lower()

        matched_agents = agents.filtered(
            lambda agent: rule.location and rule.location.strip().lower() in lead_location
        )

        if matched_agents:
            return self._get_least_busy_agent(matched_agents)

        return self._get_least_busy_agent(agents)

    def _get_performance_based_agent(self, agents):
        sorted_agents = sorted(
            agents,
            key=lambda agent: getattr(agent, "tz_performance_score", 0) or 0,
            reverse=True
        )

        return sorted_agents[0] if sorted_agents else False