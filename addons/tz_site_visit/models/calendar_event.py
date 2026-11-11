from odoo import _, api, fields, models
from odoo.exceptions import UserError


class CalendarEvent(models.Model):
    _inherit = "calendar.event"

    lead_id = fields.Many2one(
        "crm.lead",
        string="Lead / Opportunity",
        ondelete="set null",
        tracking=True,
    )

    site_visit_id = fields.Many2one(
        "tz.site.visit",
        string="Site Visit",
        ondelete="set null",
        tracking=True,
    )

    meeting_type = fields.Selection([
        ("online", "Online"),
        ("phone", "Phone Call"),
        ("in_person", "In Person"),
    ], string="Meeting Type", default="online", tracking=True)

    meeting_status = fields.Selection([
        ("scheduled", "Scheduled"),
        ("done", "Done"),
        ("no_show", "No Show"),
        ("cancelled", "Cancelled"),
        ("rescheduled", "Rescheduled"),
    ], string="Meeting Status", default="scheduled", tracking=True)

    in_person_location = fields.Char(
        string="Meeting Location",
        tracking=True,
    )

    meeting_latitude = fields.Float(
        string="Latitude",
        digits=(16, 7),
        tracking=True,
    )

    meeting_longitude = fields.Float(
        string="Longitude",
        digits=(16, 7),
        tracking=True,
    )

    meeting_location_captured_at = fields.Datetime(
        string="Location Captured At",
        readonly=True,
        tracking=True,
    )

    meeting_map_url = fields.Char(
        string="Map URL",
        compute="_compute_meeting_map_url",
        store=True,
    )

    meeting_outcome = fields.Text(
        string="Meeting Outcome",
        tracking=True,
    )

    @api.depends("meeting_latitude", "meeting_longitude")
    def _compute_meeting_map_url(self):
        for event in self:
            if event.meeting_latitude and event.meeting_longitude:
                event.meeting_map_url = "https://www.google.com/maps?q=%s,%s" % (
                    event.meeting_latitude,
                    event.meeting_longitude,
                )
            else:
                event.meeting_map_url = False

    def action_capture_current_location(self):
        self.ensure_one()

        if self.meeting_type != "in_person":
            raise UserError(_("Current location can only be captured for In Person meetings."))

        return {
            "type": "ir.actions.client",
            "tag": "tz_site_visit.capture_meeting_location",
            "params": {
                "event_id": self.id,
            },
        }

    def action_open_meeting_map(self):
        self.ensure_one()

        if not self.meeting_map_url:
            raise UserError(_("No meeting location is available."))

        return {
            "type": "ir.actions.act_url",
            "url": self.meeting_map_url,
            "target": "new",
        }

    def action_mark_meeting_done(self):
        for event in self:
            event.meeting_status = "done"
            if event.lead_id:
                event.lead_id.message_post(
                    body=_("Meeting marked as done: %s") % event.name
                )
        return True