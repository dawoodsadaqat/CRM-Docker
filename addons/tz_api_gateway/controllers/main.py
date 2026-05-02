from odoo import http
from odoo.http import request
import json


class TzApiGateway(http.Controller):

    def _json(self, data, status=200):
        return request.make_response(
            json.dumps(data),
            headers=[('Content-Type', 'application/json')],
            status=status
        )

    def _validate_key(self):
        key = request.httprequest.headers.get("X-API-Key")
        if not key:
            return False

        return request.env['tz.api.config'].sudo().search([
            ('api_key', '=', key),
            ('active', '=', True)
        ], limit=1)

    @http.route('/api/tz/leads/create', type='http', auth='public', methods=['POST'], csrf=False)
    def create_lead(self, **kwargs):

        config = self._validate_key()
        if not config:
            return self._json({"success": False, "error": "Invalid API Key"}, 401)

        try:
            payload = json.loads(request.httprequest.data or "{}")
        except:
            return self._json({"success": False, "error": "Invalid JSON"}, 400)

        name = payload.get("name")
        phone = payload.get("phone")

        if not name:
            return self._json({"success": False, "error": "Name required"}, 400)

        # 🔥 DUPLICATE CHECK (you didn’t have this — big mistake)
        existing = request.env['crm.lead'].sudo().search([
            ('phone', '=', phone)
        ], limit=1)

        if existing:
            return self._json({
                "success": False,
                "error": "Duplicate lead",
                "lead_id": existing.id
            }, 409)

        lead = request.env['crm.lead'].sudo().create({
            'name': f"API Lead - {name}",
            'contact_name': name,
            'phone': phone,
            'email_from': payload.get("email"),
            'property_type': payload.get("property_type"),
            'preferred_location': payload.get("preferred_location"),
            'budget_min': float(payload.get("budget_min") or 0),
            'budget_max': float(payload.get("budget_max") or 0),
            'lead_temperature': payload.get("lead_temperature", "warm"),
        })

        return self._json({
            "success": True,
            "lead_id": lead.id
        })