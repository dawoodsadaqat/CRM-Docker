from odoo import models, fields


class CrmLead(models.Model):
    _inherit = "crm.lead"

    matching_unit_count = fields.Integer(
        string="Matching Units",
        compute="_compute_matching_unit_count"
    )

    def _get_matching_unit_domain(self):
        self.ensure_one()

        domain = [
            ("availability", "=", "available")
        ]

        if self.property_type:
            domain.append(("property_type", "=", self.property_type))

        if self.preferred_location:
            domain.append(("area", "ilike", self.preferred_location))

        if self.budget_min:
            domain.append(("sale_price", ">=", self.budget_min))

        if self.budget_max:
            domain.append(("sale_price", "<=", self.budget_max))

        return domain

    def _compute_matching_unit_count(self):
        for lead in self:
            if not lead.property_type and not lead.preferred_location and not lead.budget_min and not lead.budget_max:
                lead.matching_unit_count = 0
                continue

            lead.matching_unit_count = self.env["tz.property.unit"].search_count(
                lead._get_matching_unit_domain()
            )

    def action_view_matching_units(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": "Matching Units",
            "res_model": "tz.property.unit",
            "view_mode": "tree,form",
            "domain": self._get_matching_unit_domain(),
            "context": {
                "default_property_type": self.property_type,
            },
        }