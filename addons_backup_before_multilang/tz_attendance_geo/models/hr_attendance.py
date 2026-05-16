import math

from odoo import api, fields, models


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    tz_check_in_latitude = fields.Float(string="Check-in Latitude", digits=(16, 7), readonly=True)
    tz_check_in_longitude = fields.Float(string="Check-in Longitude", digits=(16, 7), readonly=True)
    tz_check_in_accuracy = fields.Float(string="Check-in Accuracy", readonly=True)
    tz_check_in_map_url = fields.Char(string="Check-in Map", compute="_compute_map_urls", store=True)

    tz_check_out_latitude = fields.Float(string="Check-out Latitude", digits=(16, 7), readonly=True)
    tz_check_out_longitude = fields.Float(string="Check-out Longitude", digits=(16, 7), readonly=True)
    tz_check_out_accuracy = fields.Float(string="Check-out Accuracy", readonly=True)
    tz_check_out_map_url = fields.Char(string="Check-out Map", compute="_compute_map_urls", store=True)

    tz_gps_status = fields.Selection(
        [
            ("ok", "OK"),
            ("warning", "Warning"),
            ("suspect", "Suspect"),
            ("no_data", "No GPS Data"),
        ],
        string="GPS Status",
        default="no_data",
        readonly=True,
    )

    tz_gps_warning = fields.Text(string="GPS Warning", readonly=True)

    tz_location_age_minutes = fields.Float(string="Location Age Minutes", readonly=True)
    tz_distance_between_checkin_checkout = fields.Float(
        string="Check-in/out Distance KM",
        readonly=True,
    )

    @api.depends(
        "tz_check_in_latitude",
        "tz_check_in_longitude",
        "tz_check_out_latitude",
        "tz_check_out_longitude",
    )
    def _compute_map_urls(self):
        for rec in self:
            if rec.tz_check_in_latitude and rec.tz_check_in_longitude:
                rec.tz_check_in_map_url = (
                    f"https://www.google.com/maps?q={rec.tz_check_in_latitude},{rec.tz_check_in_longitude}"
                )
            else:
                rec.tz_check_in_map_url = False

            if rec.tz_check_out_latitude and rec.tz_check_out_longitude:
                rec.tz_check_out_map_url = (
                    f"https://www.google.com/maps?q={rec.tz_check_out_latitude},{rec.tz_check_out_longitude}"
                )
            else:
                rec.tz_check_out_map_url = False

    def _get_config_float(self, key, default):
        value = self.env["ir.config_parameter"].sudo().get_param(key, default=str(default))
        try:
            return float(value)
        except Exception:
            return default

    def _distance_km(self, lat1, lon1, lat2, lon2):
        if not all([lat1, lon1, lat2, lon2]):
            return 0.0

        radius = 6371.0

        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)

        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = (
            math.sin(delta_phi / 2) ** 2
            + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
        )

        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return radius * c

    def _get_latest_user_location(self, user):
        Location = self.env["tz.user.location"].sudo()
        History = self.env["tz.user.location.history"].sudo()

        current_location = Location.search(
            [("user_id", "=", user.id)],
            order="last_seen desc",
            limit=1,
        )

        history_location = History.search(
            [("user_id", "=", user.id)],
            order="tracked_at desc",
            limit=1,
        )

        if current_location and history_location:
            current_time = current_location.last_seen
            history_time = history_location.tracked_at

            if history_time and current_time and history_time > current_time:
                return history_location, history_time

            return current_location, current_time

        if current_location:
            return current_location, current_location.last_seen

        if history_location:
            return history_location, history_location.tracked_at

        return False, False

    def _apply_gps_to_attendance(self, mode):
        max_age_minutes = self._get_config_float(
            "tz_attendance_geo.max_location_age_minutes",
            15,
        )
        max_accuracy = self._get_config_float(
            "tz_attendance_geo.max_accuracy_meters",
            100,
        )
        max_distance_km = self._get_config_float(
            "tz_attendance_geo.max_checkin_checkout_distance_km",
            2,
        )

        now = fields.Datetime.now()

        for rec in self:
            user = rec.employee_id.user_id

            if not user:
                rec.tz_gps_status = "no_data"
                rec.tz_gps_warning = "Employee has no linked Odoo user."
                continue

            location, location_time = rec._get_latest_user_location(user)

            if not location or not location_time:
                rec.tz_gps_status = "no_data"
                rec.tz_gps_warning = "No live tracking location found for this employee."
                continue

            age_minutes = (now - location_time).total_seconds() / 60
            rec.tz_location_age_minutes = age_minutes

            warning_messages = []

            if age_minutes > max_age_minutes:
                warning_messages.append(
                    f"Location is old: {round(age_minutes, 2)} minutes."
                )

            if location.accuracy and location.accuracy > max_accuracy:
                warning_messages.append(
                    f"GPS accuracy is weak: {location.accuracy} meters."
                )

            if mode == "check_in":
                rec.tz_check_in_latitude = location.latitude
                rec.tz_check_in_longitude = location.longitude
                rec.tz_check_in_accuracy = location.accuracy

            if mode == "check_out":
                rec.tz_check_out_latitude = location.latitude
                rec.tz_check_out_longitude = location.longitude
                rec.tz_check_out_accuracy = location.accuracy

                distance = rec._distance_km(
                    rec.tz_check_in_latitude,
                    rec.tz_check_in_longitude,
                    rec.tz_check_out_latitude,
                    rec.tz_check_out_longitude,
                )

                rec.tz_distance_between_checkin_checkout = distance

                if distance > max_distance_km:
                    warning_messages.append(
                        f"Check-in/out distance is high: {round(distance, 2)} KM."
                    )

            if warning_messages:
                rec.tz_gps_status = "suspect"
                rec.tz_gps_warning = "\n".join(warning_messages)
            else:
                rec.tz_gps_status = "ok"
                rec.tz_gps_warning = False

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)

        for rec in records:
            if rec.check_in:
                rec._apply_gps_to_attendance("check_in")

        return records

    def write(self, vals):
        result = super().write(vals)

        if "check_in" in vals:
            self._apply_gps_to_attendance("check_in")

        if "check_out" in vals:
            self._apply_gps_to_attendance("check_out")

        return result

    def action_open_check_in_map(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_url",
            "url": self.tz_check_in_map_url,
            "target": "new",
        }

    def action_open_check_out_map(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_url",
            "url": self.tz_check_out_map_url,
            "target": "new",
        }