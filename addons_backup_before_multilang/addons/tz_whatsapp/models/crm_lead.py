from odoo import models, fields


class CrmLead(models.Model):
    _inherit = "crm.lead"

    whatsapp_message_ids = fields.One2many(
        "tz.whatsapp.message",
        "lead_id",
        string="WhatsApp Messages"
    )

    whatsapp_message_count = fields.Integer(
        string="WhatsApp Message Count",
        compute="_compute_whatsapp_message_count"
    )

    def _compute_whatsapp_message_count(self):
        for lead in self:
            lead.whatsapp_message_count = len(lead.whatsapp_message_ids)

    def action_view_whatsapp_messages(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": "WhatsApp Messages",
            "res_model": "tz.whatsapp.message",
            "view_mode": "tree,form",
            "domain": [("lead_id", "=", self.id)],
            "context": {
                "default_lead_id": self.id,
                "default_customer_id": self.partner_id.id if self.partner_id else False,
                "default_agent_id": self.user_id.id if self.user_id else self.env.user.id,
                "default_phone_number": self.phone or self.mobile,
            },
        }