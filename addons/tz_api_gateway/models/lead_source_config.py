from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class TzLeadConfig(models.Model):
    _name = "tz.lead.config"
    _description = "Lead Configuration"
    _order = "company_id"

    name = fields.Char(
        string="Configuration Name",
        required=True,
        default="Lead Configuration"
    )

    company_id = fields.Many2one(
        "res.company",
        string="Organization",
        default=lambda self: self.env.company,
        required=True
    )

    active = fields.Boolean(default=True)

    default_supervisor_id = fields.Many2one(
        "res.users",
        string="Default Supervisor"
    )

    default_agent_id = fields.Many2one(
        "res.users",
        string="Default Agent"
    )

    supervisor_display_name = fields.Char(
        string="Supervisor - Team",
        compute="_compute_user_display_names"
    )

    agent_display_name = fields.Char(
        string="Agent - Team",
        compute="_compute_user_display_names"
    )

    integration_ids = fields.One2many(
        "tz.lead.integration",
        "lead_config_id",
        string="Lead Integrations"
    )

    notes = fields.Text(string="Notes")

    def _get_user_team_name(self, user):
        if not user:
            return ""

        team = self.env["crm.team"].sudo().search([
            "|",
            ("user_id", "=", user.id),
            ("member_ids", "in", [user.id])
        ], limit=1)

        return team.name if team else "No Team"

    @api.depends("default_supervisor_id", "default_agent_id")
    def _compute_user_display_names(self):
        for rec in self:
            rec.supervisor_display_name = False
            rec.agent_display_name = False

            if rec.default_supervisor_id:
                team_name = rec._get_user_team_name(rec.default_supervisor_id)
                rec.supervisor_display_name = f"{rec.default_supervisor_id.name} - {team_name}"

            if rec.default_agent_id:
                team_name = rec._get_user_team_name(rec.default_agent_id)
                rec.agent_display_name = f"{rec.default_agent_id.name} - {team_name}"

    @api.onchange("default_supervisor_id")
    def _onchange_default_supervisor_id(self):
        if self.default_supervisor_id and self.default_agent_id:
            self.default_agent_id = False
            return {
                "warning": {
                    "title": _("Assignment Updated"),
                    "message": _("Only one routing target is allowed. Agent was cleared because Supervisor is now selected."),
                }
            }

    @api.onchange("default_agent_id")
    def _onchange_default_agent_id(self):
        if self.default_agent_id and self.default_supervisor_id:
            self.default_supervisor_id = False
            return {
                "warning": {
                    "title": _("Assignment Updated"),
                    "message": _("Only one routing target is allowed. Supervisor was cleared because Agent is now selected."),
                }
            }

    @api.constrains("default_supervisor_id", "default_agent_id")
    def _check_only_one_assignment_target(self):
        for rec in self:
            if rec.default_supervisor_id and rec.default_agent_id:
                raise ValidationError(_("Select either Default Supervisor or Default Agent, not both."))

    @api.constrains("default_supervisor_id", "default_agent_id")
    def _check_user_roles(self):
        for rec in self:
            if rec.default_supervisor_id and not rec.default_supervisor_id.has_group("tz_crm_base.group_tz_crm_manager"):
                raise ValidationError(_("Default Supervisor must be a CRM Manager."))

            if rec.default_agent_id:
                if not rec.default_agent_id.has_group("tz_crm_base.group_tz_crm_agent"):
                    raise ValidationError(_("Default Agent must be a CRM Agent."))

                if rec.default_agent_id.has_group("tz_crm_base.group_tz_crm_manager"):
                    raise ValidationError(_("Default Agent cannot be a CRM Manager."))


class TzLeadIntegration(models.Model):
    _name = "tz.lead.integration"
    _description = "Lead Integration"
    _order = "source_type, integration_code"

    lead_config_id = fields.Many2one(
        "tz.lead.config",
        string="Lead Configuration",
        required=True,
        ondelete="cascade"
    )

    company_id = fields.Many2one(
        related="lead_config_id.company_id",
        string="Organization",
        store=True,
        readonly=True
    )

    active = fields.Boolean(default=True)

    name = fields.Char(
        string="Integration Name",
        required=True
    )

    source_type = fields.Selection([
        ("website", "Website"),
        ("meta", "Meta"),
        ("whatsapp", "WhatsApp"),
    ], string="Source Type", required=True)

    integration_code = fields.Char(
        string="Integration Code",
        required=True,
        help="Example: website_main, meta_dubai, whatsapp_sales"
    )

    api_key = fields.Char(
        string="API Key",
        required=True
    )

    website_domain = fields.Char(string="Website Domain")

    meta_page_id = fields.Char(string="Meta Page ID")
    meta_page_name = fields.Char(string="Meta Page Name")
    meta_campaign_id = fields.Char(string="Meta Campaign ID")
    meta_campaign_name = fields.Char(string="Meta Campaign Name")

    whatsapp_phone_number_id = fields.Char(string="WhatsApp Phone Number ID")
    whatsapp_business_account_id = fields.Char(string="WhatsApp Business Account ID")

    notes = fields.Text(string="Notes")

    _sql_constraints = [
        (
            "unique_integration_code_api_key",
            "unique(integration_code, api_key)",
            "Integration Code and API Key must be unique."
        )
    ]