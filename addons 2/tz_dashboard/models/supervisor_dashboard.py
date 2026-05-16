from odoo import models, fields
from datetime import datetime, time


class TzSupervisorDashboard(models.Model):
    _name = "tz.supervisor.dashboard"
    _description = "Supervisor Dashboard"

    name = fields.Char(default="Supervisor Dashboard")

    supervisor_id = fields.Many2one(
        "res.users",
        string="Supervisor",
        default=lambda self: self.env.user,
        required=True
    )

    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")

    total_agent_reminders = fields.Integer(
        string="Agent Reminders",
        compute="_compute_dashboard"
    )

    overdue_reminders = fields.Integer(
        string="Overdue Reminders",
        compute="_compute_dashboard"
    )

    sla_breached_leads = fields.Integer(
        string="SLA Breached Leads",
        compute="_compute_dashboard"
    )

    stuck_leads = fields.Integer(
        string="Stuck Leads",
        compute="_compute_dashboard"
    )

    agent_ids = fields.Many2many(
        "res.users",
        string="Agents",
        compute="_compute_dashboard"
    )

    def _get_agent_ids(self):
        self.ensure_one()
        return self.env["res.users"].search([
            ("supervisor_id", "=", self.supervisor_id.id)
        ])

    def _get_date_domain(self):
        domain = []

        if self.date_from:
            domain.append(("create_date", ">=", datetime.combine(self.date_from, time.min)))

        if self.date_to:
            domain.append(("create_date", "<=", datetime.combine(self.date_to, time.max)))

        return domain

    def _compute_dashboard(self):
        Activity = self.env["mail.activity"]
        Lead = self.env["crm.lead"]

        for rec in self:
            agents = rec._get_agent_ids()
            agent_ids = agents.ids

            rec.agent_ids = [(6, 0, agent_ids)]

            activity_domain = [
                ("summary", "=", "Follow-up Reminder"),
                ("res_model", "=", "crm.lead"),
                ("user_id", "in", agent_ids),
            ]

            lead_domain = [
                ("user_id", "in", agent_ids),
            ] + rec._get_date_domain()

            rec.total_agent_reminders = Activity.search_count(activity_domain)

            rec.overdue_reminders = Activity.search_count(
                activity_domain + [
                    ("date_deadline", "<", fields.Date.today()),
                ]
            )

            rec.sla_breached_leads = Lead.search_count(
                lead_domain + [
                    ("sla_status", "=", "breached"),
                ]
            )

            rec.stuck_leads = Lead.search_count(
                lead_domain + [
                    ("is_stuck", "=", True),
                ]
            )

    def action_open_agent_reminders(self):
        self.ensure_one()
        agents = self._get_agent_ids()

        return {
            "type": "ir.actions.act_window",
            "name": "Agent Follow-up Reminders",
            "res_model": "mail.activity",
            "view_mode": "tree,form",
            "domain": [
                ("summary", "=", "Follow-up Reminder"),
                ("res_model", "=", "crm.lead"),
                ("user_id", "in", agents.ids),
            ],
        }

    def action_open_overdue_reminders(self):
        self.ensure_one()
        agents = self._get_agent_ids()

        return {
            "type": "ir.actions.act_window",
            "name": "Overdue Follow-ups",
            "res_model": "mail.activity",
            "view_mode": "tree,form",
            "domain": [
                ("summary", "=", "Follow-up Reminder"),
                ("res_model", "=", "crm.lead"),
                ("user_id", "in", agents.ids),
                ("date_deadline", "<", fields.Date.today()),
            ],
        }

    def action_open_sla_breaches(self):
        self.ensure_one()
        agents = self._get_agent_ids()

        return {
            "type": "ir.actions.act_window",
            "name": "SLA Breached Leads",
            "res_model": "crm.lead",
            "view_mode": "tree,form",
            "domain": [
                ("user_id", "in", agents.ids),
                ("sla_status", "=", "breached"),
            ],
        }

    def action_open_stuck_leads(self):
        self.ensure_one()
        agents = self._get_agent_ids()

        return {
            "type": "ir.actions.act_window",
            "name": "Stuck Leads",
            "res_model": "crm.lead",
            "view_mode": "tree,form",
            "domain": [
                ("user_id", "in", agents.ids),
                ("is_stuck", "=", True),
            ],
        }

    def action_refresh_dashboard(self):
        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }