import json
import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)
_logger.warning("TZ API CONTROLLER LOADED")


class TzApiGateway(http.Controller):

    def _json(self, data, status=200):
        return request.make_response(
            json.dumps(data),
            headers=[("Content-Type", "application/json")],
            status=status
        )

    def _log_api(self, config, payload, response, status, http_status, lead=False, error=False):
        try:
            request.env["tz.api.log"].sudo().create({
                "name": "Lead Create API",
                "endpoint": "/api/tz/leads/create",
                "api_key_name": config.name if config else "Invalid",
                "request_payload": json.dumps(payload),
                "response_payload": json.dumps(response),
                "status": status,
                "http_status": http_status,
                "lead_id": lead.id if lead else False,
                "error_message": error or False,
            })
        except Exception as e:
            _logger.exception("Failed to create API log: %s", e)

    def _validate_key(self):
        key = request.httprequest.headers.get("X-API-Key")
        if not key:
            return False

        return request.env["tz.api.config"].sudo().search([
            ("api_key", "=", key),
            ("active", "=", True)
        ], limit=1)

    def _clean_phone(self, phone):
        if not phone:
            return False
        return phone.replace(" ", "").replace("-", "").strip()

    def _get_or_create_utm(self, model, name):
        if not name:
            return False

        name = str(name).strip()
        if not name:
            return False

        record = request.env[model].sudo().search([("name", "=", name)], limit=1)

        if not record:
            record = request.env[model].sudo().create({
                "name": name
            })

        return record

    @http.route("/api/tz/leads/create", type="http", auth="public", methods=["POST"], csrf=False)
    def create_lead(self, **kwargs):
        config = self._validate_key()
        raw_body = request.httprequest.data or b"{}"

        try:
            payload = json.loads(raw_body)
        except Exception:
            response = {"success": False, "error": "Invalid JSON"}
            self._log_api(config, {}, response, "failed", 400, error="Invalid JSON")
            return self._json(response, 400)

        if not config:
            response = {"success": False, "error": "Invalid API Key"}
            self._log_api(False, payload, response, "failed", 401, error="Invalid API Key")
            return self._json(response, 401)

        name = (payload.get("name") or "").strip()
        phone = self._clean_phone(payload.get("phone"))
        email = (payload.get("email") or "").strip().lower()

        if not name:
            response = {"success": False, "error": "Name required"}
            self._log_api(config, payload, response, "failed", 400, error="Name required")
            return self._json(response, 400)

        if not phone and not email:
            response = {"success": False, "error": "Phone or email required"}
            self._log_api(config, payload, response, "failed", 400, error="Phone or email required")
            return self._json(response, 400)

        valid_property_types = ["apartment", "villa", "townhouse", "office", "retail", "land"]
        property_type = payload.get("property_type")

        if property_type and property_type not in valid_property_types:
            response = {"success": False, "error": "Invalid property_type"}
            self._log_api(config, payload, response, "failed", 400, error="Invalid property_type")
            return self._json(response, 400)

        valid_temperatures = ["hot", "warm", "cold"]
        lead_temperature = payload.get("lead_temperature", "warm")

        if lead_temperature not in valid_temperatures:
            response = {"success": False, "error": "Invalid lead_temperature"}
            self._log_api(config, payload, response, "failed", 400, error="Invalid lead_temperature")
            return self._json(response, 400)

        # ✅ FIXED DUPLICATE CHECK
        duplicate_domain = []

        if phone:
            duplicate_domain.append(("phone", "=", phone))

        if email:
            if duplicate_domain:
                duplicate_domain = ["|"] + duplicate_domain + [("email_from", "=", email)]
            else:
                duplicate_domain.append(("email_from", "=", email))

        existing = False

        if duplicate_domain:
            existing = request.env["crm.lead"].sudo().search(duplicate_domain, limit=1)

        if existing:
            response = {
                "success": False,
                "error": "Duplicate lead",
                "lead_id": existing.id
            }
            self._log_api(config, payload, response, "failed", 409, lead=existing, error="Duplicate lead")
            return self._json(response, 409)

        # UTM
        utm_source = self._get_or_create_utm(
            "utm.source",
            payload.get("utm_source") or payload.get("source")
        )
        utm_medium = self._get_or_create_utm(
            "utm.medium",
            payload.get("utm_medium") or payload.get("medium")
        )
        utm_campaign = self._get_or_create_utm(
            "utm.campaign",
            payload.get("utm_campaign") or payload.get("campaign")
        )

        lead_vals = {
            "name": payload.get("lead_title") or f"API Lead - {name}",
            "contact_name": name,
            "phone": phone,
            "email_from": email,
            "type": "lead",
            "property_type": property_type,
            "preferred_location": payload.get("preferred_location"),
            "budget_min": float(payload.get("budget_min") or 0),
            "budget_max": float(payload.get("budget_max") or 0),
            "lead_temperature": lead_temperature,
            "source_id": utm_source.id if utm_source else False,
            "medium_id": utm_medium.id if utm_medium else False,
            "campaign_id": utm_campaign.id if utm_campaign else False,
            "description": payload.get("notes"),
        }

        lead = request.env["crm.lead"].sudo().create(lead_vals)

        response = {
            "success": True,
            "lead_id": lead.id,
            "message": "Lead created successfully"
        }

        self._log_api(config, payload, response, "success", 200, lead=lead)
        return self._json(response, 200)