from odoo import models, fields, api


class TzCallLog(models.Model):
    _name = "tz.call.log"
    _description = "Call Log"
    _order = "call_datetime desc, id desc"

    name = fields.Char(
        string="Call Reference",
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

    call_direction = fields.Selection([
        ("outgoing", "Outgoing"),
        ("incoming", "Incoming"),
    ], string="Call Direction", default="outgoing", required=True)

    call_status = fields.Selection([
        ("not_called", "Not Called"),
        ("connected", "Connected"),
        ("not_answered", "Not Answered"),
        ("busy", "Busy"),
        ("wrong_number", "Wrong Number"),
        ("failed", "Failed"),
    ], string="Call Status", default="not_called", required=True)

    disposition = fields.Selection([
        ("interested", "Interested"),
        ("not_interested", "Not Interested"),
        ("call_back", "Call Back"),
        ("site_visit", "Site Visit"),
        ("negotiation", "Negotiation"),
        ("closed", "Closed"),
        ("lost", "Lost"),
    ], string="Disposition")

    call_datetime = fields.Datetime(
        string="Call Date & Time",
        default=fields.Datetime.now
    )

    duration_seconds = fields.Integer(string="Duration Seconds")

    recording_url = fields.Char(string="Recording URL")

    notes = fields.Text(string="Notes")

    next_followup_date = fields.Datetime(string="Next Follow-up Date")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("tz.call.log") or "New"

            if vals.get("lead_id"):
                lead = self.env["crm.lead"].browse(vals["lead_id"])

                if not vals.get("customer_id") and lead.partner_id:
                    vals["customer_id"] = lead.partner_id.id

                if not vals.get("agent_id") and lead.user_id:
                    vals["agent_id"] = lead.user_id.id

                if not vals.get("phone_number"):
                    vals["phone_number"] = lead.phone or lead.mobile

        calls = super().create(vals_list)

        for call in calls:
            call._sync_lead_call_status()

        return calls

    def write(self, vals):
        result = super().write(vals)

        sync_fields = {"call_status", "next_followup_date", "disposition"}

        if sync_fields.intersection(vals.keys()):
            for call in self:
                call._sync_lead_call_status()

        return result

    def _sync_lead_call_status(self):
        for call in self:
            if not call.lead_id:
                continue

            if call.call_status:
                call.lead_id.call_status = call.call_status

            if call.next_followup_date:
                call.lead_id.next_followup_date = call.next_followup_date