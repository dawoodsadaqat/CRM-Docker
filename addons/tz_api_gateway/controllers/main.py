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

    def _log_api(
        self,
        source_config,
        payload,
        response,
        status,
        http_status,
        lead=False,
        error=False,
    ):
        try:
            request.env["tz.api.log"].sudo().create({
                "name": "Lead Create API",
                "endpoint": "/api/tz/leads/create",
                "api_key_name": source_config.name if source_config else "Invalid",
                "request_payload": json.dumps(payload),
                "response_payload": json.dumps(response),
                "status": status,
                "http_status": http_status,
                "lead_id": lead.id if lead else False,
                "error_message": error or False,
            })
        except Exception as e:
            _logger.exception("Failed to create API log: %s", e)

    def _clean_phone(self, phone):
        if not phone:
            return False

        return (
            phone.replace(" ", "")
            .replace("-", "")
            .replace("(", "")
            .replace(")", "")
            .strip()
        )

    def _get_or_create_utm(self, model, name):
        if not name:
            return False

        name = str(name).strip()

        if not name:
            return False

        record = request.env[model].sudo().search([
            ("name", "=", name)
        ], limit=1)

        if not record:
            record = request.env[model].sudo().create({
                "name": name
            })

        return record

    # =====================================================
    # SOURCE CONFIG VALIDATION
    # =====================================================

    def _get_source_config(self, api_key, source_channel):
        if not api_key or not source_channel:
            return False

        return request.env["tz.lead.integration"].sudo().search([
            ("api_key", "=", api_key),
            ("integration_code", "=", source_channel),
            ("active", "=", True),
        ], limit=1)

    # =====================================================
    # ROUTING RULE MATCHING
    # =====================================================

    def _find_matching_routing_rule(
        self,
        source_config,
        payload,
        property_type,
        lead_temperature,
    ):
        lead_config = source_config.lead_config_id

        routing_rules = request.env[
            "tz.lead.routing.rule"
        ].sudo().search([
            ("company_id", "=", lead_config.company_id.id),
            ("active", "=", True),
        ], order="priority asc, id asc")

        incoming_budget_min = float(payload.get("budget_min") or 0)
        incoming_budget_max = float(payload.get("budget_max") or 0)

        for rule in routing_rules:

            # =============================================
            # SOURCE CHECK
            # =============================================

            if rule.allowed_source_ids:
                if source_config.id not in rule.allowed_source_ids.ids:
                    continue

            # =============================================
            # PROPERTY TYPE CHECK
            # =============================================

            if rule.property_type_ids:
                property_codes = rule.property_type_ids.mapped("code")

                if property_type not in property_codes:
                    continue

            # =============================================
            # LEAD TEMPERATURE CHECK
            # =============================================

            if rule.lead_temperature_ids:
                temperature_codes = rule.lead_temperature_ids.mapped("code")

                if lead_temperature not in temperature_codes:
                    continue

            # =============================================
            # LOCATION CHECK
            # =============================================

            if rule.preferred_location:
                incoming_location = (
                    payload.get("preferred_location") or ""
                ).strip().lower()

                rule_location = rule.preferred_location.strip().lower()

                if rule_location not in incoming_location:
                    continue

            # =============================================
            # BUDGET CHECK
            # =============================================

            if rule.budget_min:
                if incoming_budget_max < rule.budget_min:
                    continue

            if rule.budget_max:
                if incoming_budget_min > rule.budget_max:
                    continue

            return rule

        return False

    # =====================================================
    # ASSIGNMENT LOGIC
    # =====================================================

    def _get_assigned_user_id(self, source_config, matched_rule=False):
        lead_config = source_config.lead_config_id

        if matched_rule:

            if matched_rule.assign_agent_id:
                return matched_rule.assign_agent_id.id

            if matched_rule.assign_supervisor_id:
                return matched_rule.assign_supervisor_id.id

        if lead_config.default_agent_id:
            return lead_config.default_agent_id.id

        if lead_config.default_manager_id:
            return lead_config.default_manager_id.id

        return False

    # =====================================================
    # MAIN API
    # =====================================================

    @http.route(
        "/api/tz/leads/create",
        type="json",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    def create_lead(self, **kwargs):

        payload = request.jsonrequest or {}

        api_key = request.httprequest.headers.get("X-API-Key")

        source_channel = payload.get("source_channel")

        if not source_channel:
            response = {
                "success": False,
                "error": "source_channel is required"
            }
            return self._json(response, 400)

        config = self._get_source_config(api_key, source_channel)

        if not config:
            response = {
                "success": False,
                "error": "Invalid API Key or Source Channel",
                "source_channel": source_channel,
            }

            self._log_api(
                False,
                payload,
                response,
                "failed",
                401,
                error="Invalid API Key or Source Channel",
            )

            return self._json(response, 401)

        name = payload.get("name")

        if not name:
            response = {
                "success": False,
                "error": "name is required"
            }

            self._log_api(config, payload, response, "failed", 400)
            return self._json(response, 400)

        phone = self._clean_phone(payload.get("phone"))
        email = payload.get("email")

        property_type = payload.get("property_type")
        lead_temperature = payload.get("lead_temperature")

        valid_property_types = [
            "apartment",
            "villa",
            "townhouse",
            "office",
            "retail",
            "land",
        ]

        if property_type and property_type not in valid_property_types:
            response = {
                "success": False,
                "error": "Invalid property_type"
            }

            self._log_api(
                config,
                payload,
                response,
                "failed",
                400,
                error="Invalid property_type",
            )

            return self._json(response, 400)

        valid_temperatures = [
            "cold",
            "warm",
            "hot",
        ]

        if lead_temperature and lead_temperature not in valid_temperatures:
            response = {
                "success": False,
                "error": "Invalid lead_temperature"
            }

            self._log_api(
                config,
                payload,
                response,
                "failed",
                400,
                error="Invalid lead_temperature",
            )

            return self._json(response, 400)

        # =============================================
        # DUPLICATE CHECK
        # =============================================

        duplicate_domain = []

        if phone:
            duplicate_domain.append(("phone", "=", phone))

        if email:
            if duplicate_domain:
                duplicate_domain = [
                    "|"
                ] + duplicate_domain + [
                    ("email_from", "=", email)
                ]
            else:
                duplicate_domain.append(("email_from", "=", email))

        existing = False

        if duplicate_domain:
            existing = request.env["crm.lead"].sudo().search(
                duplicate_domain,
                limit=1,
            )

        if existing:
            response = {
                "success": False,
                "error": "Duplicate lead",
                "lead_id": existing.id,
            }

            self._log_api(
                config,
                payload,
                response,
                "failed",
                409,
                lead=existing,
                error="Duplicate lead",
            )

            return self._json(response, 409)

        # =============================================
        # ROUTING RULE MATCH
        # =============================================

        matched_rule = self._find_matching_routing_rule(
            config,
            payload,
            property_type,
            lead_temperature,
        )

        assigned_user_id = self._get_assigned_user_id(
            config,
            matched_rule,
        )

        # =============================================
        # UTM
        # =============================================

        utm_source = self._get_or_create_utm(
            "utm.source",
            payload.get("utm_source") or payload.get("source"),
        )

        utm_medium = self._get_or_create_utm(
            "utm.medium",
            payload.get("utm_medium") or payload.get("medium"),
        )

        utm_campaign = self._get_or_create_utm(
            "utm.campaign",
            payload.get("utm_campaign") or payload.get("campaign"),
        )

        # =============================================
        # LEAD CREATE
        # =============================================

        lead_vals = {
            "name": payload.get("lead_title") or f"API Lead - {name}",
            "contact_name": name,
            "phone": phone,
            "email_from": email,
            "type": "lead",
            "user_id": assigned_user_id,
            "source_channel": source_channel,
            "property_type": property_type,
            "preferred_location": payload.get("preferred_location"),
            "budget_min": float(payload.get("budget_min") or 0),
            "budget_max": float(payload.get("budget_max") or 0),
            "lead_temperature": lead_temperature,
            "source_id": utm_source.id if utm_source else False,
            "medium_id": utm_medium.id if utm_medium else False,
            "campaign_id": utm_campaign.id if utm_campaign else False,
            "description": payload.get("notes") or json.dumps(payload),
        }

        lead = request.env["crm.lead"].sudo().create(lead_vals)

        response = {
            "success": True,
            "lead_id": lead.id,
            "assigned_user_id": assigned_user_id,
            "routing_rule": matched_rule.name if matched_rule else False,
            "message": "Lead created successfully",
        }

        self._log_api(
            config,
            payload,
            response,
            "success",
            200,
            lead=lead,
        )

        return self._json(response, 200)