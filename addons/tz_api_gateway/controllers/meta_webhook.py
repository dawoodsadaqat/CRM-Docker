import json
import logging
import requests

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class MetaWebhookController(http.Controller):

    @http.route(
        "/api/meta/webhook",
        type="http",
        auth="public",
        methods=["GET"],
        csrf=False
    )
    def verify_meta_webhook(self, **kwargs):
        verify_token = request.env["ir.config_parameter"].sudo().get_param(
            "tz_api_gateway.meta_verify_token",
            default="techzilla_meta_verify"
        )

        mode = kwargs.get("hub.mode")
        token = kwargs.get("hub.verify_token")
        challenge = kwargs.get("hub.challenge")

        if mode == "subscribe" and token == verify_token:
            return request.make_response(challenge or "")

        return request.make_response("Verification failed", status=403)

    def _extract_leadgen_ids(self, payload):
        leadgen_ids = []

        for entry in payload.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                leadgen_id = value.get("leadgen_id")

                if leadgen_id:
                    leadgen_ids.append(leadgen_id)

        return leadgen_ids

    def _fetch_meta_lead(self, leadgen_id):
        access_token = request.env["ir.config_parameter"].sudo().get_param(
            "tz_api_gateway.meta_page_access_token"
        )

        if not access_token:
            raise Exception("Meta Page Access Token is not configured.")

        url = f"https://graph.facebook.com/v19.0/{leadgen_id}"

        params = {
            "access_token": access_token,
            "fields": "id,created_time,field_data,ad_id,form_id,campaign_id"
        }

        response = requests.get(url, params=params, timeout=20)

        if response.status_code != 200:
            raise Exception(f"Meta API error: {response.text}")

        return response.json()

    def _field_data_to_dict(self, field_data):
        result = {}

        for item in field_data or []:
            key = item.get("name")
            values = item.get("values") or []

            if key and values:
                result[key] = values[0]

        return result

    def _create_or_update_meta_lead(self, leadgen_id, meta_data, raw_payload):
        fields_map = self._field_data_to_dict(meta_data.get("field_data"))

        name = (
            fields_map.get("full_name")
            or fields_map.get("name")
            or fields_map.get("first_name")
            or f"Meta Lead {leadgen_id}"
        )

        phone = (
            fields_map.get("phone_number")
            or fields_map.get("phone")
            or fields_map.get("mobile")
        )

        email = fields_map.get("email")

        duplicate_domain = []

        if phone:
            duplicate_domain.append(("phone", "=", phone))

        if email:
            if duplicate_domain:
                duplicate_domain = ["|"] + duplicate_domain + [("email_from", "=", email)]
            else:
                duplicate_domain.append(("email_from", "=", email))

        Lead = request.env["crm.lead"].sudo()
        existing = Lead.search(duplicate_domain, limit=1) if duplicate_domain else False

        if existing:
            existing.message_post(
                body=f"Duplicate Meta lead received. Leadgen ID: {leadgen_id}"
            )
            return existing, False

        lead = Lead.create({
            "name": f"Meta Lead - {name}",
            "contact_name": name,
            "phone": phone,
            "email_from": email,
            "type": "lead",
            "source_channel": "meta",
            "description": json.dumps({
                "leadgen_id": leadgen_id,
                "meta_data": meta_data,
                "webhook_payload": raw_payload,
            }),
        })

        return lead, True

    @http.route(
        "/api/meta/webhook",
        type="json",
        auth="public",
        methods=["POST"],
        csrf=False
    )
    def receive_meta_webhook(self, **payload):
        _logger.warning("META WEBHOOK RECEIVED: %s", payload)

        results = []

        try:
            leadgen_ids = self._extract_leadgen_ids(payload)

            for leadgen_id in leadgen_ids:
                meta_data = self._fetch_meta_lead(leadgen_id)
                lead, created = self._create_or_update_meta_lead(
                    leadgen_id,
                    meta_data,
                    payload
                )

                results.append({
                    "leadgen_id": leadgen_id,
                    "lead_id": lead.id,
                    "lead_name": lead.name,
                    "created": created,
                })

            return {
                "success": True,
                "results": results
            }

        except Exception as e:
            _logger.exception("Meta Webhook Error")
            return {
                "success": False,
                "error": str(e)
            }