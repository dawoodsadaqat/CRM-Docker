from odoo import models, fields


class TzApiLog(models.Model):
    _name = "tz.api.log"
    _description = "API Request Log"
    _order = "create_date desc"

    name = fields.Char(string="Reference")
    endpoint = fields.Char(string="Endpoint")
    api_key_name = fields.Char(string="API Key Name")
    request_payload = fields.Text(string="Request Payload")
    response_payload = fields.Text(string="Response Payload")

    status = fields.Selection([
        ("success", "Success"),
        ("failed", "Failed"),
    ], string="Status")

    http_status = fields.Integer(string="HTTP Status")
    lead_id = fields.Many2one("crm.lead", string="Created Lead")
    error_message = fields.Text(string="Error Message")