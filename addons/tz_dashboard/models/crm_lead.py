from odoo import models, fields, api
from datetime import timedelta


class CrmLead(models.Model):
    _inherit = "crm.lead"

    conversion_stage = fields.Selection([
        ("new", "New"),
        ("contacted", "Contacted"),
        ("site_visit", "Site Visit"),
        ("negotiation", "Negotiation"),
        ("won", "Won"),
        ("lost", "Lost"),
    ], string="Conversion Stage", default="new", tracking=True)

    conversion_stage_date = fields.Datetime(
        string="Last Conversion Update",
        default=fields.Datetime.now
    )

    deal_value = fields.Float(string="Deal Value")

    first_response_date = fields.Datetime(string="First Response Date")
    response_time_hours = fields.Float(
        string="Response Time Hours",
        compute="_compute_response_time_hours",
        store=True
    )

    sla_deadline = fields.Datetime(
        string="SLA Deadline",
        compute="_compute_sla_deadline",
        store=True
    )

    sla_status = fields.Selection([
        ("pending", "Pending"),
        ("met", "Met"),
        ("breached", "Breached"),
    ], string="SLA Status", compute="_compute_sla_status", store=True)

    next_followup_date = fields.Datetime(string="Next Follow-up Date")

    followup_status = fields.Selection([
        ("no_followup", "No Follow-up"),
        ("planned", "Planned"),
        ("overdue", "Overdue"),
        ("done", "Done"),
    ], string="Follow-up Status", compute="_compute_followup_status", store=True)

    lead_age_days = fields.Integer(
        string="Lead Age Days",
        compute="_compute_lead_age_days",
        store=True
    )

    stage_age_days = fields.Integer(
        string="Stage Age Days",
        compute="_compute_stage_age_days",
        store=True
    )

    is_stuck = fields.Boolean(
        string="Stuck Lead",
        compute="_compute_is_stuck",
        store=True
    )

    @api.onchange("conversion_stage")
    def _onchange_conversion_stage(self):
        for lead in self:
            lead.conversion_stage_date = fields.Datetime.now()

    @api.depends("create_date", "first_response_date")
    def _compute_response_time_hours(self):
        for lead in self:
            if lead.create_date and lead.first_response_date:
                delta = lead.first_response_date - lead.create_date
                lead.response_time_hours = delta.total_seconds() / 3600
            else:
                lead.response_time_hours = 0

    @api.depends("create_date")
    def _compute_sla_deadline(self):
        for lead in self:
            lead.sla_deadline = lead.create_date + timedelta(hours=2) if lead.create_date else False

    @api.depends("first_response_date", "sla_deadline")
    def _compute_sla_status(self):
        now = fields.Datetime.now()
        for lead in self:
            if lead.first_response_date and lead.sla_deadline:
                lead.sla_status = "met" if lead.first_response_date <= lead.sla_deadline else "breached"
            elif lead.sla_deadline and now > lead.sla_deadline:
                lead.sla_status = "breached"
            else:
                lead.sla_status = "pending"

    @api.depends("next_followup_date")
    def _compute_followup_status(self):
        now = fields.Datetime.now()
        for lead in self:
            if not lead.next_followup_date:
                lead.followup_status = "no_followup"
            elif lead.next_followup_date < now:
                lead.followup_status = "overdue"
            else:
                lead.followup_status = "planned"

    @api.depends("create_date")
    def _compute_lead_age_days(self):
        now = fields.Datetime.now()
        for lead in self:
            if lead.create_date:
                lead.lead_age_days = (now - lead.create_date).days
            else:
                lead.lead_age_days = 0

    @api.depends("conversion_stage_date")
    def _compute_stage_age_days(self):
        now = fields.Datetime.now()
        for lead in self:
            if lead.conversion_stage_date:
                lead.stage_age_days = (now - lead.conversion_stage_date).days
            else:
                lead.stage_age_days = 0

    @api.depends("conversion_stage", "stage_age_days")
    def _compute_is_stuck(self):
        for lead in self:
            lead.is_stuck = (
                lead.conversion_stage not in ["won", "lost"]
                and lead.stage_age_days >= 3
            )

    def action_mark_first_response(self):
        for lead in self:
            if not lead.first_response_date:
                lead.first_response_date = fields.Datetime.now()
            lead.conversion_stage = "contacted"
            lead.conversion_stage_date = fields.Datetime.now()

    def action_mark_followup_done(self):
        for lead in self:
            lead.next_followup_date = False

    def write(self, vals):
        if "conversion_stage" in vals:
            vals["conversion_stage_date"] = fields.Datetime.now()
        return super().write(vals)