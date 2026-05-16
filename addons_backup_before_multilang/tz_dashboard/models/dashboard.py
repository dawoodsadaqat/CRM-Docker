from odoo import models, fields
from datetime import datetime, time


class TzCrmDashboard(models.Model):
    _name = "tz.crm.dashboard"
    _description = "CRM Management Dashboard"

    name = fields.Char(default="Management Dashboard")

    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    agent_id = fields.Many2one("res.users", string="Agent")
    source_id = fields.Many2one("utm.source", string="Lead Source")
    campaign_id = fields.Many2one("utm.campaign", string="Campaign")

    total_leads = fields.Integer(string="Total Leads", compute="_compute_dashboard")
    contacted_leads = fields.Integer(string="Contacted", compute="_compute_dashboard")
    site_visit_leads = fields.Integer(string="Site Visits", compute="_compute_dashboard")
    negotiation_leads = fields.Integer(string="Negotiation", compute="_compute_dashboard")
    won_leads = fields.Integer(string="Won Leads", compute="_compute_dashboard")
    lost_leads = fields.Integer(string="Lost Leads", compute="_compute_dashboard")

    lead_to_visit_rate = fields.Float(string="Lead to Visit %", compute="_compute_dashboard")
    lead_to_won_rate = fields.Float(string="Lead to Won %", compute="_compute_dashboard")

    revenue_won = fields.Float(string="Won Revenue", compute="_compute_dashboard")
    pipeline_value = fields.Float(string="Pipeline Value", compute="_compute_dashboard")

    best_campaign = fields.Char(string="Best Campaign", compute="_compute_dashboard")
    worst_campaign = fields.Char(string="Worst Campaign", compute="_compute_dashboard")

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

        if self.campaign_id:
            domain.append(("campaign_id", "=", self.campaign_id.id))

        return domain

    def _compute_dashboard(self):
        Lead = self.env["crm.lead"]

        for rec in self:
            domain = rec._get_lead_domain()

            total = Lead.search_count(domain)
            contacted = Lead.search_count(domain + [("conversion_stage", "=", "contacted")])
            visits = Lead.search_count(domain + [("conversion_stage", "=", "site_visit")])
            negotiation = Lead.search_count(domain + [("conversion_stage", "=", "negotiation")])
            won = Lead.search_count(domain + [("conversion_stage", "=", "won")])
            lost = Lead.search_count(domain + [("conversion_stage", "=", "lost")])

            leads = Lead.search(domain)
            won_leads = leads.filtered(lambda l: l.conversion_stage == "won")
            pipeline_leads = leads.filtered(lambda l: l.conversion_stage in ["new", "contacted", "site_visit", "negotiation"])

            rec.total_leads = total
            rec.contacted_leads = contacted
            rec.site_visit_leads = visits
            rec.negotiation_leads = negotiation
            rec.won_leads = won
            rec.lost_leads = lost

            rec.lead_to_visit_rate = (visits / total * 100) if total else 0
            rec.lead_to_won_rate = (won / total * 100) if total else 0

            rec.revenue_won = sum(won_leads.mapped("deal_value"))
            rec.pipeline_value = sum(pipeline_leads.mapped("deal_value"))

            rec.best_campaign = rec._get_campaign_performance(best=True)
            rec.worst_campaign = rec._get_campaign_performance(best=False)

    def _get_campaign_performance(self, best=True):
        Lead = self.env["crm.lead"]
        campaigns = Lead.search([
            ("campaign_id", "!=", False)
        ]).mapped("campaign_id")

        if not campaigns:
            return "No campaign data"

        results = []

        for campaign in campaigns:
            total = Lead.search_count([("campaign_id", "=", campaign.id)])
            won = Lead.search_count([
                ("campaign_id", "=", campaign.id),
                ("conversion_stage", "=", "won")
            ])

            rate = (won / total * 100) if total else 0

            results.append({
                "name": campaign.name,
                "rate": rate,
                "total": total,
                "won": won,
            })

        results = sorted(results, key=lambda x: x["rate"], reverse=best)

        if not results:
            return "No campaign data"

        result = results[0]
        return f"{result['name']} - {result['rate']:.1f}% ({result['won']}/{result['total']})"

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