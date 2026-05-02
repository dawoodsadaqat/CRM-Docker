from odoo import models, fields, api


class CrmLead(models.Model):
    _inherit = "crm.lead"

    conversion_stage = fields.Selection([
        ("new", "New"),
        ("contacted", "Contacted"),
        ("site_visit", "Site Visit"),
        ("negotiation", "Negotiation"),
        ("won", "Won"),
        ("lost", "Lost"),
    ], string="Conversion Stage", default="new", tracking=True)

    conversion_stage_date = fields.Datetime(
        string="Last Conversion Update",
        default=fields.Datetime.now
    )

    deal_value = fields.Float(string="Deal Value")

    @api.onchange("conversion_stage")
    def _onchange_conversion_stage(self):
        for lead in self:
            lead.conversion_stage_date = fields.Datetime.now()