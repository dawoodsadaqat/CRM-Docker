from odoo import models, fields


class TzUserLocation(models.Model):
    _name = "tz.user.location"
    _description = "Latest User Location"
    _order = "last_seen desc"

    user_id = fields.Many2one(
        "res.users",
        string="User",
        required=True,
        index=True,
        ondelete="cascade"
    )

    latitude = fields.Float(string="Latitude", digits=(16, 8), required=True)
    longitude = fields.Float(string="Longitude", digits=(16, 8), required=True)
    accuracy = fields.Float(string="Accuracy")
    battery_level = fields.Float(string="Battery Level")
    last_seen = fields.Datetime(string="Last Seen", default=fields.Datetime.now)

    supervisor_id = fields.Many2one(
        related="user_id.sale_team_id.user_id",
        string="Supervisor",
        store=False
    )

    def action_open_map(self):
        self.ensure_one()

        url = "https://www.google.com/maps?q=%s,%s" % (
            self.latitude,
            self.longitude,
        )

        return {
            "type": "ir.actions.act_url",
            "url": url,
            "target": "new",
        }


class TzUserLocationHistory(models.Model):
    _name = "tz.user.location.history"
    _description = "User Location History"
    _order = "tracked_at desc"

    user_id = fields.Many2one(
        "res.users",
        string="User",
        required=True,
        index=True,
        ondelete="cascade"
    )

    latitude = fields.Float(string="Latitude", digits=(16, 8), required=True)
    longitude = fields.Float(string="Longitude", digits=(16, 8), required=True)
    accuracy = fields.Float(string="Accuracy")
    battery_level = fields.Float(string="Battery Level")
    tracked_at = fields.Datetime(string="Tracked At", default=fields.Datetime.now)

    supervisor_id = fields.Many2one(
        related="user_id.sale_team_id.user_id",
        string="Supervisor",
        store=False
    )

    def action_open_map(self):
        self.ensure_one()

        url = "https://www.google.com/maps?q=%s,%s" % (
            self.latitude,
            self.longitude,
        )

        return {
            "type": "ir.actions.act_url",
            "url": url,
            "target": "new",
        }