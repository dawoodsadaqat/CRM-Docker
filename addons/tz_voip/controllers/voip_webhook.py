from datetime import datetime

from odoo import fields, http
from odoo.http import request


class TzVoipWebhookController(http.Controller):

    def _parse_datetime(self, value):
        if not value:
            return fields.Datetime.now()

        try:
            return datetime.fromisoformat(
                value.replace("Z", "+00:00")
            ).replace(tzinfo=None)
        except Exception:
            return fields.Datetime.now()

    @http.route(
        "/api/voip/call-event",
        type="json",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    def call_event(self, **kwargs):
        data = request.jsonrequest or {}

        api_key = data.get("api_key")

        provider = request.env["tz.voip.provider"].sudo().search([
            ("webhook_api_key", "=", api_key),
            ("active", "=", True),
        ], limit=1)

        if not provider:
            return {
                "success": False,
                "error": "Invalid API key",
            }

        event_type = data.get("event_type")

        external_call_id = (
            data.get("external_call_id")
            or data.get("unique_id")
        )

        linked_call_id = (
            data.get("linked_call_id")
            or data.get("linked_id")
        )

        phone_number = (
            data.get("phone_number")
            or data.get("destination_number")
        )

        source_extension = data.get("source_extension")
        destination_number = data.get("destination_number")
        recording_url = data.get("recording_url")

        CallLog = request.env["tz.call.log"].sudo()

        call_log = False

        if external_call_id:
            call_log = CallLog.search([
                ("external_call_id", "=", external_call_id)
            ], limit=1)

        if not call_log and linked_call_id:
            call_log = CallLog.search([
                ("linked_call_id", "=", linked_call_id)
            ], limit=1)

        if not call_log and phone_number:
            call_log = CallLog.search([
                ("phone_number", "ilike", phone_number[-7:])
            ], order="create_date desc", limit=1)

        vals = {
            "provider_id": provider.id,
            "external_call_id": external_call_id,
            "linked_call_id": linked_call_id,
            "phone_number": phone_number,
            "source_extension": source_extension,
            "destination_number": destination_number,
        }

        if event_type == "started":
            vals.update({
                "call_status": "not_called",
                "started_at": self._parse_datetime(
                    data.get("started_at")
                ),
            })

        elif event_type == "answered":
            vals.update({
                "call_status": "connected",
                "answered_at": self._parse_datetime(
                    data.get("answered_at")
                ),
            })

        elif event_type == "completed":
            ended_at = self._parse_datetime(
                data.get("ended_at")
            )

            answered_at = (
                call_log.answered_at
                if call_log and call_log.answered_at
                else False
            )

            duration_seconds = 0

            if answered_at and ended_at:
                duration_seconds = int(
                    (ended_at - answered_at).total_seconds()
                )

            vals.update({
                "call_status": "connected",
                "ended_at": ended_at,
                "duration_seconds": duration_seconds,
                "recording_url": recording_url,
            })

        elif event_type in ("missed", "failed"):
            vals.update({
                "call_status": (
                    "not_answered"
                    if event_type == "missed"
                    else "failed"
                ),
                "ended_at": self._parse_datetime(
                    data.get("ended_at")
                ),
            })

        elif event_type == "busy":
            vals.update({
                "call_status": "busy",
                "ended_at": self._parse_datetime(
                    data.get("ended_at")
                ),
            })

        if call_log:
            call_log.write(vals)
        else:
            call_log = CallLog.create(vals)

        return {
            "success": True,
            "call_log_id": call_log.id,
            "status": call_log.call_status,
            "duration_seconds": call_log.duration_seconds,
        }