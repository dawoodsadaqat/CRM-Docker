from odoo import models, fields, api
from datetime import datetime, time


class TzCrmDashboard(models.Model):
    _name = "tz.crm.dashboard"
    _description = "CRM Management Dashboard"

    name = fields.Char(default="Management Dashboard")

    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    agent_id = fields.Many2one("res.users", string="Agent")
    source_id = fields.Many2one("utm.source", string="Lead Source")

    total_leads = fields.Integer(string="Total Leads", compute="_compute_dashboard")
    hot_leads = fields.Integer(string="Hot Leads", compute="_compute_dashboard")
    overdue_followups = fields.Integer(string="Follow-ups Overdue", compute="_compute_dashboard")
    site_visits_scheduled = fields.Integer(string="Site Visits Scheduled", compute="_compute_dashboard")
    deals_won = fields.Integer(string="Deals Won", compute="_compute_dashboard")
    lost_leads = fields.Integer(string="Lost Leads", compute="_compute_dashboard")
    revenue_pipeline = fields.Float(string="Revenue Pipeline", compute="_compute_dashboard")
    commission_payable = fields.Float(string="Commission Payable", compute="_compute_dashboard")

    def _get_lead_domain(self):
        domain = []

        if self.date_from:
            domain.append(("create_date", ">=", datetime.combine(self.date_from, time.min)))

        if self.date_to:
            domain.append(("create_date", "<=", datetime.combine(self.date_to, time.max)))

        if self.agent_id:
            domain.append(("user_id", "=", self.agent_id.id))

        if self.source_id:
            domain.append(("source_id", "=", self.source_id.id))

        return domain

    def _compute_dashboard(self):
        Lead = self.env["crm.lead"]
        SiteVisit = self.env["tz.site.visit"]
        Commission = self.env["tz.commission"]

        for rec in self:
            lead_domain = rec._get_lead_domain()

            rec.total_leads = Lead.search_count(lead_domain)

            rec.hot_leads = Lead.search_count(
                lead_domain + [("lead_temperature", "=", "hot")]
            )

            rec.overdue_followups = Lead.search_count(
                lead_domain + [
                    ("next_followup_date", "!=", False),
                    ("next_followup_date", "<", fields.Datetime.now()),
                ]
            )

            rec.deals_won = Lead.search_count(
                lead_domain + [("stage_id.is_won", "=", True)]
            )

            rec.lost_leads = Lead.search_count(
                lead_domain + [("active", "=", False)]
            )

            pipeline_leads = Lead.search(lead_domain)
            rec.revenue_pipeline = sum(pipeline_leads.mapped("expected_revenue"))

            visit_domain = [("status", "in", ["scheduled", "confirmed"])]

            if rec.date_from:
                visit_domain.append(("visit_datetime", ">=", datetime.combine(rec.date_from, time.min)))

            if rec.date_to:
                visit_domain.append(("visit_datetime", "<=", datetime.combine(rec.date_to, time.max)))

            if rec.agent_id:
                visit_domain.append(("agent_id", "=", rec.agent_id.id))

            rec.site_visits_scheduled = SiteVisit.search_count(visit_domain)

            commission_domain = [
                ("approval_status", "=", "approved"),
                ("payment_status", "in", ["unpaid", "partially_paid"]),
            ]

            if rec.agent_id:
                commission_domain.append(("agent_id", "=", rec.agent_id.id))

            commissions = Commission.search(commission_domain)
            rec.commission_payable = sum(commissions.mapped("remaining_amount"))

    def action_refresh_dashboard(self):
        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }

    def action_open_leads(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Leads",
            "res_model": "crm.lead",
            "view_mode": "tree,form",
            "domain": self._get_lead_domain(),
        }

    def action_open_hot_leads(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Hot Leads",
            "res_model": "crm.lead",
            "view_mode": "tree,form",
            "domain": self._get_lead_domain() + [("lead_temperature", "=", "hot")],
        }

    def action_open_overdue_followups(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Overdue Follow-ups",
            "res_model": "crm.lead",
            "view_mode": "tree,form",
            "domain": self._get_lead_domain() + [
                ("next_followup_date", "!=", False),
                ("next_followup_date", "<", fields.Datetime.now()),
            ],
        }

    def action_open_site_visits(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Scheduled Site Visits",
            "res_model": "tz.site.visit",
            "view_mode": "tree,form",
            "domain": [("status", "in", ["scheduled", "confirmed"])],
        }

    def action_open_commissions(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Commission Payable",
            "res_model": "tz.commission",
            "view_mode": "tree,form",
            "domain": [
                ("approval_status", "=", "approved"),
                ("payment_status", "in", ["unpaid", "partially_paid"]),
            ],
        }