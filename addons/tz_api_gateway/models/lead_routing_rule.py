from odoo import api, fields, models
from odoo.exceptions import ValidationError


class TzLeadRoutingRule(models.Model):
    _name = "tz.lead.routing.rule"
    _description = "Lead Routing Rule"
    _order = "priority asc, id asc"

    name = fields.Char(required=True)

    active = fields.Boolean(default=True)

    company_id = fields.Many2one(
        "res.company",
        string="Organization",
        required=True,
        default=lambda self: self.env.company
    )

    priority = fields.Integer(
        string="Priority",
        default=10,
        help="Lower number means higher priority."
    )

    # =====================================================
    # MULTISELECT ROUTING FIELDS
    # =====================================================

    allowed_source_ids = fields.Many2many(
        "tz.lead.integration",
        string="Allowed Sources"
    )

    property_type_ids = fields.Many2many(
        "tz.property.type",
        string="Property Types"
    )

    lead_temperature_ids = fields.Many2many(
        "tz.lead.temperature",
        string="Lead Temperatures"
    )

    # =====================================================
    # ADDITIONAL FILTERS
    # =====================================================

    preferred_location = fields.Char(
        string="Preferred Location"
    )

    budget_min = fields.Float(
        string="Budget Min"
    )

    budget_max = fields.Float(
        string="Budget Max"
    )

    # =====================================================
    # ASSIGNMENT
    # =====================================================

    assign_supervisor_id = fields.Many2one(
        "res.users",
        string="Assign Supervisor"
    )

    assign_agent_id = fields.Many2one(
        "res.users",
        string="Assign Agent"
    )

    # =====================================================
    # DISPLAY FIELDS
    # =====================================================

    supervisor_display_name = fields.Char(
        string="Supervisor - Team",
        compute="_compute_user_display_names"
    )

    agent_display_name = fields.Char(
        string="Agent - Team",
        compute="_compute_user_display_names"
    )

    notes = fields.Text()

    # =====================================================
    # TEAM DISPLAY HELPER
    # =====================================================

    def _get_user_team_name(self, user):
        if not user:
            return ""

        team = self.env["crm.team"].sudo().search([
            "|",
            ("user_id", "=", user.id),
            ("member_ids", "in", [user.id])
        ], limit=1)

        return team.name if team else "No Team"

    # =====================================================
    # COMPUTE DISPLAY NAMES
    # =====================================================

    @api.depends("assign_supervisor_id", "assign_agent_id")
    def _compute_user_display_names(self):
        for rec in self:
            rec.supervisor_display_name = False
            rec.agent_display_name = False

            if rec.assign_supervisor_id:
                team_name = rec._get_user_team_name(rec.assign_supervisor_id)
                rec.supervisor_display_name = (
                    f"{rec.assign_supervisor_id.name} - {team_name}"
                )

            if rec.assign_agent_id:
                team_name = rec._get_user_team_name(rec.assign_agent_id)
                rec.agent_display_name = (
                    f"{rec.assign_agent_id.name} - {team_name}"
                )

    # =====================================================
    # ONCHANGE VALIDATION
    # =====================================================

    @api.onchange("assign_supervisor_id")
    def _onchange_assign_supervisor_id(self):
        if self.assign_supervisor_id and self.assign_agent_id:
            self.assign_agent_id = False

            return {
                "warning": {
                    "title": "Assignment Updated",
                    "message": (
                        "Only one routing target is allowed. "
                        "Agent was cleared because Supervisor is selected."
                    ),
                }
            }

    @api.onchange("assign_agent_id")
    def _onchange_assign_agent_id(self):
        if self.assign_agent_id and self.assign_supervisor_id:
            self.assign_supervisor_id = False

            return {
                "warning": {
                    "title": "Assignment Updated",
                    "message": (
                        "Only one routing target is allowed. "
                        "Supervisor was cleared because Agent is selected."
                    ),
                }
            }

    # =====================================================
    # ONLY ONE TARGET VALIDATION
    # =====================================================

    @api.constrains("assign_supervisor_id", "assign_agent_id")
    def _check_only_one_assignment_target(self):
        for rec in self:
            if rec.assign_supervisor_id and rec.assign_agent_id:
                raise ValidationError(
                    "Select either Assign Supervisor or Assign Agent, not both."
                )

    # =====================================================
    # ROLE VALIDATION
    # =====================================================

    @api.constrains("assign_supervisor_id", "assign_agent_id")
    def _check_user_roles(self):
        for rec in self:

            if rec.assign_supervisor_id:
                if not rec.assign_supervisor_id.has_group(
                    "tz_crm_base.group_tz_crm_manager"
                ):
                    raise ValidationError(
                        "Assign Supervisor must be a CRM Manager."
                    )

            if rec.assign_agent_id:
                if not rec.assign_agent_id.has_group(
                    "tz_crm_base.group_tz_crm_agent"
                ):
                    raise ValidationError(
                        "Assign Agent must be a CRM Agent."
                    )

                if rec.assign_agent_id.has_group(
                    "tz_crm_base.group_tz_crm_manager"
                ):
                    raise ValidationError(
                        "Assign Agent cannot be a CRM Manager."
                    )