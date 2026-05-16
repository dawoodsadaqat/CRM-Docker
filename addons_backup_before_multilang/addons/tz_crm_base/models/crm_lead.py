from odoo import models, fields


class CrmLead(models.Model):
    _inherit = "crm.lead"

    source_channel = fields.Selection([
        ("manual", "Manual"),
        ("website", "Website"),
        ("meta", "Meta"),
        ("whatsapp", "WhatsApp"),
    ], string="Source Channel", default="manual", tracking=True)