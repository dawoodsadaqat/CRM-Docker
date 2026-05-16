from odoo import models, fields
import uuid


class ResUsers(models.Model):
    _inherit = "res.users"

    tz_tracking_enabled = fields.Boolean(
        string="Live Tracking Enabled",
        default=True
    )

    tz_tracking_status = fields.Selection(
        [
            ("stopped", "Stopped"),
            ("active", "Active"),
        ],
        string="Tracking Status",
        default="stopped"
    )

    tz_last_latitude = fields.Float(string="Last Latitude", digits=(16, 8))
    tz_last_longitude = fields.Float(string="Last Longitude", digits=(16, 8))
    tz_last_accuracy = fields.Float(string="Last Accuracy")
    tz_last_seen = fields.Datetime(string="Last Location Update")

    # Compatibility fields for your old broken views/code
    tz_location_tracking_enabled = fields.Boolean(
        string="Live Tracking Enabled",
        related="tz_tracking_enabled",
        readonly=False,
        store=True
    )

    tz_location_token = fields.Char(
        string="Location Token",
        default=lambda self: str(uuid.uuid4()),
        copy=False
    )

    def action_generate_location_token(self):
        for user in self:
            user.tz_location_token = str(uuid.uuid4())