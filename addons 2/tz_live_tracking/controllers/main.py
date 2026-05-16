from odoo import _, http, fields
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class TzLiveTrackingController(http.Controller):

    @http.route(
        "/api/tz/location/update",
        type="json",
        auth="user",
        csrf=False,
        methods=["POST"]
    )
    def update_location(self, latitude=None, longitude=None, accuracy=None, battery_level=None, **kwargs):

        user = request.env.user

        _logger.warning(
            "TZ LOCATION UPDATE HIT: user=%s latitude=%s longitude=%s",
            user.name,
            latitude,
            longitude,
        )

        if not user or user._is_public():
            return {
                "success": False,
                "error": "User not authenticated",
            }

        if not user.tz_tracking_enabled:
            return {
                "success": False,
                "error": "Tracking is disabled for this user",
            }

        if latitude is None or longitude is None:
            return {
                "success": False,
                "error": "Latitude and longitude are required",
            }

        now = fields.Datetime.now()

        values = {
            "user_id": user.id,
            "latitude": latitude,
            "longitude": longitude,
            "accuracy": accuracy or 0,
            "battery_level": battery_level or 0,
        }

        latest_location = request.env["tz.user.location"].sudo().search([
            ("user_id", "=", user.id)
        ], limit=1)

        latest_values = values.copy()
        latest_values["last_seen"] = now

        if latest_location:
            latest_location.write(latest_values)
        else:
            request.env["tz.user.location"].sudo().create(latest_values)

        history_values = values.copy()
        history_values["tracked_at"] = now

        request.env["tz.user.location.history"].sudo().create(history_values)

        user.sudo().write({
            "tz_tracking_status": "active",
            "tz_last_latitude": latitude,
            "tz_last_longitude": longitude,
            "tz_last_accuracy": accuracy or 0,
            "tz_last_seen": now,
        })

        return {
            "success": True,
            "message": _("Location updated"),
        }

    @http.route(
        "/api/tz/location/stop",
        type="json",
        auth="user",
        csrf=False,
        methods=["POST"]
    )
    def stop_location(self, **kwargs):
        user = request.env.user

        if not user or user._is_public():
            return {
                "success": False,
                "error": "User not authenticated",
            }

        user.sudo().write({
            "tz_tracking_status": "stopped",
        })

        return {
            "success": True,
            "message": _("Tracking stopped"),
        }