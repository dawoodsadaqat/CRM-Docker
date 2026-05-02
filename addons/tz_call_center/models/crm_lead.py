from odoo import models, fields


class CrmLead(models.Model):
    _inherit = "crm.lead"

    call_log_ids = fields.One2many(
        "tz.call.log",
        "lead_id",
        string="Call Logs"
    )

    call_log_count = fields.Integer(
        string="Call Log Count",
        compute="_compute_call_log_count"
    )

    def _compute_call_log_count(self):
        for lead in self:
            lead.call_log_count = len(lead.call_log_ids)

    def action_view_call_logs(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": "Call Logs",
            "res_model": "tz.call.log",
            "view_mode": "tree,form",
            "domain": [("lead_id", "=", self.id)],
            "context": {
                "default_lead_id": self.id,
                "default_customer_id": self.partner_id.id if self.partner_id else False,
                "default_agent_id": self.user_id.id if self.user_id else self.env.user.id,
                "default_phone_number": self.phone or self.mobile,
            },
        }