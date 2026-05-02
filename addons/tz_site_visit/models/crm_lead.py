from odoo import models, fields


class CrmLead(models.Model):
    _inherit = "crm.lead"

    site_visit_ids = fields.One2many(
        "tz.site.visit",
        "lead_id",
        string="Site Visits"
    )

    site_visit_count = fields.Integer(
        string="Site Visit Count",
        compute="_compute_site_visit_count"
    )

    def _compute_site_visit_count(self):
        for lead in self:
            lead.site_visit_count = len(lead.site_visit_ids)

    def action_view_site_visits(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": "Site Visits",
            "res_model": "tz.site.visit",
            "view_mode": "tree,form",
            "domain": [("lead_id", "=", self.id)],
            "context": {
                "default_lead_id": self.id,
                "default_customer_id": self.partner_id.id if self.partner_id else False,
                "default_agent_id": self.user_id.id if self.user_id else self.env.user.id,
            },
        }