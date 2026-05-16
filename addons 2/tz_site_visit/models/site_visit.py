from odoo import models, fields, api


class TzSiteVisit(models.Model):
    _name = "tz.site.visit"
    _description = "Site Visit"
    _order = "visit_datetime desc"

    name = fields.Char(
        string="Visit Reference",
        required=True,
        copy=False,
        default="New"
    )

    lead_id = fields.Many2one(
        "crm.lead",
        string="Lead / Opportunity",
        required=True,
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

    property_unit_id = fields.Many2one(
        "tz.property.unit",
        string="Property Unit",
        required=True
    )

    visit_datetime = fields.Datetime(
        string="Visit Date & Time",
        required=True
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
    ], string="Status", default="scheduled", required=True)

    feedback = fields.Text(string="Customer Feedback")
    next_action = fields.Text(string="Next Action")

    property_type = fields.Selection(
        related="property_unit_id.property_type",
        string="Property Type",
        store=True,
        readonly=True
    )

    area = fields.Char(
        related="property_unit_id.area",
        string="Area",
        store=True,
        readonly=True
    )

    sale_price = fields.Float(
        related="property_unit_id.sale_price",
        string="Sale Price",
        store=True,
        readonly=True
    )

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

        if "status" in vals:
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