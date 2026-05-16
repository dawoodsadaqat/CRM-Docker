from odoo import fields, models


class TzLiveTrackingConfig(models.Model):
    _name = "tz.live.tracking.config"
    _description = "Live Tracking Configuration"

    name = fields.Char(default="Live Tracking Settings", required=True)

    update_interval_seconds = fields.Integer(
        string="Location Update Interval Seconds",
        default=15,
        required=True
    )

    online_threshold_seconds = fields.Integer(
        string="Online Threshold Seconds",
        default=300,
        required=True
    )

    tracking_enabled = fields.Boolean(
        string="Tracking Enabled",
        default=True
    )