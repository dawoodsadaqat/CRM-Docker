from odoo import models, fields
from datetime import datetime, time


class TzAgentPerformance(models.Model):
    _name = "tz.agent.performance"
    _description = "Agent Performance"
    _order = "performance_score desc"

    name = fields.Char(default="Agent Performance")

    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    agent_id = fields.Many2one("res.users", string="Agent", required=True)

    total_leads = fields.Integer(string="Total Leads", compute="_compute_performance")
    contacted_leads = fields.Integer(string="Contacted", compute="_compute_performance")
    won_leads = fields.Integer(string="Won Leads", compute="_compute_performance")
    lost_leads = fields.Integer(string="Lost Leads", compute="_compute_performance")
    overdue_followups = fields.Integer(string="Overdue Follow-ups", compute="_compute_performance")
    stuck_leads = fields.Integer(string="Stuck Leads", compute="_compute_performance")
    avg_response_time_hours = fields.Float(string="Avg Response Hours", compute="_compute_performance")
    conversion_rate = fields.Float(string="Conversion Rate %", compute="_compute_performance")
    performance_score = fields.Float(string="Performance Score %", compute="_compute_performance")

    def _get_domain(self):
        domain = [("user_id", "=", self.agent_id.id)]

        if self.date_from:
            domain.append(("create_date", ">=", datetime.combine(self.date_from, time.min)))

        if self.date_to:
            domain.append(("create_date", "<=", datetime.combine(self.date_to, time.max)))

        return domain

    def _compute_performance(self):
        Lead = self.env["crm.lead"]

        for rec in self:
            if not rec.agent_id:
                rec.total_leads = 0
                rec.contacted_leads = 0
                rec.won_leads = 0
                rec.lost_leads = 0
                rec.overdue_followups = 0
                rec.stuck_leads = 0
                rec.avg_response_time_hours = 0
                rec.conversion_rate = 0
                rec.performance_score = 0
                continue

            domain = rec._get_domain()
            leads = Lead.search(domain)

            total = len(leads)
            contacted = len(leads.filtered(lambda l: l.conversion_stage in ["contacted", "site_visit", "negotiation", "won"]))
            won = len(leads.filtered(lambda l: l.conversion_stage == "won"))
            lost = len(leads.filtered(lambda l: l.conversion_stage == "lost"))
            overdue = len(leads.filtered(lambda l: l.followup_status == "overdue"))
            stuck = len(leads.filtered(lambda l: l.is_stuck))

            responded = leads.filtered(lambda l: l.response_time_hours > 0)
            avg_response = sum(responded.mapped("response_time_hours")) / len(responded) if responded else 0
            conversion = (won / total * 100) if total else 0

            penalty = (overdue * 5) + (stuck * 5)
            score = max(0, min(100, conversion + contacted - penalty))

            rec.total_leads = total
            rec.contacted_leads = contacted
            rec.won_leads = won
            rec.lost_leads = lost
            rec.overdue_followups = overdue
            rec.stuck_leads = stuck
            rec.avg_response_time_hours = avg_response
            rec.conversion_rate = conversion
            rec.performance_score = score