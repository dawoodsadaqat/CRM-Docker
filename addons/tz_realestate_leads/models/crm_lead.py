from odoo import models, fields


class CrmLead(models.Model):
    _inherit = "crm.lead"

    property_type = fields.Selection([
        ("apartment", "Apartment"),
        ("villa", "Villa"),
        ("townhouse", "Townhouse"),
        ("office", "Office"),
        ("retail", "Retail"),
        ("land", "Land"),
    ], string="Property Type")

    preferred_location = fields.Char(string="Preferred Location")
    budget_min = fields.Float(string="Budget Min")
    budget_max = fields.Float(string="Budget Max")

    buying_purpose = fields.Selection([
        ("investment", "Investment"),
        ("end_use", "End Use"),
        ("rental", "Rental"),
        ("resale", "Resale"),
    ], string="Buying Purpose")

    lead_temperature = fields.Selection([
        ("hot", "Hot"),
        ("warm", "Warm"),
        ("cold", "Cold"),
    ], string="Lead Temperature", default="warm")

    lead_score = fields.Integer(string="Lead Score", default=0)

    whatsapp_status = fields.Selection([
        ("not_sent", "Not Sent"),
        ("sent", "Sent"),
        ("replied", "Replied"),
        ("failed", "Failed"),
    ], string="WhatsApp Status", default="not_sent")

    call_status = fields.Selection([
        ("not_called", "Not Called"),
        ("connected", "Connected"),
        ("not_answered", "Not Answered"),
        ("wrong_number", "Wrong Number"),
    ], string="Call Status", default="not_called")

    site_visit_status = fields.Selection([
        ("not_scheduled", "Not Scheduled"),
        ("scheduled", "Scheduled"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ], string="Site Visit Status", default="not_scheduled")

    next_followup_date = fields.Datetime(string="Next Follow-up Date")
    lost_reason_detail = fields.Text(string="Lost Reason Detail")