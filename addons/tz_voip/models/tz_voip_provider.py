from odoo import fields, models


class TzVoipProvider(models.Model):
    _name = "tz.voip.provider"
    _description = "VOIP Provider Configuration"
    _order = "sequence, id"

    name = fields.Char(required=True)

    sequence = fields.Integer(default=10)

    active = fields.Boolean(default=True)

    provider_type = fields.Selection([
        ("asterisk", "Asterisk / FreePBX"),
        ("twilio", "Twilio"),
        ("generic", "Generic Webhook Provider"),
    ], string="Provider Type", required=True, default="asterisk")

    call_mode = fields.Selection([
        ("manual_softphone", "Manual Softphone"),
        ("ami_originate", "Asterisk AMI Originate"),
        ("api", "Provider API"),
        ("tel_link", "Browser Tel Link"),
    ], string="Call Mode", required=True, default="manual_softphone")

    host = fields.Char(string="Host / Server IP")
    port = fields.Integer(string="Port", default=5038)

    username = fields.Char(string="Username / AMI User")
    password = fields.Char(string="Password / Secret")

    default_context = fields.Char(
        string="Default Context",
        default="from-internal"
    )

    webhook_api_key = fields.Char(
        string="Webhook API Key",
        default="demo-secret-key",
        required=True,
    )

    webhook_url = fields.Char(
        string="Webhook URL",
        compute="_compute_webhook_url",
    )

    recording_base_url = fields.Char(
        string="Recording Base URL",
        help="Optional base URL if recordings are exposed through web server."
    )

    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company,
        required=True,
    )

    def _compute_webhook_url(self):
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        for rec in self:
            rec.webhook_url = "%s/api/voip/call-event" % base_url