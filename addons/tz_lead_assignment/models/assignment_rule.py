from odoo import fields, models


class TzLeadAssignmentRule(models.Model):
    _name = "tz.lead.assignment.rule"
    _description = "Lead Assignment Rule"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)

    team_id = fields.Many2one(
        "crm.team",
        string="Sales Team",
        required=True
    )

    assignment_type = fields.Selection([
        ("manual", "Manual Only"),
        ("round_robin", "Round Robin"),
        ("least_busy", "Least Busy Agent"),
        ("location_based", "Location Based"),
        ("performance_based", "Performance Based"),
    ], string="Assignment Type", default="round_robin", required=True)

    assignment_sequence = fields.Integer(default=0)

    agent_ids = fields.Many2many(
    "res.users",
    string="Eligible Agents"
)

    location = fields.Char(
        string="Location",
        help="Used for Location Based assignment. Example: Dubai Marina"
    )

    performance_weight = fields.Float(
        string="Performance Weight",
        default=1.0
    )