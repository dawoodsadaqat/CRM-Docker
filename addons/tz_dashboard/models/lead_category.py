from odoo import models, fields


class TzLeadCategory(models.Model):
    _name = "tz.lead.category"
    _description = "Lead Category"
    _order = "sequence, name"

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)