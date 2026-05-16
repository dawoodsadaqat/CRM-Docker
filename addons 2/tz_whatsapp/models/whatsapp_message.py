from odoo import models, fields, api


class TzWhatsappMessage(models.Model):
    _name = "tz.whatsapp.message"
    _description = "WhatsApp Message"
    _order = "message_datetime desc, id desc"

    name = fields.Char(
        string="Message Reference",
        required=True,
        copy=False,
        default="New"
    )

    lead_id = fields.Many2one(
        "crm.lead",
        string="Lead / Opportunity",
        ondelete="cascade"
    )

    customer_id = fields.Many2one(
        "res.partner",
        string="Customer"
    )

    agent_id = fields.Many2one(
        "res.users",
        string="Agent",
        default=lambda self: self.env.user
    )

    phone_number = fields.Char(string="Phone Number")

    direction = fields.Selection([
        ("outgoing", "Outgoing"),
        ("incoming", "Incoming"),
    ], string="Direction", default="outgoing", required=True)

    template_name = fields.Char(string="Template Name")

    message_body = fields.Text(string="Message Body", required=True)

    status = fields.Selection([
        ("draft", "Draft"),
        ("sent", "Sent"),
        ("delivered", "Delivered"),
        ("read", "Read"),
        ("failed", "Failed"),
    ], string="Status", default="draft", required=True)

    message_datetime = fields.Datetime(
        string="Message Date & Time",
        default=fields.Datetime.now
    )

    external_message_id = fields.Char(string="External Message ID")

    failure_reason = fields.Text(string="Failure Reason")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("tz.whatsapp.message") or "New"

            if vals.get("lead_id"):
                lead = self.env["crm.lead"].browse(vals["lead_id"])

                if not vals.get("customer_id") and lead.partner_id:
                    vals["customer_id"] = lead.partner_id.id

                if not vals.get("agent_id") and lead.user_id:
                    vals["agent_id"] = lead.user_id.id

                if not vals.get("phone_number"):
                    vals["phone_number"] = lead.phone or lead.mobile

        messages = super().create(vals_list)

        for message in messages:
            message._sync_lead_whatsapp_status()

        return messages

    def write(self, vals):
        result = super().write(vals)

        if "status" in vals:
            for message in self:
                message._sync_lead_whatsapp_status()

        return result

    def _sync_lead_whatsapp_status(self):
        for message in self:
            if not message.lead_id:
                continue

            if message.status == "sent":
                message.lead_id.whatsapp_status = "sent"

            elif message.status in ["delivered", "read"]:
                message.lead_id.whatsapp_status = "replied" if message.direction == "incoming" else "sent"

            elif message.status == "failed":
                message.lead_id.whatsapp_status = "failed"

            elif message.status == "draft":
                message.lead_id.whatsapp_status = "not_sent"