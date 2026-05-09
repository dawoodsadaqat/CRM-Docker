from odoo import models, fields


class TzLeadHistory(models.Model):
    _name = "tz.lead.history"
    _description = "Lead History"
    _order = "event_time desc"

    # =====================================================
    # LEAD RELATIONS
    # =====================================================

    lead_id = fields.Many2one(
        "crm.lead",
        string="Lead",
        required=True,
        ondelete="cascade"
    )

    team_id = fields.Many2one(
        "crm.team",
        related="lead_id.team_id",
        store=True,
        string="Team"
    )

    supervisor_id = fields.Many2one(
        "res.users",
        related="lead_id.user_id",
        store=True,
        string="Supervisor"
    )

    agent_id = fields.Many2one(
        "res.users",
        related="lead_id.agent_owner_id",
        store=True,
        string="Assigned Agent"
    )

    # =====================================================
    # EVENT TYPES
    # =====================================================

    event_type = fields.Selection([
        ("lead_created", "Lead Created"),
        ("agent_assigned", "Agent Assigned"),
        ("stage_changed", "Stage Changed"),
        ("sla_breached", "SLA Breached"),
        ("assigned_from_queue", "Assigned From SLA Queue"),
        ("rescue_started", "Rescue Started"),
        ("rescue_breached", "Rescue SLA Breached"),
        ("first_response", "First Response Marked"),
        ("rescued", "Rescued"),
        ("followup_created", "Follow-up Reminder Created"),
        ("followup_done", "Follow-up Done"),
        ("escalation_created", "Escalation Created"),
        ("won", "Won"),
        ("lost", "Lost"),
        ("sla_warning_created", "SLA Warning Reminder Created"),
    ], string="Event Type", required=True)

    # =====================================================
    # USER TRACKING
    # =====================================================

    old_agent_id = fields.Many2one(
        "res.users",
        string="Old Agent"
    )

    new_agent_id = fields.Many2one(
        "res.users",
        string="New Agent"
    )

    performed_by_id = fields.Many2one(
        "res.users",
        string="Performed By",
        default=lambda self: self.env.user
    )

    # =====================================================
    # TIMELINES
    # =====================================================

    event_time = fields.Datetime(
        string="Event Time",
        default=fields.Datetime.now,
        required=True
    )

    sla_deadline = fields.Datetime(
        string="SLA Deadline"
    )

    rescue_deadline = fields.Datetime(
        string="Rescue Deadline"
    )

    # =====================================================
    # NOTES
    # =====================================================

    note = fields.Text(
        string="Notes"
    )