from odoo import _, fields, models


class CrmLead(models.Model):
    _inherit = "crm.lead"

    site_visit_ids = fields.One2many(
        "tz.site.visit",
        "lead_id",
        string="Site Visits",
    )

    site_visit_count = fields.Integer(
        string="Site Visits",
        compute="_compute_site_visit_count",
    )

    meeting_count = fields.Integer(
        string="Lead Meetings",
        compute="_compute_meeting_count",
    )

    def _compute_site_visit_count(self):
        for lead in self:
            lead.site_visit_count = len(lead.site_visit_ids)

    def _compute_meeting_count(self):
        CalendarEvent = self.env["calendar.event"]
        for lead in self:
            lead.meeting_count = CalendarEvent.search_count([
                ("lead_id", "=", lead.id)
            ])

    def action_view_site_visits(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Site Visits"),
            "res_model": "tz.site.visit",
            "view_mode": "tree,form,calendar",
            "domain": [("lead_id", "=", self.id)],
            "context": {
                "default_lead_id": self.id,
                "default_customer_id": self.partner_id.id if self.partner_id else False,
                "default_agent_id": self.user_id.id if self.user_id else self.env.user.id,
            },
        }

    def action_create_site_visit(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Create Site Visit"),
            "res_model": "tz.site.visit",
            "view_mode": "form",
            "target": "current",
            "context": {
                "default_lead_id": self.id,
                "default_customer_id": self.partner_id.id if self.partner_id else False,
                "default_agent_id": self.user_id.id if self.user_id else self.env.user.id,
            },
        }

    def action_view_meetings(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Lead Meetings"),
            "res_model": "calendar.event",
            "view_mode": "calendar,tree,form",
            "domain": [("lead_id", "=", self.id)],
            "context": {
                "default_lead_id": self.id,
                "default_partner_ids": [(6, 0, [self.partner_id.id])] if self.partner_id else False,
                "default_name": _("Meeting: %s") % self.name,
            },
        }

    def action_book_meeting(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Book Meeting"),
            "res_model": "calendar.event",
            "view_mode": "form",
            "target": "current",
            "context": {
                "default_lead_id": self.id,
                "default_partner_ids": [(6, 0, [self.partner_id.id])] if self.partner_id else False,
                "default_name": _("Meeting: %s") % self.name,
                "default_meeting_status": "scheduled",
                "default_meeting_type": "online",
            },
        }