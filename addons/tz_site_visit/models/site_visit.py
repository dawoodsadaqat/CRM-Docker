from odoo import _, api, fields, models


class TzSiteVisit(models.Model):
    _name = "tz.site.visit"
    _description = "Site Visit"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "visit_datetime desc"

    name = fields.Char(
        string="Visit Reference",
        required=True,
        copy=False,
        default="New",
        tracking=True,
    )

    lead_id = fields.Many2one(
        "crm.lead",
        string="Lead / Opportunity",
        required=True,
        ondelete="cascade",
        tracking=True,
    )

    customer_id = fields.Many2one(
        "res.partner",
        string="Customer",
        tracking=True,
    )

    agent_id = fields.Many2one(
        "res.users",
        string="Agent",
        default=lambda self: self.env.user,
        tracking=True,
    )

    property_unit_id = fields.Many2one(
        "tz.property.unit",
        string="Property Unit",
        required=True,
        tracking=True,
    )

    visit_datetime = fields.Datetime(
        string="Visit Date & Time",
        required=True,
        tracking=True,
    )

    status = fields.Selection([
        ("scheduled", "Scheduled"),
        ("confirmed", "Confirmed"),
        ("completed", "Completed"),
        ("interested", "Interested"),
        ("negotiation", "Negotiation"),
        ("closed", "Closed"),
        ("lost", "Lost"),
        ("cancelled", "Cancelled"),
    ], string="Status", default="scheduled", required=True, tracking=True)

    meeting_event_id = fields.Many2one(
        "calendar.event",
        string="Calendar Meeting",
        readonly=True,
        copy=False,
    )

    feedback = fields.Text(string="Customer Feedback")
    next_action = fields.Text(string="Next Action")

    property_type = fields.Selection(
        related="property_unit_id.property_type",
        string="Property Type",
        store=True,
        readonly=True,
    )

    area = fields.Char(
        related="property_unit_id.area",
        string="Area",
        store=True,
        readonly=True,
    )

    sale_price = fields.Float(
        related="property_unit_id.sale_price",
        string="Sale Price",
        store=True,
        readonly=True,
    )

    @api.onchange("lead_id")
    def _onchange_lead_id(self):
        for visit in self:
            if visit.lead_id:
                visit.customer_id = visit.lead_id.partner_id
                visit.agent_id = visit.lead_id.user_id or self.env.user

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("tz.site.visit") or "New"

            if vals.get("lead_id") and not vals.get("customer_id"):
                lead = self.env["crm.lead"].browse(vals["lead_id"])
                vals["customer_id"] = lead.partner_id.id if lead.partner_id else False

            if vals.get("lead_id") and not vals.get("agent_id"):
                lead = self.env["crm.lead"].browse(vals["lead_id"])
                vals["agent_id"] = lead.user_id.id if lead.user_id else self.env.user.id

        visits = super().create(vals_list)

        for visit in visits:
            visit._sync_lead_site_visit_status()

        return visits

    def write(self, vals):
        result = super().write(vals)

        if "status" in vals or "lead_id" in vals:
            for visit in self:
                visit._sync_lead_site_visit_status()

        return result

    def _sync_lead_site_visit_status(self):
        for visit in self:
            if not visit.lead_id:
                continue

            if visit.status in ["scheduled", "confirmed"]:
                visit.lead_id.site_visit_status = "scheduled"

            elif visit.status in ["completed", "interested", "negotiation", "closed"]:
                visit.lead_id.site_visit_status = "completed"

            elif visit.status in ["cancelled", "lost"]:
                visit.lead_id.site_visit_status = "cancelled"

    def action_create_calendar_meeting(self):
        self.ensure_one()

        partner_ids = []
        if self.customer_id:
            partner_ids.append(self.customer_id.id)

        event = self.env["calendar.event"].create({
            "name": _("Site Visit: %s") % (self.lead_id.name or self.name),
            "start": self.visit_datetime,
            "stop": self.visit_datetime,
            "partner_ids": [(6, 0, partner_ids)],
            "lead_id": self.lead_id.id,
            "site_visit_id": self.id,
            "meeting_type": "in_person",
            "meeting_status": "scheduled",
            "location": self.area or "",
            "description": self.next_action or "",
        })

        self.meeting_event_id = event.id

        return {
            "type": "ir.actions.act_window",
            "name": _("Calendar Meeting"),
            "res_model": "calendar.event",
            "res_id": event.id,
            "view_mode": "form",
            "target": "current",
        }

    def action_open_calendar_meeting(self):
        self.ensure_one()

        if not self.meeting_event_id:
            return self.action_create_calendar_meeting()

        return {
            "type": "ir.actions.act_window",
            "name": _("Calendar Meeting"),
            "res_model": "calendar.event",
            "res_id": self.meeting_event_id.id,
            "view_mode": "form",
            "target": "current",
        }