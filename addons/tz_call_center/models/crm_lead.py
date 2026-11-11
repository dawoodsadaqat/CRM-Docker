from urllib.parse import quote

from odoo import _, fields, models
from odoo.exceptions import UserError


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

    def _get_clean_phone(self):
        self.ensure_one()

        phone = self.mobile or self.phone

        if not phone:
            raise UserError(_("No phone number is available on this lead."))

        return (
            phone.replace(" ", "")
            .replace("-", "")
            .replace("(", "")
            .replace(")", "")
        )

    def _get_whatsapp_phone(self, phone):
        return phone.replace("+", "")

    def _create_call_log(self, phone, notes):
        self.ensure_one()

        self.env["tz.call.log"].sudo().create({
            "lead_id": self.id,
            "customer_id": self.partner_id.id if self.partner_id else False,
            "agent_id": self.env.user.id,
            "phone_number": phone,
            "notes": notes,
        })

    def action_view_call_logs(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": _("Call Logs"),
            "res_model": "tz.call.log",
            "view_mode": "tree,form",
            "domain": [("lead_id", "=", self.id)],
            "context": {
                "default_lead_id": self.id,
                "default_customer_id": self.partner_id.id if self.partner_id else False,
                "default_agent_id": self.user_id.id if self.user_id else self.env.user.id,
                "default_phone_number": self.mobile or self.phone,
            },
        }

    def action_call_customer(self):
        self.ensure_one()

        phone = self._get_clean_phone()

        self._create_call_log(
            phone=phone,
            notes=_("Manual call initiated from CRM lead.")
        )

        return {
            "type": "ir.actions.client",
            "tag": "tz_call_center.dial_tel",
            "params": {
                "phone": phone,
            },
        }

    def action_sms_customer(self):
        self.ensure_one()

        phone = self._get_clean_phone()

        self._create_call_log(
            phone=phone,
            notes=_("SMS initiated from CRM lead.")
        )

        sms_body = _("Hello, this is regarding your property inquiry.")

        return {
            "type": "ir.actions.act_url",
            "url": "sms:%s?body=%s" % (phone, quote(sms_body)),
            "target": "new",
        }

    def action_whatsapp_chat(self):
        self.ensure_one()

        phone = self._get_clean_phone()
        whatsapp_phone = self._get_whatsapp_phone(phone)

        self._create_call_log(
            phone=phone,
            notes=_("WhatsApp chat initiated from CRM lead.")
        )

        return {
            "type": "ir.actions.act_url",
            "url": "https://wa.me/%s" % whatsapp_phone,
            "target": "new",
        }

    def action_whatsapp_call(self):
        self.ensure_one()

        phone = self._get_clean_phone()
        whatsapp_phone = self._get_whatsapp_phone(phone)

        self._create_call_log(
            phone=phone,
            notes=_("WhatsApp call attempt initiated from CRM lead.")
        )

        return {
            "type": "ir.actions.act_url",
            "url": "https://wa.me/%s" % whatsapp_phone,
            "target": "new",
        }