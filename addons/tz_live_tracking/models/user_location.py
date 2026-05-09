from odoo import api, fields, models
import secrets


class ResUsers(models.Model):
    _inherit = "res.users"

    tz_location_tracking_enabled = fields.Boolean(
        string="Location Tracking Enabled",
        default=True
    )

    tz_location_token = fields.Char(
        string="Location API Token",
        copy=False,
        readonly=True
    )

    def action_generate_location_token(self):
        for user in self:
            user.tz_location_token = secrets.token_urlsafe(32)
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Token Generated",
                "message": "Location tracking token generated successfully.",
                "type": "success",
                "sticky": False,
            }
        }

class TzUserLocation(models.Model):
    _name = "tz.user.location"
    _description = "User Live Location"
    _order = "last_seen desc"

    user_id = fields.Many2one(
        "res.users",
        string="User",
        required=True,
        ondelete="cascade"
    )

    name = fields.Char(
        related="user_id.name",
        store=True
    )

    latitude = fields.Float(required=True)
    longitude = fields.Float(required=True)

    accuracy = fields.Float()
    battery_level = fields.Float()

    last_seen = fields.Datetime(
        default=fields.Datetime.now
    )

    team_ids = fields.Many2many(
        "crm.team",
        compute="_compute_team_ids",
        store=True
    )

    is_online = fields.Boolean(
        compute="_compute_is_online"
    )

    map_url = fields.Char(
        compute="_compute_map_url"
    )

    @api.model
    def _get_config(self):
        config = self.env["tz.live.tracking.config"].sudo().search([], limit=1)
        if not config:
            config = self.env["tz.live.tracking.config"].sudo().create({
                "name": "Live Tracking Settings"
            })
        return config

    @api.depends("user_id")
    def _compute_team_ids(self):
        Team = self.env["crm.team"].sudo()

        for rec in self:
            teams = Team.search([
                "|",
                ("user_id", "=", rec.user_id.id),
                ("member_ids", "in", [rec.user_id.id])
            ])
            rec.team_ids = [(6, 0, teams.ids)]

    def _compute_is_online(self):
        now = fields.Datetime.now()
        config = self._get_config()
        threshold = config.online_threshold_seconds or 300

        for rec in self:
            if not rec.last_seen:
                rec.is_online = False
            else:
                rec.is_online = (now - rec.last_seen).total_seconds() <= threshold

    def _compute_map_url(self):
        for rec in self:
            rec.map_url = (
                f"https://www.google.com/maps?q={rec.latitude},{rec.longitude}"
                if rec.latitude and rec.longitude
                else False
            )